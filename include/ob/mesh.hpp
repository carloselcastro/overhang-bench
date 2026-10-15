// overhang-bench — mesh loading and per-face geometry.
// Conventions follow Castro (2020), "Optimal rotations for overhang reduction",
// MSc dissertation, UFSC, Sec. 2.3 (Def. 2.3.3: n(f) = (v_j-v_i) x (v_k-v_i) / ||.||).
#pragma once
#include <Eigen/Core>
#include <Eigen/Geometry>
#include <igl/read_triangle_mesh.h>
#include <igl/boundary_facets.h>
#include <igl/edges.h>
#include <stdexcept>
#include <string>
#include <cmath>

namespace ob {

using Eigen::MatrixXd;
using Eigen::MatrixXi;
using Eigen::Vector3d;
using Eigen::VectorXd;

struct Mesh {
  std::string name;
  MatrixXd V;   // #V x 3
  MatrixXi F;   // #F x 3
  MatrixXd N;   // #F x 3 unit face normals (zero row for degenerate faces)
  VectorXd A;   // #F face areas
  MatrixXd B;   // #F x 3 face barycenters (v1+v2+v3)/3
  double signed_volume = 0.0;
  int boundary_edges = 0;  // 0 => closed (watertight in the combinatorial sense)
  bool flipped = false;    // true if F was reoriented to make the volume positive

  void compute() {
    const int m = static_cast<int>(F.rows());
    N.resize(m, 3); A.resize(m); B.resize(m, 3);
    signed_volume = 0.0;
    for (int f = 0; f < m; ++f) {
      const Vector3d a = V.row(F(f, 0)), b = V.row(F(f, 1)), c = V.row(F(f, 2));
      const Vector3d x = (b - a).cross(c - a);
      const double nx = x.norm();
      A(f) = 0.5 * nx;
      N.row(f) = nx > 0 ? Vector3d(x / nx) : Vector3d::Zero();
      B.row(f) = (a + b + c) / 3.0;
      signed_volume += a.dot(b.cross(c)) / 6.0;  // divergence theorem
    }
  }
};

// Forward declaration (defined below).
inline Eigen::Matrix3d rot_x(double t);

inline Eigen::Matrix3d rot_z(double t) {
  Eigen::Matrix3d R;
  R << std::cos(t), -std::sin(t), 0, std::sin(t), std::cos(t), 0, 0, 0, 1;
  return R;
}
inline Eigen::Matrix3d rot_y(double t);

// Pre-rotation spec such as "rx90,rz180": rotations about the fixed axes, in
// degrees, applied left to right to the vertices as read from the file.
inline Eigen::Matrix3d parse_prerotation(const std::string& spec) {
  Eigen::Matrix3d Q = Eigen::Matrix3d::Identity();
  size_t i = 0;
  while (i < spec.size()) {
    size_t j = spec.find(',', i);
    if (j == std::string::npos) j = spec.size();
    const std::string tok = spec.substr(i, j - i);
    if (tok.size() >= 3 && tok[0] == 'r') {
      const double a = std::stod(tok.substr(2)) * 3.14159265358979323846 / 180.0;
      const Eigen::Matrix3d S = tok[1] == 'x' ? rot_x(a) : tok[1] == 'y' ? rot_y(a) : rot_z(a);
      Q = S * Q;
    }
    i = j + 1;
  }
  return Q;
}

// y_up: the file uses the y-up convention (libigl data); convert it to z-up by
// the rotation R_{e1}(pi/2), (x,y,z) -> (x,-z,y). Castro (2020) optimized the
// z-up meshes: with this conversion the optimal t1 of the dissertation is
// reproduced (without it, t1 is shifted by exactly pi/2).
// `pre`: optional pre-rotation spec (see parse_prerotation), applied after y_up.
inline Mesh load_mesh(const std::string& path, bool y_up = false, const std::string& pre = "",
                      bool orient_outward = true) {
  Mesh M;
  if (!igl::read_triangle_mesh(path, M.V, M.F) || M.F.rows() == 0)
    throw std::runtime_error("could not read mesh: " + path);
  if (y_up) M.V = (M.V * rot_x(1.5707963267948966).transpose()).eval();
  if (!pre.empty()) M.V = (M.V * parse_prerotation(pre).transpose()).eval();
  const auto slash = path.find_last_of("/\\");
  M.name = path.substr(slash == std::string::npos ? 0 : slash + 1);
  M.name = M.name.substr(0, M.name.find_last_of('.'));
  M.compute();
  if (orient_outward && M.signed_volume < 0) {  // make normals point outward
    M.F.col(1).swap(M.F.col(2));
    M.flipped = true;
    M.compute();
  }
  MatrixXi Fb;
  igl::boundary_facets(M.F, Fb);
  M.boundary_edges = static_cast<int>(Fb.rows());
  return M;
}

// ---------------------------------------------------------------------------
// Rotation parameterization used in the dissertation (Sec. 3 and eq. 4.0.1):
//   R(t1,t2) = R_{e2}(t2) R_{e1}(t1),  (t1,t2) in (-pi,pi] x [-pi/2,pi/2].
// The build direction expressed in the object frame is d = R^T e3, i.e. the
// third row of R:  d = (-sin t2, sin t1 cos t2, cos t1 cos t2).
// Every objective below depends on (t1,t2) only through d (heights are d.p,
// the z-component of a rotated normal is d.n), so the problem lives on S^2.
// ---------------------------------------------------------------------------
inline Eigen::Matrix3d rot_x(double t) {
  Eigen::Matrix3d R;
  R << 1, 0, 0, 0, std::cos(t), -std::sin(t), 0, std::sin(t), std::cos(t);
  return R;
}
inline Eigen::Matrix3d rot_y(double t) {
  Eigen::Matrix3d R;
  R << std::cos(t), 0, std::sin(t), 0, 1, 0, -std::sin(t), 0, std::cos(t);
  return R;
}
inline Eigen::Matrix3d rotation(double t1, double t2) { return rot_y(t2) * rot_x(t1); }

inline Vector3d direction(double t1, double t2) {
  return Vector3d(-std::sin(t2), std::sin(t1) * std::cos(t2), std::cos(t1) * std::cos(t2));
}
// Inverse of direction(): returns (t1,t2) with t2 = asin(-dx), t1 = atan2(dy,dz).
inline Eigen::Vector2d angles_from_direction(const Vector3d& d) {
  const double dx = std::max(-1.0, std::min(1.0, d.x()));
  return Eigen::Vector2d(std::atan2(d.y(), d.z()), std::asin(-dx));
}

// Place a rotated copy of the mesh on the build plate: rotate by R(t1,t2),
// scale uniformly by `scale`, put min z at 0 and center the xy bounding box.
inline MatrixXd place_on_plate(const Mesh& M, double t1, double t2, double scale) {
  const Eigen::Matrix3d R = rotation(t1, t2);
  MatrixXd W = (M.V * R.transpose()) * scale;
  const Eigen::RowVector3d mn = W.colwise().minCoeff(), mx = W.colwise().maxCoeff();
  Eigen::RowVector3d shift(-(mn.x() + mx.x()) / 2, -(mn.y() + mx.y()) / 2, -mn.z());
  W.rowwise() += shift;
  return W;
}

}  // namespace ob
