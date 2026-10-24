// overhang-bench â€” interactive viewer (Polyscope).
//
//   viewer MESH[@prerotation] [--size-mm 60] [--overhang-deg 45]
//          [--poses results/all_poses.csv]        (every method, incl. external)
//          [--orientations results/orientations.csv] (optimizers only)
//          [--prusaslicer results/prusaslicer.csv]
//          [--screenshots DIR]     (headless: write PNGs and exit)
//          [--figure] [--color R,G,B]  (with --screenshots: the part only, in one
//                                       colour, on a transparent background)
//          [--support-paths DIR]   (with --figure: also draw the slicer's support
//                                   toolpaths DIR/MESH__POSE.csv, written by
//                                   scripts/support_paths.py)
//          [--view-yaw DEG]        (with --figure: orbit the camera about z)
//          [--compare]             (all poses side by side; with --screenshots
//                                   writes a single MESH__compare.png)
//
// Shows, for the initial pose and the best pose of each objective:
//   * the part on the build plate, faces coloured by "needs support"
//   * the vertical support columns of the proxy model (simulate.hpp)
//   * a layer slider (slice plane at the current layer height)
//   * each objective as a function on S^2, drawn on the sphere d(t1,t2) and on
//     the (t1,t2) rectangle, with the optimum of every method marked
//   * proxy estimates and, if given, PrusaSlicer's estimates for the pose
//   * a "side by side" mode with every pose on the plate, left to right in the
//     order of the pose list, and a table of the estimates of all poses
#include "ob/mesh.hpp"
#include "ob/objectives.hpp"
#include "ob/optimize.hpp"
#include "ob/simulate.hpp"

#include "polyscope/polyscope.h"
#include "polyscope/surface_mesh.h"
#include "polyscope/curve_network.h"
#include "polyscope/point_cloud.h"
#include "polyscope/view.h"
#include "imgui.h"

#include <ctime>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>

using namespace ob;

namespace {

struct Pose { std::string name; double t1 = 0, t2 = 0; };

struct SlicerRow { double time_min = NAN, filament_mm = NAN, filament_g = NAN, support_mm = NAN; };

std::vector<std::string> csv_split(const std::string& l) {
  std::vector<std::string> v; std::stringstream ss(l); std::string t;
  while (std::getline(ss, t, ',')) v.push_back(t);
  return v;
}

// best (lowest f) row per objective for this mesh in orientations.csv; for
// castro-eq only the two multistarts of the paper count (as in pipeline.py)
std::vector<Pose> read_orientations(const std::string& path, const std::string& mesh) {
  std::ifstream in(path); std::string line; std::getline(in, line);
  const auto h = csv_split(line);
  auto col = [&](const std::string& k) { return int(std::find(h.begin(), h.end(), k) - h.begin()); };
  const int cm = col("mesh"), co = col("objective"), c1 = col("t1"), c2 = col("t2"), cf = col("fval"),
            cs = col("search");
  std::map<std::string, std::pair<double, Pose>> best;
  while (std::getline(in, line)) {
    const auto v = csv_split(line);
    if (int(v.size()) <= cf || v[cm] != mesh) continue;
    if (v[co] == "castro-eq" && v[cs] != "mcd" && v[cs] != "rcsp") continue;
    const double f = std::stod(v[cf]);
    if (!best.count(v[co]) || f < best[v[co]].first)
      best[v[co]] = {f, Pose{v[co], std::stod(v[c1]), std::stod(v[c2])}};
  }
  std::vector<Pose> out;
  for (auto& [k, p] : best) out.push_back(p.second);
  return out;
}

std::map<std::string, SlicerRow> read_slicer(const std::string& path, const std::string& mesh) {
  std::map<std::string, SlicerRow> out;
  std::ifstream in(path); std::string line;
  if (!std::getline(in, line)) return out;
  const auto h = csv_split(line);
  auto col = [&](const std::string& k) { return int(std::find(h.begin(), h.end(), k) - h.begin()); };
  while (std::getline(in, line)) {
    const auto v = csv_split(line);
    if (v.size() < h.size() || v[col("mesh")] != mesh || v[col("status")] != "ok") continue;
    SlicerRow r;
    r.time_min = std::stod(v[col("time_min")]);
    r.filament_mm = std::stod(v[col("filament_mm")]);
    r.filament_g = std::stod(v[col("filament_g")]);
    r.support_mm = std::stod(v[col("support_filament_mm")]);
    out[v[col("pose")]] = r;
  }
  return out;
}

// toolpath segments x0,y0,z0,x1,y1,z1 (scripts/support_paths.py) as a curve network
bool read_segments(const std::string& path, MatrixXd& N, MatrixXi& E) {
  std::ifstream in(path); std::string line;
  if (!std::getline(in, line)) return false;
  std::vector<double> v;
  while (std::getline(in, line)) {
    const auto c = csv_split(line);
    if (c.size() < 6) continue;
    for (int k = 0; k < 6; ++k) v.push_back(std::stod(c[k]));
  }
  const int n = int(v.size() / 6);
  N.resize(2 * n, 3); E.resize(n, 2);
  for (int i = 0; i < n; ++i) {
    N.row(2 * i) << v[6 * i], v[6 * i + 1], v[6 * i + 2];
    N.row(2 * i + 1) << v[6 * i + 3], v[6 * i + 4], v[6 * i + 5];
    E.row(i) << 2 * i, 2 * i + 1;
  }
  return n > 0;
}

// (t1,t2) grid, as a sphere through d(t1,t2) and as a flat rectangle
struct Landscape { MatrixXd S, P; MatrixXi F; int n1, n2; };
Landscape make_landscape(int n1, int n2, const Vector3d& c_sphere, double r,
                         const Vector3d& c_plane, double w) {
  Landscape L; L.n1 = n1; L.n2 = n2;
  L.S.resize(n1 * n2, 3); L.P.resize(n1 * n2, 3);
  for (int i = 0; i < n1; ++i)
    for (int j = 0; j < n2; ++j) {
      const double t1 = -kPi + 2 * kPi * i / (n1 - 1), t2 = -kPi / 2 + kPi * j / (n2 - 1);
      L.S.row(i * n2 + j) = c_sphere + r * direction(t1, t2);
      L.P.row(i * n2 + j) = c_plane + Vector3d(w * t1 / (2 * kPi), 0.0, w * t2 / (2 * kPi));
    }
  L.F.resize(2 * (n1 - 1) * (n2 - 1), 3);
  int k = 0;
  for (int i = 0; i + 1 < n1; ++i)
    for (int j = 0; j + 1 < n2; ++j) {
      const int a = i * n2 + j, b = (i + 1) * n2 + j, c = (i + 1) * n2 + j + 1, d = i * n2 + j + 1;
      L.F.row(k++) << a, b, c; L.F.row(k++) << a, c, d;
    }
  return L;
}

}  // namespace

int main(int argc, char** argv) {
  std::string mesh_arg, orient_csv, slicer_csv, shots, backend, poses_csv, support_dir;
  double size_mm = 60, overhang = 45, yaw_deg = 0;
  bool figure = false, compare = false;
  glm::vec3 color(0.45f, 0.80f, 0.68f);
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() { return std::string(argv[++i]); };
    if (a == "--size-mm") size_mm = std::stod(next());
    else if (a == "--overhang-deg") overhang = std::stod(next());
    else if (a == "--orientations") orient_csv = next();
    else if (a == "--poses") poses_csv = next();
    else if (a == "--prusaslicer") slicer_csv = next();
    else if (a == "--screenshots") shots = next();
    else if (a == "--backend") backend = next();
    else if (a == "--figure") figure = true;
    else if (a == "--compare") compare = true;
    else if (a == "--support-paths") support_dir = next();
    else if (a == "--view-yaw") yaw_deg = std::stod(next());
    else if (a == "--color") { const auto c = csv_split(next()); color = {std::stof(c[0]), std::stof(c[1]), std::stof(c[2])}; }
    else mesh_arg = a;
  }
  if (mesh_arg.empty()) {
    std::cerr << "usage: viewer MESH[@rx90,...] [--size-mm S] [--overhang-deg A] "
                 "[--poses all_poses.csv | --orientations CSV] [--prusaslicer CSV] [--screenshots DIR]\n"
                 "              [--figure] [--color R,G,B] [--support-paths DIR] [--view-yaw DEG] [--compare]\n";
    return 1;
  }
  const auto at = mesh_arg.find('@');
  Mesh M = at == std::string::npos ? load_mesh(mesh_arg)
                                   : load_mesh(mesh_arg.substr(0, at), false, mesh_arg.substr(at + 1));
  const double maxdim = (M.V.colwise().maxCoeff() - M.V.colwise().minCoeff()).maxCoeff();
  const double scale = size_mm / maxdim;

  AlexanderParams ap; ap.overhang_deg = overhang; ap.length_scale = scale / 10.0;
  std::vector<std::unique_ptr<Objective>> objs;
  for (const char* n : {"castro-eq", "alexander"}) objs.push_back(make_objective(n, M, ap));
  // Ezair's V(S) at 256^2 pixels for the landscape only (the benchmark uses 1024^2)
  objs.push_back(std::make_unique<EzairSupportVolume>(M, 256));

  std::vector<Pose> poses{{"initial", 0, 0}};
  if (!poses_csv.empty()) {  // mesh,pose,t1,t2 (e.g. results/all_poses.csv: every method)
    std::ifstream in(poses_csv); std::string line; std::getline(in, line);
    while (std::getline(in, line)) {
      const auto v = csv_split(line);
      if (v.size() >= 4 && v[0] == M.name && v[1] != "initial")
        poses.push_back({v[1], std::stod(v[2]), std::stod(v[3])});
    }
  } else if (!orient_csv.empty()) {
    for (auto& p : read_orientations(orient_csv, M.name)) poses.push_back(p);
  } else {
    std::cerr << "no --poses/--orientations given: optimizing on S^2 (Fibonacci 20000 + local)...\n";
    for (size_t k = 0; k < 2; ++k) {
      auto& o = objs[k];
      const Result r = sphere_search(*o, 20000);
      poses.push_back({o->name(), r.t1, r.t2});
    }
  }
  const auto slicer = slicer_csv.empty() ? std::map<std::string, SlicerRow>{}
                                         : read_slicer(slicer_csv, M.name);

  polyscope::options::programName = "overhang-bench â€” " + M.name;
  polyscope::options::groundPlaneMode = polyscope::GroundPlaneMode::ShadowOnly;
  polyscope::view::setUpDir(polyscope::UpDir::ZUp);
  polyscope::view::setFrontDir(polyscope::FrontDir::NegYFront);
  if (figure && !shots.empty()) {  // print-resolution renders, antialiased thin toolpaths
    polyscope::options::usePrefsFile = false;  // else the saved window size wins
    polyscope::view::windowWidth = 3000; polyscope::view::windowHeight = 1150;
    polyscope::options::ssaaFactor = 2;
  }
  polyscope::init(backend);  // "" = auto; "openGL3_egl" for headless GPUs

  // --- landscapes (one per objective, only the selected one is shown)
  const Landscape L = make_landscape(181, 91, Vector3d(-1.5 * size_mm, 0, 0.45 * size_mm),
                                     0.35 * size_mm, Vector3d(0, 1.6 * size_mm, 0.45 * size_mm),
                                     1.4 * size_mm);
  std::vector<VectorXd> land(objs.size());
  auto compute_landscape = [&](size_t k) {  // on demand: Ezair's takes a few seconds
    if (land[k].size()) return;
    land[k].resize(L.S.rows());
#pragma omp parallel for
    for (int i = 0; i < L.n1; ++i)
      for (int j = 0; j < L.n2; ++j)
        land[k](i * L.n2 + j) = objs[k]->eval_angles(-kPi + 2 * kPi * i / (L.n1 - 1),
                                                     -kPi / 2 + kPi * j / (L.n2 - 1));
  };
  polyscope::SurfaceMesh *sph = nullptr, *pln = nullptr;
  if (!figure) {
    sph = polyscope::registerSurfaceMesh("f on S^2", L.S, L.F);
    pln = polyscope::registerSurfaceMesh("f on (t1,t2)", L.P, L.F);
    sph->setEdgeWidth(0); pln->setEdgeWidth(0);
  }
  // optima markers
  MatrixXd mk_s(poses.size(), 3), mk_p(poses.size(), 3);
  for (size_t k = 0; k < poses.size(); ++k) {
    mk_s.row(k) = Vector3d(-1.5 * size_mm, 0, 0.45 * size_mm) +
                  0.37 * size_mm * direction(poses[k].t1, poses[k].t2);
    mk_p.row(k) = Vector3d(0, 1.6 * size_mm, 0.45 * size_mm) +
                  Vector3d(1.4 * size_mm * poses[k].t1 / (2 * kPi), -0.5, 1.4 * size_mm * poses[k].t2 / (2 * kPi));
  }
  if (!figure) {
    auto* pts_s = polyscope::registerPointCloud("optima (S^2)", mk_s);
    auto* pts_p = polyscope::registerPointCloud("optima (t1,t2)", mk_p);
    pts_s->setPointRadius(0.012); pts_p->setPointRadius(0.012);
  }

  int cur_obj = 0, cur_pose = 1 % int(poses.size());
  auto show_landscape = [&]() {
    if (figure) return;
    compute_landscape(cur_obj);
    sph->addVertexScalarQuantity("f", land[cur_obj])->setColorMap("viridis")->setEnabled(true);
    pln->addVertexScalarQuantity("f", land[cur_obj])->setColorMap("viridis")->setEnabled(true);
  };
  show_landscape();

  // --- part on the plate
  PrintEstimate est;
  PrintParams pp; pp.overhang_deg = overhang;
  polyscope::SlicePlane* plane = polyscope::addSceneSlicePlane();
  plane->setActive(false);
  float layer = 1.0f;  // fraction of the height
  bool slicing = false;

  auto show_pose = [&]() {
    const Pose& P = poses[cur_pose];
    const MatrixXd W = place_on_plate(M, P.t1, P.t2, scale);
    std::vector<Eigen::RowVector3d> cols;
    est = estimate_print(W, M.F, pp, &cols);
    auto* pm = polyscope::registerSurfaceMesh("part", W, M.F);
    VectorXd flag(M.F.rows());
    const double thr = -std::sin(overhang * kPi / 180.0);
    for (int f = 0; f < M.F.rows(); ++f) {
      const Vector3d a = W.row(M.F(f, 0)), b = W.row(M.F(f, 1)), c = W.row(M.F(f, 2));
      const Vector3d n = (b - a).cross(c - a).normalized();
      flag(f) = n.z() < thr ? 1.0 : 0.0;
    }
    if (figure) {
      pm->setSurfaceColor(color); pm->setSmoothShade(true);
      if (polyscope::hasCurveNetwork("slicer supports")) polyscope::removeCurveNetwork("slicer supports");
      MatrixXd SN; MatrixXi SE;
      if (!support_dir.empty() && read_segments(support_dir + "/" + M.name + "__" + P.name + ".csv", SN, SE)) {
        auto* cn = polyscope::registerCurveNetwork("slicer supports", SN, SE);
        cn->setRadius(0.2, false);  // half the 0.4 mm extrusion width
        cn->setColor({0.80f, 0.78f, 0.74f});
      }
      return;
    }
    pm->addFaceScalarQuantity("needs support", flag)->setColorMap("reds")->setEnabled(true);
    MatrixXd N(cols.size(), 3); MatrixXi E(cols.size() / 2, 2);
    for (size_t k = 0; k < cols.size(); ++k) N.row(k) = cols[k];
    for (size_t k = 0; k < cols.size() / 2; ++k) E.row(k) << int(2 * k), int(2 * k + 1);
    if (polyscope::hasCurveNetwork("support columns")) polyscope::removeCurveNetwork("support columns");
    if (E.rows() > 0) {
      auto* cn = polyscope::registerCurveNetwork("support columns", N, E);
      cn->setRadius(0.0015); cn->setColor({0.35f, 0.75f, 0.45f});
    }
  };
  show_pose();

  // --- side by side: every pose on the plate, left to right in list order
  std::vector<PrintEstimate> all_est(poses.size());
  std::vector<MatrixXd> placed(poses.size());
  double spacing = 0;
  for (size_t k = 0; k < poses.size(); ++k) {
    placed[k] = place_on_plate(M, poses[k].t1, poses[k].t2, scale);
    spacing = std::max(spacing, placed[k].col(0).maxCoeff() - placed[k].col(0).minCoeff());
  }
  spacing *= 1.25;
  auto cmp_name = [&](size_t k) { return std::to_string(k) + " " + poses[k].name; };
  auto cmp_sup = [&](size_t k) { return cmp_name(k) + " (support columns)"; };
  auto show_compare = [&](bool on) {
    for (size_t k = 0; k < poses.size(); ++k) {
      if (polyscope::hasCurveNetwork(cmp_sup(k))) polyscope::removeCurveNetwork(cmp_sup(k));
      if (!on) {
        if (polyscope::hasSurfaceMesh(cmp_name(k))) polyscope::removeSurfaceMesh(cmp_name(k));
        continue;
      }
      std::vector<Eigen::RowVector3d> cols;  // proxy support columns, as in show_pose
      all_est[k] = estimate_print(placed[k], M.F, pp, &cols);
      MatrixXd W = placed[k];
      W.col(0).array() += spacing * double(k);
      auto* pm = polyscope::registerSurfaceMesh(cmp_name(k), W, M.F);
      if (figure) { pm->setSurfaceColor(color); pm->setSmoothShade(true); continue; }
      VectorXd flag(M.F.rows());
      const double thr = -std::sin(overhang * kPi / 180.0);
      for (int f = 0; f < M.F.rows(); ++f) {
        const Vector3d a = W.row(M.F(f, 0)), b = W.row(M.F(f, 1)), c = W.row(M.F(f, 2));
        flag(f) = (b - a).cross(c - a).normalized().z() < thr ? 1.0 : 0.0;
      }
      pm->addFaceScalarQuantity("needs support", flag)->setColorMap("reds")->setEnabled(true);
      if (cols.empty()) continue;
      MatrixXd N(cols.size(), 3); MatrixXi E(cols.size() / 2, 2);
      for (size_t i = 0; i < cols.size(); ++i) N.row(i) = cols[i] + Eigen::RowVector3d(spacing * double(k), 0, 0);
      for (size_t i = 0; i < cols.size() / 2; ++i) E.row(i) << int(2 * i), int(2 * i + 1);
      auto* cn = polyscope::registerCurveNetwork(cmp_sup(k), N, E);
      cn->setRadius(0.003 * size_mm, false); cn->setColor({0.35f, 0.75f, 0.45f});
    }
    if (polyscope::hasSurfaceMesh("part")) polyscope::getSurfaceMesh("part")->setEnabled(!on);
    if (polyscope::hasCurveNetwork("support columns"))
      polyscope::getCurveNetwork("support columns")->setEnabled(!on);
    for (const char* n : {"f on S^2", "f on (t1,t2)"})
      if (polyscope::hasSurfaceMesh(n)) polyscope::getSurfaceMesh(n)->setEnabled(!on);
    for (const char* n : {"optima (S^2)", "optima (t1,t2)"})
      if (polyscope::hasPointCloud(n)) polyscope::getPointCloud(n)->setEnabled(!on);
    if (on) {
      const float s = float(size_mm), mid = float(spacing * (poses.size() - 1) / 2);
      polyscope::view::lookAt(glm::vec3(mid, -std::max(2.4f * s, 1.7f * mid), 0.5f * s + 0.3f * mid),
                              glm::vec3(mid, 0.f, 0.35f * s));
    }
  };
  bool side_by_side = compare;
  if (compare) show_compare(true);

  auto apply_slice = [&]() {
    plane->setActive(slicing);
    if (slicing)
      plane->setPose(glm::vec3(0, 0, float(layer * est.height_mm)), glm::vec3(0, 0, -1));
  };

  polyscope::state::userCallback = [&]() {
    ImGui::PushItemWidth(180);
    std::vector<const char*> pnames; for (auto& p : poses) pnames.push_back(p.name.c_str());
    if (ImGui::Combo("pose", &cur_pose, pnames.data(), int(pnames.size()))) { show_pose(); apply_slice(); }
    if (ImGui::Checkbox("side by side (all poses)", &side_by_side)) show_compare(side_by_side);
    const char* onames[] = {"castro-eq", "alexander", "ezair (256^2)"};
    if (ImGui::Combo("landscape", &cur_obj, onames, 3)) show_landscape();
    float ov = float(overhang);
    if (ImGui::SliderFloat("overhang (deg)", &ov, 20.f, 70.f)) {
      overhang = ov; pp.overhang_deg = ov; show_pose();
      if (side_by_side) show_compare(true);
    }
    if (ImGui::Checkbox("layer view", &slicing)) apply_slice();
    if (slicing && ImGui::SliderFloat("layer", &layer, 0.f, 1.f)) apply_slice();
    ImGui::PopItemWidth();
    // polyscope's own screenshot restarts at screenshot_000000 in every session
    // (overwriting older files) and is transparent; this one never overwrites
    static std::string saved;
    if (ImGui::Button("save image")) {
      std::filesystem::create_directories("screenshots");
      char ts[32]; const std::time_t now = std::time(nullptr);
      std::strftime(ts, sizeof ts, "%Y%m%d-%H%M%S", std::localtime(&now));
      std::string base = "screenshots/" + M.name + "__" + (side_by_side ? "compare" : poses[cur_pose].name) + "__" + ts;
      std::string path = base + ".png";
      for (int n = 2; std::filesystem::exists(path); ++n) path = base + "-" + std::to_string(n) + ".png";
      polyscope::screenshot(path, false);
      saved = std::filesystem::absolute(path).string();
      if (side_by_side) {  // the image has no labels: write the order next to it
        std::ofstream t(path.substr(0, path.size() - 4) + ".txt");
        t << "poses left to right (" << M.name << ")";
        if (!slicer.empty()) t << "; PrusaSlicer support filament m / total m / time min";
        t << '\n';
        for (size_t k = 0; k < poses.size(); ++k) {
          t << k << ' ' << poses[k].name;
          if (slicer.count(poses[k].name)) {
            const auto& r = slicer.at(poses[k].name);
            char b[64];
            std::snprintf(b, sizeof b, "  %.2f / %.2f / %.0f", r.support_mm / 1000, r.filament_mm / 1000, r.time_min);
            t << b;
          }
          t << '\n';
        }
      }
    }
    if (!saved.empty()) { ImGui::SameLine(); ImGui::TextWrapped("saved %s", saved.c_str()); }
    const Pose& P = poses[cur_pose];
    ImGui::Separator();
    ImGui::Text("t1 = %.4f  t2 = %.4f", P.t1, P.t2);
    ImGui::Text("PROXY (not a slicer):");
    ImGui::Text("  height %.1f mm  layers %d", est.height_mm, est.layers);
    ImGui::Text("  overhang area %.0f mm2", est.overhang_area_mm2);
    ImGui::Text("  support envelope %.0f mm3 (on part %.0f)", est.support_volume_mm3, est.support_on_part_volume_mm3);
    ImGui::Text("  filament %.2f m  %.1f g  time %.0f min", est.filament_m, est.mass_g, est.time_min);
    if (slicer.count(P.name)) {
      const auto& s = slicer.at(P.name);
      ImGui::Text("PrusaSlicer estimate:");
      ImGui::Text("  filament %.2f m (support %.2f m)  %.1f g", s.filament_mm / 1000, s.support_mm / 1000, s.filament_g);
      ImGui::Text("  time %.0f min", s.time_min);
    }
    if (side_by_side) {  // all poses, left to right on the plate
      // name of each pose above its part, projected to the screen every frame
      const glm::mat4 VP = polyscope::view::getCameraPerspectiveMatrix() * polyscope::view::getCameraViewMatrix();
      const ImVec2 ds = ImGui::GetIO().DisplaySize;
      ImDrawList* dl = ImGui::GetBackgroundDrawList();
      for (size_t k = 0; k < poses.size(); ++k) {
        const float top = float(placed[k].col(2).maxCoeff() + 0.08 * size_mm);
        const glm::vec4 c = VP * glm::vec4(float(spacing * double(k)), 0.f, top, 1.f);
        if (c.w <= 0) continue;  // behind the camera
        const std::string t = cmp_name(k);
        const ImVec2 sz = ImGui::CalcTextSize(t.c_str());
        const ImVec2 q((c.x / c.w * 0.5f + 0.5f) * ds.x - sz.x / 2, (0.5f - c.y / c.w * 0.5f) * ds.y - sz.y / 2);
        dl->AddRectFilled(ImVec2(q.x - 4, q.y - 2), ImVec2(q.x + sz.x + 4, q.y + sz.y + 2), IM_COL32(255, 255, 255, 210), 3.f);
        dl->AddText(q, IM_COL32(20, 20, 20, 255), t.c_str());
      }
      ImGui::Separator();
      const bool sl = !slicer.empty();
      ImGui::Text(sl ? "All poses, left to right (PrusaSlicer):" : "All poses, left to right (proxy):");
      if (ImGui::BeginTable("poses", 5, ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg)) {
        for (const char* h : {"#", "pose", sl ? "support m" : "overhang mm2", sl ? "total m" : "filament m", "time min"})
          ImGui::TableSetupColumn(h);
        ImGui::TableHeadersRow();
        for (size_t k = 0; k < poses.size(); ++k) {
          ImGui::TableNextRow();
          ImGui::TableNextColumn(); ImGui::Text("%d", int(k));
          ImGui::TableNextColumn(); ImGui::Text("%s", poses[k].name.c_str());
          if (sl && slicer.count(poses[k].name)) {
            const auto& r = slicer.at(poses[k].name);
            ImGui::TableNextColumn(); ImGui::Text("%.2f", r.support_mm / 1000);
            ImGui::TableNextColumn(); ImGui::Text("%.2f", r.filament_mm / 1000);
            ImGui::TableNextColumn(); ImGui::Text("%.0f", r.time_min);
          } else if (sl) {
            for (int c = 0; c < 3; ++c) { ImGui::TableNextColumn(); ImGui::Text("-"); }
          } else {
            ImGui::TableNextColumn(); ImGui::Text("%.0f", all_est[k].overhang_area_mm2);
            ImGui::TableNextColumn(); ImGui::Text("%.2f", all_est[k].filament_m);
            ImGui::TableNextColumn(); ImGui::Text("%.0f", all_est[k].time_min);
          }
        }
        ImGui::EndTable();
      }
    }
  };

  if (!shots.empty() && compare) {  // one image with every pose
    polyscope::screenshot(shots + "/" + M.name + "__compare.png", figure);
    return 0;
  }
  if (!shots.empty()) {  // headless figure export
    for (cur_pose = 0; cur_pose < int(poses.size()); ++cur_pose) {
      show_pose();
      const float s = float(size_mm);
      if (figure) {  // frame the part alone, seen from the front and slightly above
        const MatrixXd W = place_on_plate(M, poses[cur_pose].t1, poses[cur_pose].t2, scale);
        const Vector3d lo = W.colwise().minCoeff(), hi = W.colwise().maxCoeff(), c = 0.5 * (lo + hi);
        const glm::vec3 C(float(c.x()), float(c.y()), float(c.z()));
        // --view-yaw: camera orbited about the vertical axis (a rotation about z
        // does not change what the slicer prints, only which side is seen)
        const float cy = std::cos(float(yaw_deg * kPi / 180)), sy = std::sin(float(yaw_deg * kPi / 180));
        const float ex = 0.75f * s, ey = -2.4f * s;
        polyscope::view::lookAt(C + glm::vec3(cy * ex - sy * ey, sy * ex + cy * ey, 1.0f * s), C);
      } else {
        polyscope::view::lookAt(glm::vec3(0.6f * s, -2.9f * s, 0.9f * s), glm::vec3(-0.45f * s, 0.5f * s, 0.35f * s));
      }
      polyscope::screenshot(shots + "/" + M.name + "__" + poses[cur_pose].name + ".png", figure);
    }
    return 0;
  }
  polyscope::show();
  return 0;
}
