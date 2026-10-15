// overhang-bench — orientation objectives f(d), d = build direction in the
// object frame (unit vector; see mesh.hpp). Lower is better for all of them.
//
// Implemented here:
//   castro-eq    Castro (2020), eq. (3.2.4) exactly as written: barycentric
//                height minus the minimum z over ALL vertices, times face area,
//                times the squared z-component of the rotated normal.
//   castro-code  Castro (2020), the MATLAB code of App. A.1 as it was run:
//                the height weight uses only the first vertex of each face,
//                and the minimum is taken over those first vertices.
//   alexander    Alexander, Allen & Dutta (1998), "Part orientation and build
//                cost determination in layered manufacturing", CAD 30(5),
//                as summarized in Castro (2020), Sec. 3.3, eq. (3.3.7).
//
// New methods: derive from Objective and register in make_objective().
#pragma once
#include "mesh.hpp"
#include <igl/AABB.h>
#include <igl/Hit.h>
#include <memory>
#include <vector>
#include <unordered_set>
#include <functional>
#include <limits>
#include <algorithm>

namespace ob {

struct Objective {
  virtual ~Objective() = default;
  virtual std::string name() const = 0;
  virtual double eval(const Vector3d& d) const = 0;
  // true if f is (piecewise) smooth enough for a gradient-based local solver
  virtual bool smooth() const { return true; }
  double eval_angles(double t1, double t2) const { return eval(direction(t1, t2)); }
};

// ---------------------------------------------------------------- Castro 2020
class CastroEq : public Objective {
 public:
  explicit CastroEq(const Mesh& M) : M_(M) {}
  std::string name() const override { return "castro-eq"; }
  double eval(const Vector3d& d) const override {
    const double minz = (M_.V * d).minCoeff();           // min_z^V after rotation
    const VectorXd h = (M_.B * d).array() - minz;        // e3^T R b_f - min_z^V
    const VectorXd nz = M_.N * d;                         // e3^T R n(f)
    return (M_.A.array() * h.array() * nz.array().square()).sum();
  }
 private:
  const Mesh& M_;
};

class CastroCode : public Objective {
 public:
  explicit CastroCode(const Mesh& M) : M_(M) {}
  std::string name() const override { return "castro-code"; }
  double eval(const Vector3d& d) const override {
    const VectorXd z1 = M_.P1 * d;                        // Vh(F(:,1),:) rotated
    const VectorXd h = z1.array() - z1.minCoeff();
    const VectorXd nz = M_.N * d;
    return (M_.A.array() * h.array() * nz.array().square()).sum();
  }
 private:
  const Mesh& M_;
};

// ------------------------------------------------------- Alexander et al. 1998
// Parameters as used in Castro (2020), Sec. 3.4: z_t = p = q = 0.1 cm, R = 10.
// `length_scale` converts mesh units to the units of z_t/p/q (e.g. cm).
// A face "needs support" when its normal points downward beyond the printable
// overhang angle: n.d < -sin(overhang_deg) (overhang_deg measured from the
// vertical; 45 deg is the usual FDM rule). A face is "touched from above" when
// the vertical ray cast downward from the barycenter of a supported face hits
// it first; each such face contributes R * A_proj once, with
// A_proj = min(p q / |n.d|, A_face) (Castro 2020, Sec. 3.3).
struct AlexanderParams {
  double zt = 0.1, p = 0.1, q = 0.1, R = 10.0;
  double overhang_deg = 45.0;
  double length_scale = 1.0;  // mesh units -> cm
};

class Alexander : public Objective {
 public:
  Alexander(const Mesh& M, AlexanderParams P) : M_(M), P_(P) { tree_.init(M_.V, M_.F); }
  std::string name() const override { return "alexander"; }
  bool smooth() const override { return false; }
  double eval(const Vector3d& d) const override {
    const double s2 = P_.length_scale * P_.length_scale;
    const double thr = -std::sin(P_.overhang_deg * M_PI / 180.0);
    const VectorXd c = M_.N * d;
    double f = 0.0;
    std::vector<char> touched(M_.F.rows(), 0);
    for (int i = 0; i < M_.F.rows(); ++i) {
      const double Ai = M_.A(i) * s2;
      f += Ai * P_.zt * std::abs(c(i));
      if (M_.A(i) > 0 && c(i) < thr) {
        f += Ai * P_.R;
        igl::Hit hit;
        const Eigen::RowVector3d o = M_.B.row(i) - 1e-9 * d.transpose();
        if (tree_.intersect_ray(M_.V, M_.F, o, -d.transpose(), hit) && hit.id != i)
          touched[hit.id] = 1;
      }
    }
    for (int j = 0; j < M_.F.rows(); ++j) {
      if (!touched[j]) continue;
      const double Aj = M_.A(j) * s2;
      const double cj = std::abs(c(j));
      const double Aproj = cj > 1e-12 ? std::min(P_.p * P_.q / cj, Aj) : Aj;
      f += P_.R * Aproj;
    }
    return f;
  }
 private:
  const Mesh& M_;
  AlexanderParams P_;
  igl::AABB<MatrixXd, 3> tree_;
};

// ------------------------------------------------------------ Ezair et al. 2015
// Ezair, Massarwi & Elber (2015), "Orientation analysis of 3D objects toward
// minimal support volume in 3D-printing", Computers & Graphics 51:117-124.
// Def. 3.1 / Cor. 3.2: the support is S = T - M, where the "top cover" T is
// everything below any point of the model down to the floor z = Zmin (the
// lowest point of the model); V(S) = V(T) - V(M). No self-supporting angle:
// every region below the model is supported, always down to the floor.
// V(T) is computed as in their Algorithm 1: an orthographic z-buffer of the
// highest model point per pixel over the bounding-sphere square (default
// 1024^2 pixels), V(T) = sum_pixels (z_top - Zmin) * pixel_area.
// (They render on the GPU; this is the same computation on the CPU.)
// Returns V(S) in mesh units^3.
class EzairSupportVolume : public Objective {
 public:
  explicit EzairSupportVolume(const Mesh& M, int res = 1024) : M_(M), res_(res) {
    center_ = M_.V.colwise().mean().transpose();
    radius_ = (M_.V.rowwise() - center_.transpose()).rowwise().norm().maxCoeff() * (1 + 1e-9);
  }
  std::string name() const override { return "ezair"; }
  bool smooth() const override { return false; }
  double eval(const Vector3d& dd) const override {
    const Vector3d d = dd.normalized();
    // any orthonormal frame (u, v, d); V(T) does not depend on the rotation about d
    const Vector3d a = std::abs(d.x()) < 0.9 ? Vector3d::UnitX() : Vector3d::UnitY();
    const Vector3d u = d.cross(a).normalized(), v = d.cross(u);
    const int n = static_cast<int>(M_.V.rows());
    thread_local std::vector<double> X, Y, Z;
    thread_local std::vector<float> zb;
    X.resize(n); Y.resize(n); Z.resize(n);
    double zmin = 1e300;
    const double cu = center_.dot(u), cv = center_.dot(v);
    const double h = 2 * radius_ / res_;  // pixel size
    for (int i = 0; i < n; ++i) {
      const Vector3d p = M_.V.row(i);
      X[i] = (p.dot(u) - cu + radius_) / h;  // pixel coordinates
      Y[i] = (p.dot(v) - cv + radius_) / h;
      Z[i] = p.dot(d);
      zmin = std::min(zmin, Z[i]);
    }
    zb.assign(static_cast<size_t>(res_) * res_, -std::numeric_limits<float>::infinity());
    for (int f = 0; f < M_.F.rows(); ++f) {
      const int i0 = M_.F(f, 0), i1 = M_.F(f, 1), i2 = M_.F(f, 2);
      const double x0 = X[i0], y0 = Y[i0], x1 = X[i1], y1 = Y[i1], x2 = X[i2], y2 = Y[i2];
      const double area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0);
      if (std::abs(area) < 1e-14) continue;  // edge-on triangle: covered by its neighbours
      const int px0 = std::max(0, static_cast<int>(std::floor(std::min({x0, x1, x2}))));
      const int px1 = std::min(res_ - 1, static_cast<int>(std::ceil(std::max({x0, x1, x2}))));
      const int py0 = std::max(0, static_cast<int>(std::floor(std::min({y0, y1, y2}))));
      const int py1 = std::min(res_ - 1, static_cast<int>(std::ceil(std::max({y0, y1, y2}))));
      for (int py = py0; py <= py1; ++py)
        for (int px = px0; px <= px1; ++px) {
          const double x = px + 0.5, y = py + 0.5;  // pixel centre
          const double w0 = ((x1 - x) * (y2 - y) - (x2 - x) * (y1 - y)) / area;
          const double w1 = ((x2 - x) * (y0 - y) - (x0 - x) * (y2 - y)) / area;
          const double w2 = 1.0 - w0 - w1;
          if (w0 < 0 || w1 < 0 || w2 < 0) continue;
          const float z = static_cast<float>(w0 * Z[i0] + w1 * Z[i1] + w2 * Z[i2]);
          float& zz = zb[static_cast<size_t>(py) * res_ + px];
          if (z > zz) zz = z;
        }
    }
    double vt = 0;
    for (float z : zb) if (z > -1e30f) vt += z - zmin;
    return vt * h * h - M_.signed_volume;
  }
 private:
  const Mesh& M_;
  int res_;
  Vector3d center_;
  double radius_;
};

// ------------------------------------------------------ Goguelin et al. 2021
// Goguelin, Dhokia & Flynn (2021), "Bayesian optimisation of part orientation in
// additive manufacturing", Int. J. Computer Integrated Manufacturing
// 34(12):1263-1284, Sec. 3.3. A facet overhangs when its outward normal lies
// in the cone of half-angle theta_crit (45 deg) around the downward build
// direction (their Fig. 1, eq. 1). Rays are cast downwards and stop at the first
// collision with the mesh or with the build plate (the plane through the
// lowest point of the part):
//   length (eq. 2): sum over overhanging facets of the ray length from the
//                   facet centroid;
//   volume (eq. 3): sum over overhanging facets of (d1+d2+d3)/3 * A, with
//                   d1..d3 the ray lengths from the three vertices and A the
//                   (unprojected) facet area.
// The paper found the length proxy the most effective. Values in mesh units.
class Goguelin : public Objective {
 public:
  Goguelin(const Mesh& M, bool volume, double theta_crit_deg = 45.0)
      : M_(M), volume_(volume), cos_crit_(std::cos(theta_crit_deg * M_PI / 180.0)) {
    tree_.init(M_.V, M_.F);
    eps_ = 1e-7 * (M_.V.colwise().maxCoeff() - M_.V.colwise().minCoeff()).norm();
  }
  std::string name() const override { return volume_ ? "goguelin-vol" : "goguelin-len"; }
  bool smooth() const override { return false; }
  double eval(const Vector3d& dd) const override {
    const Vector3d d = dd.normalized();
    const double plate = (M_.V * d).minCoeff();
    const VectorXd c = M_.N * d;
    auto ray = [&](const Eigen::RowVector3d& p, int f) {
      // first collision along -d with the mesh, otherwise the plate. The origin is
      // moved eps below p: facets through p (the facet itself, or those sharing
      // the vertex) then lie behind the origin and cannot be hit.
      (void)f;
      igl::Hit h;
      const Eigen::RowVector3d o = p - eps_ * d.transpose();
      double best = p.dot(d) - plate;
      if (tree_.intersect_ray(M_.V, M_.F, o, Eigen::RowVector3d(-d.transpose()), 0.0, h))
        best = std::min(best, static_cast<double>(h.t) + eps_);
      return std::max(0.0, best);
    };
    double s = 0;
    for (int f = 0; f < M_.F.rows(); ++f) {
      if (M_.A(f) <= 0 || c(f) > -cos_crit_) continue;  // normal outside the downward cone
      if (!volume_) {
        s += ray(M_.B.row(f), f);
      } else {
        double dsum = 0;
        for (int k = 0; k < 3; ++k) dsum += ray(M_.V.row(M_.F(f, k)), f);
        s += dsum / 3.0 * M_.A(f);
      }
    }
    return s;
  }
 private:
  const Mesh& M_;
  bool volume_;
  double cos_crit_, eps_;
  igl::AABB<MatrixXd, 3> tree_;
};

// ------------------------------------------------- ablation: support volume
// Direct minimization of the proxy's support volume (vertical columns under
// faces beyond the overhang angle, down to the plate or to the part; see
// simulate.hpp). Not a published method: it answers "why not optimize the
// support volume itself?". Defined in simulate.hpp's terms, so it is created
// in make_objective() below through a callback to avoid a circular include.
class Callback : public Objective {
 public:
  Callback(std::string n, std::function<double(const Vector3d&)> f) : n_(std::move(n)), f_(std::move(f)) {}
  std::string name() const override { return n_; }
  bool smooth() const override { return false; }
  double eval(const Vector3d& d) const override { return f_(d); }
 private:
  std::string n_;
  std::function<double(const Vector3d&)> f_;
};

inline std::unique_ptr<Objective> make_objective(const std::string& name, const Mesh& M,
                                                 const AlexanderParams& ap = {}) {
  if (name == "castro-eq") return std::make_unique<CastroEq>(M);
  if (name == "castro-code") return std::make_unique<CastroCode>(M);
  if (name == "alexander") return std::make_unique<Alexander>(M, ap);
  if (name == "ezair") return std::make_unique<EzairSupportVolume>(M);
  if (name == "goguelin-len") return std::make_unique<Goguelin>(M, false, ap.overhang_deg);
  if (name == "goguelin-vol") return std::make_unique<Goguelin>(M, true, ap.overhang_deg);
  throw std::runtime_error("unknown objective: " + name);
}

}  // namespace ob
