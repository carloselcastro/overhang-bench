// overhang-bench — command-line benchmark.
//
//   bench --out results --size-mm 60 \
//         --objectives castro-eq,castro-code,alexander \
//         --searches grid,mcd-asrun,mcd,rcsp,sphere \
//         meshes/arm.obj meshes/bunny.off ...
//
// Writes:
//   results/orientations.csv  one row per (mesh, objective, search)
//   results/print_proxy.csv   proxy print estimate for the initial pose and for
//                             the best pose of each objective
//   results/stl/<mesh>__<pose>.stl  placed, scaled STLs for a real slicer
//   results/landscape/<mesh>__<objective>.csv  (with --landscape) f on the grid
#include "ob/mesh.hpp"
#include "ob/objectives.hpp"
#include "ob/optimize.hpp"
#include "ob/simulate.hpp"
#include <igl/writeSTL.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <map>
#include <sstream>

namespace fs = std::filesystem;
using namespace ob;

static std::vector<std::string> split(const std::string& s, char c = ',') {
  std::vector<std::string> out; std::stringstream ss(s); std::string t;
  while (std::getline(ss, t, c)) if (!t.empty()) out.push_back(t);
  return out;
}

static void usage() {
  std::cerr << "usage: bench [--out DIR] [--size-mm S] [--grid-deg G] [--sphere-n N]\n"
               "             [--objectives a,b,..] [--searches a,b,..] [--overhang-deg A]\n"
               "             [--cell-mm C] [--landscape] [--no-stl] [--y-up]\n"
               "             [--poses CSV(mesh,pose,t1,t2)] MESH[@rx90,...]...\n"
               "  --searches none --poses CSV  evaluates external poses only (appends)\n";
}

int main(int argc, char** argv) {
  std::string out = "results";
  double size_mm = 60.0, grid_deg = 1.0, overhang = 45.0, cell = 0.5;
  int sphere_n = 20000;
  bool landscape = false, write_stl = true, y_up = false;
  std::vector<std::string> objectives{"castro-eq", "castro-code", "alexander"};
  std::vector<std::string> searches{"grid", "mcd-asrun", "mcd", "rcsp", "sphere"};
  std::vector<std::string> meshes;
  std::string poses_csv;  // extra poses from external methods: mesh,pose,t1,t2
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() { if (i + 1 >= argc) { usage(); std::exit(1); } return std::string(argv[++i]); };
    if (a == "--out") out = next();
    else if (a == "--size-mm") size_mm = std::stod(next());
    else if (a == "--grid-deg") grid_deg = std::stod(next());
    else if (a == "--sphere-n") sphere_n = std::stoi(next());
    else if (a == "--overhang-deg") overhang = std::stod(next());
    else if (a == "--cell-mm") cell = std::stod(next());
    else if (a == "--objectives") objectives = split(next());
    else if (a == "--searches") { searches = split(next()); if (searches == std::vector<std::string>{"none"}) searches.clear(); }
    else if (a == "--landscape") landscape = true;
    else if (a == "--no-stl") write_stl = false;
    else if (a == "--y-up") y_up = true;
    else if (a == "--poses") poses_csv = next();
    else if (a == "-h" || a == "--help") { usage(); return 0; }
    else meshes.push_back(a);
  }
  if (meshes.empty()) { usage(); return 1; }
  fs::create_directories(out + "/stl");
  if (landscape) fs::create_directories(out + "/landscape");

  // Output files are appended to when they already exist (so external methods
  // can be evaluated in a second call with --searches none --poses CSV).
  auto open_csv = [&](const std::string& name, const std::string& header) {
    const std::string path = out + "/" + name;
    const bool exists = fs::exists(path) && fs::file_size(path) > 0;
    auto f = std::make_unique<std::ofstream>(path, std::ios::app);
    if (!exists) *f << header << '\n';
    *f << std::setprecision(10);
    return f;
  };
  std::unique_ptr<std::ofstream> fo_ptr;
  if (!searches.empty())
    fo_ptr = open_csv("orientations.csv", "mesh,faces,closed,objective,search,t1,t2,dx,dy,dz,fval,evals,seconds");
  auto fp_ptr = open_csv("print_proxy.csv",
      "mesh,pose,t1,t2,height_mm,part_volume_mm3,overhang_area_mm2,support_volume_mm3,"
      "support_on_part_volume_mm3,support_contact_mm2,filament_m,mass_g,time_min");
  auto fe_ptr = open_csv("poses_eval.csv", "mesh,pose,objective,t1,t2,fval");
  std::ofstream& fp = *fp_ptr;
  std::ofstream& fe = *fe_ptr;

  // external poses, keyed by mesh name
  std::map<std::string, std::vector<std::pair<std::string, Result>>> extra;
  if (!poses_csv.empty()) {
    std::ifstream in(poses_csv); std::string line; std::getline(in, line);
    while (std::getline(in, line)) {
      const auto v = split(line);
      if (v.size() < 4) continue;
      Result r; r.t1 = std::stod(v[2]); r.t2 = std::stod(v[3]);
      extra[v[0]].emplace_back(v[1], r);
    }
  }

  PrintParams pp; pp.overhang_deg = overhang; pp.cell_mm = cell;

  for (const auto& path : meshes) {
    // MESH may carry a pre-rotation: path@rx90,rz180 (see mesh.hpp)
    const auto at = path.find('@');
    Mesh M = at == std::string::npos ? load_mesh(path, y_up)
                                     : load_mesh(path.substr(0, at), y_up, path.substr(at + 1));
    const double maxdim = (M.V.colwise().maxCoeff() - M.V.colwise().minCoeff()).maxCoeff();
    const double scale = size_mm / maxdim;  // mesh units -> mm (same for all poses)
    AlexanderParams ap; ap.overhang_deg = overhang; ap.length_scale = scale / 10.0;  // -> cm
    std::cerr << "[" << M.name << "] |F|=" << M.F.rows() << " boundary edges=" << M.boundary_edges
              << (M.flipped ? " (reoriented)" : "") << "\n";

    std::map<std::string, Result> best;
    for (const auto& on : objectives) {
      auto obj = on == "support-volume" ? make_support_volume_objective(M, scale, pp)
                                        : make_objective(on, M, ap);
      for (const auto& sn : searches) {
        Result r;
        if (sn == "grid") r = grid_search(*obj, grid_deg * kPi / 180.0);
        else if (sn == "mcd-asrun") r = multistart(*obj, starts_mcd(true), sn);
        else if (sn == "mcd") r = multistart(*obj, starts_mcd(false), sn);
        else if (sn == "rcsp") r = multistart(*obj, starts_rcsp(), sn);
        else if (sn == "sphere") r = sphere_search(*obj, sphere_n);
        else if (sn == "ezair") r = ezair_search(*obj);
        else throw std::runtime_error("unknown search: " + sn);
        const Vector3d d = r.d();
        std::ofstream& fo = *fo_ptr;
        fo << M.name << ',' << M.F.rows() << ',' << (M.boundary_edges == 0) << ',' << on << ','
           << sn << ',' << r.t1 << ',' << r.t2 << ',' << d.x() << ',' << d.y() << ',' << d.z()
           << ',' << r.fval << ',' << r.evals << ',' << r.seconds << '\n';
        fo.flush();
        std::cerr << "  " << std::setw(12) << on << " " << std::setw(10) << sn << "  t=("
                  << std::fixed << std::setprecision(4) << r.t1 << "," << r.t2 << ")  f="
                  << std::scientific << r.fval << std::defaultfloat << "  " << r.evals
                  << " evals  " << r.seconds << "s\n";
        if (!best.count(on) || r.fval < best[on].fval) best[on] = r;
      }
      if (landscape) {
        std::ofstream fl(out + "/landscape/" + M.name + "__" + on + ".csv");
        fl << "t1,t2,f\n" << std::setprecision(10);
        const double st = grid_deg * kPi / 180.0;
        for (double t1 = -kPi; t1 <= kPi + 1e-9; t1 += st)
          for (double t2 = -kPi / 2; t2 <= kPi / 2 + 1e-9; t2 += st)
            fl << t1 << ',' << t2 << ',' << obj->eval_angles(t1, t2) << '\n';
      }
    }

    std::vector<std::pair<std::string, Result>> poses;
    if (searches.empty() && extra.count(M.name)) {
      poses = extra[M.name];  // evaluation-only call
    } else {
      poses.emplace_back("initial", Result{});
      for (auto& [k, r] : best) poses.emplace_back(k, r);
      if (extra.count(M.name)) for (auto& p : extra[M.name]) poses.push_back(p);
    }
    // every objective evaluated at every pose (cross-comparison table)
    std::vector<std::unique_ptr<Objective>> all;
    for (const char* n : {"castro-code", "castro-eq", "alexander", "ezair", "goguelin-len", "goguelin-vol"})
      all.push_back(make_objective(n, M, ap));
    all.push_back(make_support_volume_objective(M, scale, pp));
    for (auto& [pose, r] : poses)
      for (auto& o : all)
        fe << M.name << ',' << pose << ',' << o->name() << ',' << r.t1 << ',' << r.t2 << ','
           << o->eval_angles(r.t1, r.t2) << '\n';
    fe.flush();
    for (auto& [pose, r] : poses) {
      const MatrixXd W = place_on_plate(M, r.t1, r.t2, scale);
      const PrintEstimate E = estimate_print(W, M.F, pp);
      fp << M.name << ',' << pose << ',' << r.t1 << ',' << r.t2 << ',' << E.height_mm << ','
         << E.part_volume_mm3 << ',' << E.overhang_area_mm2 << ',' << E.support_volume_mm3 << ','
         << E.support_on_part_volume_mm3 << ',' << E.support_contact_mm2 << ',' << E.filament_m
         << ',' << E.mass_g << ',' << E.time_min << '\n';
      if (write_stl)
        igl::writeSTL(out + "/stl/" + M.name + "__" + pose + ".stl", W, M.F,
                      igl::FileEncoding::Binary);
    }
    fp.flush();
  }
  return 0;
}
