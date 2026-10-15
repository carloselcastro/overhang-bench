// overhang-bench — fast print-cost PROXY (not a slicer).
//
// Support: vertical columns on an xy raster (cell size `cell_mm`). For every
// raster cell a ray is cast upward through the placed part; along the ray, each
// downward-facing hit whose face is an overhang (n_z < -sin(overhang_deg), angle
// measured from the vertical) receives a column from the surface directly
// below it (the build plate, or the top of the part underneath). This is the
// usual vertical-support model of the orientation literature (e.g. Ezair,
// Massarwi & Elber 2015, "Orientation analysis of 3D objects toward minimal
// support volume in 3D-printing", Computers & Graphics 51).
//
// Material and time are rough linear models of an FDM print; they exist only to
// rank orientations quickly. Absolute numbers must come from a real slicer
// (scripts/slice_prusaslicer.py), and the proxy should be reported together with
// its correlation to the slicer, never as a measurement.
#pragma once
#include "mesh.hpp"
#include "objectives.hpp"
#include <memory>
#include <igl/AABB.h>
#include <igl/Hit.h>
#include <vector>
#include <algorithm>

namespace ob {

struct PrintParams {
  double overhang_deg = 45.0;   // printable overhang from the vertical
  double cell_mm = 0.5;         // support raster
  double layer_mm = 0.2;
  double line_width_mm = 0.45;
  int perimeters = 2;
  double infill = 0.15;         // part infill fraction
  double support_density = 0.15;
  double filament_d_mm = 1.75;
  double density_g_cm3 = 1.24;  // PLA
  double speed_mm_s = 45.0;     // average extrusion speed
  double layer_overhead_s = 1.5;
};

struct PrintEstimate {
  double height_mm = 0, part_volume_mm3 = 0, surface_mm2 = 0;
  double overhang_area_mm2 = 0;          // area of faces beyond the overhang angle
  double support_volume_mm3 = 0;         // envelope volume of the vertical columns
  double support_on_part_volume_mm3 = 0; // columns that stand on the part itself
  double support_contact_mm2 = 0;        // footprint where supports touch the part
  double extruded_mm3 = 0, filament_m = 0, mass_g = 0, time_min = 0;
  int layers = 0;
};

// W: vertices already placed on the plate (mm), F: faces with outward normals.
inline PrintEstimate estimate_print(const MatrixXd& W, const MatrixXi& F, const PrintParams& P,
                                    std::vector<Eigen::RowVector3d>* columns = nullptr) {
  PrintEstimate E;
  const double thr = -std::sin(P.overhang_deg * M_PI / 180.0);
  const int m = static_cast<int>(F.rows());
  VectorXd nz(m);
  for (int f = 0; f < m; ++f) {
    const Vector3d a = W.row(F(f, 0)), b = W.row(F(f, 1)), c = W.row(F(f, 2));
    const Vector3d x = (b - a).cross(c - a);
    const double area = 0.5 * x.norm();
    nz(f) = area > 0 ? x.z() / x.norm() : 0.0;
    E.surface_mm2 += area;
    E.part_volume_mm3 += a.dot(b.cross(c)) / 6.0;
    if (nz(f) < thr) E.overhang_area_mm2 += area;
  }
  E.height_mm = W.col(2).maxCoeff();

  igl::AABB<MatrixXd, 3> tree;
  tree.init(W, F);
  const Eigen::RowVector3d mn = W.colwise().minCoeff(), mx = W.colwise().maxCoeff();
  const int nx = std::max(1, static_cast<int>(std::ceil((mx.x() - mn.x()) / P.cell_mm)));
  const int ny = std::max(1, static_cast<int>(std::ceil((mx.y() - mn.y()) / P.cell_mm)));
  const double ca = P.cell_mm * P.cell_mm;
  double vs = 0, vsp = 0, cont = 0;
#pragma omp parallel for reduction(+ : vs, vsp, cont) schedule(dynamic, 8)
  for (int i = 0; i < nx; ++i) {
    std::vector<igl::Hit> hits;
    for (int j = 0; j < ny; ++j) {
      // tiny irrational offsets keep rays off mesh edges/vertices
      const Eigen::RowVector3d o(mn.x() + (i + 0.5) * P.cell_mm + 1.3e-5,
                                 mn.y() + (j + 0.5) * P.cell_mm + 0.7e-5, -1.0);
      hits.clear();
      if (!tree.intersect_ray(W, F, o, Eigen::RowVector3d(0, 0, 1), hits)) continue;
      std::sort(hits.begin(), hits.end(), [](const igl::Hit& a, const igl::Hit& b) { return a.t < b.t; });
      double floor_z = 0.0;  // top of whatever lies below (plate at z=0)
      for (const auto& h : hits) {
        const double z = o.z() + h.t;
        const double n = nz(h.id);
        if (n < 0) {  // downward-facing surface
          if (n < thr && z - floor_z > P.layer_mm) {
            vs += ca * (z - floor_z);
            if (floor_z > P.layer_mm) { vsp += ca * (z - floor_z); cont += ca; }
#pragma omp critical
            if (columns) {
              columns->emplace_back(o.x(), o.y(), floor_z);
              columns->emplace_back(o.x(), o.y(), z);
            }
          }
        } else {
          floor_z = z;
        }
      }
    }
  }
  E.support_volume_mm3 = vs;
  E.support_on_part_volume_mm3 = vsp;
  E.support_contact_mm2 = cont;

  // Material: shells (perimeters) + sparse infill, plus sparse support.
  const double shell = std::min(E.part_volume_mm3,
                                E.surface_mm2 * P.perimeters * P.line_width_mm);
  const double part_ext = shell + P.infill * std::max(0.0, E.part_volume_mm3 - shell);
  const double sup_ext = P.support_density * E.support_volume_mm3;
  E.extruded_mm3 = part_ext + sup_ext;
  const double fil_area = M_PI * 0.25 * P.filament_d_mm * P.filament_d_mm;
  E.filament_m = E.extruded_mm3 / fil_area / 1000.0;
  E.mass_g = E.extruded_mm3 / 1000.0 * P.density_g_cm3;
  E.layers = static_cast<int>(std::ceil(E.height_mm / P.layer_mm));
  const double flow = P.line_width_mm * P.layer_mm * P.speed_mm_s;  // mm^3/s
  E.time_min = (E.extruded_mm3 / flow + E.layers * P.layer_overhead_s) / 60.0;
  return E;
}

}  // namespace ob
