// overhang-bench — search strategies over (t1,t2) in (-pi,pi] x [-pi/2,pi/2].
//
//   grid        exhaustive grid with step Delta (Castro 2020, Sec. 3.4 used pi/180:
//               361 x 181 = 65341 evaluations).
//   mcd-asrun   multistart "multiple constraint division" (Castro 2020, Sec. 4.2)
//               with the starting points exactly as in App. A.1.1:
//               x0 = ((ii+h)/2, (jj+h)/2), h = pi/4 (32 points).
//   mcd         same, with the cell centers x0 = (ii+h/2, jj+h/2).
//   rcsp        32 uniformly random starting points (Castro 2020, Sec. 4.2).
//   sphere      Fibonacci-lattice sampling of S^2 (quasi-uniform in d, unlike the
//               (t1,t2) grid which oversamples the poles) + local refinement.
//
// Local solver: L-BFGS-B (Byrd, Lu, Nocedal & Zhu 1995, SIAM J. Sci. Comput.
// 16(5)) via LBFGSpp, with central-difference gradients (Nocedal & Wright 2006,
// eq. 8.7; Castro 2020 eq. 4.1.1). This replaces MATLAB's fmincon
// (interior-point + BFGS), which has no drop-in C++ equivalent.
// Non-smooth objectives are refined with Nelder-Mead (Nelder & Mead 1965,
// Computer Journal 7(4)) instead.
#pragma once
#include "objectives.hpp"
#include <LBFGSB.h>
#include <chrono>
#include <random>
#include <atomic>

namespace ob {

struct Result {
  std::string objective, search;
  double t1 = 0, t2 = 0, fval = 0;
  long evals = 0;
  double seconds = 0;
  Vector3d d() const { return direction(t1, t2); }
};

constexpr double kPi = 3.14159265358979323846;
inline const Eigen::Vector2d kLB(-kPi, -kPi / 2), kUB(kPi, kPi / 2);

class Counted {
 public:
  explicit Counted(const Objective& f) : f_(f) {}
  double operator()(double t1, double t2) const { ++n_; return f_.eval_angles(t1, t2); }
  long count() const { return n_; }
 private:
  const Objective& f_;
  mutable std::atomic<long> n_{0};
};

inline Result grid_search(const Objective& f, double step) {
  auto t0 = std::chrono::steady_clock::now();
  const int n1 = static_cast<int>(std::floor(2 * kPi / step + 1e-9)) + 1;
  const int n2 = static_cast<int>(std::floor(kPi / step + 1e-9)) + 1;
  std::vector<double> val(static_cast<size_t>(n1) * n2);
#pragma omp parallel for schedule(dynamic, 4)
  for (int i = 0; i < n1; ++i)
    for (int j = 0; j < n2; ++j)
      val[static_cast<size_t>(i) * n2 + j] = f.eval_angles(-kPi + i * step, -kPi / 2 + j * step);
  size_t best = 0;
  for (size_t k = 1; k < val.size(); ++k) if (val[k] < val[best]) best = k;
  Result r;
  r.objective = f.name(); r.search = "grid";
  r.t1 = -kPi + static_cast<int>(best / n2) * step;
  r.t2 = -kPi / 2 + static_cast<int>(best % n2) * step;
  r.fval = val[best]; r.evals = static_cast<long>(val.size());
  r.seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  return r;
}

// --------------------------------------------------------------- local solvers
struct FDProblem {
  const Counted& f; double eps;
  double operator()(const Eigen::VectorXd& x, Eigen::VectorXd& g) {
    const double fx = f(x(0), x(1));
    g.resize(2);
    for (int k = 0; k < 2; ++k) {
      Eigen::VectorXd xp = x, xm = x;
      xp(k) = std::min(xp(k) + eps, kUB(k)); xm(k) = std::max(xm(k) - eps, kLB(k));
      g(k) = (f(xp(0), xp(1)) - f(xm(0), xm(1))) / (xp(k) - xm(k));
    }
    return fx;
  }
};

inline Eigen::Vector2d clamp_box(Eigen::Vector2d x) {
  return x.cwiseMax(kLB).cwiseMin(kUB);
}

inline std::pair<Eigen::Vector2d, double> local_lbfgsb(const Counted& f, Eigen::Vector2d x0) {
  LBFGSpp::LBFGSBParam<double> prm;
  prm.epsilon = 1e-7; prm.max_iterations = 200; prm.max_linesearch = 40;
  LBFGSpp::LBFGSBSolver<double> solver(prm);
  FDProblem prob{f, 1e-6};
  Eigen::VectorXd x = clamp_box(x0), lb = kLB, ub = kUB;
  double fx = f(x(0), x(1));
  try {
    solver.minimize(prob, x, fx, lb, ub);
  } catch (const std::exception&) {
    // line-search failure at a kink of the (piecewise smooth) objective:
    // keep the last iterate, which LBFGSpp leaves in x.
    fx = f(x(0), x(1));
  }
  return {Eigen::Vector2d(x(0), x(1)), fx};
}

// Nelder-Mead on the box (points are clamped), for non-smooth objectives.
inline std::pair<Eigen::Vector2d, double> local_nelder_mead(const Counted& f, Eigen::Vector2d x0,
                                                            double step = 0.05, int maxit = 300) {
  std::array<Eigen::Vector2d, 3> S{clamp_box(x0), clamp_box(x0 + Eigen::Vector2d(step, 0)),
                                   clamp_box(x0 + Eigen::Vector2d(0, step))};
  std::array<double, 3> F{f(S[0](0), S[0](1)), f(S[1](0), S[1](1)), f(S[2](0), S[2](1))};
  auto ev = [&](const Eigen::Vector2d& x) { return f(x(0), x(1)); };
  for (int it = 0; it < maxit; ++it) {
    std::array<int, 3> o{0, 1, 2};
    std::sort(o.begin(), o.end(), [&](int a, int b) { return F[a] < F[b]; });
    const int b = o[0], m = o[1], w = o[2];
    if ((S[w] - S[b]).norm() < 1e-6) break;
    const Eigen::Vector2d c = (S[b] + S[m]) / 2;
    Eigen::Vector2d xr = clamp_box(c + (c - S[w])); double fr = ev(xr);
    if (fr < F[b]) {
      Eigen::Vector2d xe = clamp_box(c + 2 * (c - S[w])); double fe = ev(xe);
      if (fe < fr) { S[w] = xe; F[w] = fe; } else { S[w] = xr; F[w] = fr; }
    } else if (fr < F[m]) {
      S[w] = xr; F[w] = fr;
    } else {
      Eigen::Vector2d xc = clamp_box(c + 0.5 * (S[w] - c)); double fc = ev(xc);
      if (fc < F[w]) { S[w] = xc; F[w] = fc; }
      else { for (int k : {m, w}) { S[k] = S[b] + 0.5 * (S[k] - S[b]); F[k] = ev(S[k]); } }
    }
  }
  int b = 0; for (int k = 1; k < 3; ++k) if (F[k] < F[b]) b = k;
  return {S[b], F[b]};
}

inline std::pair<Eigen::Vector2d, double> local_solve(const Objective& obj, const Counted& f,
                                                      Eigen::Vector2d x0) {
  return obj.smooth() ? local_lbfgsb(f, x0) : local_nelder_mead(f, x0);
}

// One local run of a multistart search: its starting point and where it ended.
struct LocalRun { Eigen::Vector2d x0, x; double fval; };

inline Result multistart(const Objective& obj, const std::vector<Eigen::Vector2d>& starts,
                         const std::string& label, std::vector<LocalRun>* runs = nullptr) {
  auto t0 = std::chrono::steady_clock::now();
  Counted f(obj);
  Result r; r.objective = obj.name(); r.search = label; r.fval = 1e300;
  for (const auto& x0 : starts) {
    auto [x, fx] = local_solve(obj, f, x0);
    if (runs) runs->push_back({x0, x, fx});
    if (fx < r.fval) { r.fval = fx; r.t1 = x(0); r.t2 = x(1); }
  }
  r.evals = f.count();
  r.seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  return r;
}

inline std::vector<Eigen::Vector2d> starts_mcd(bool as_run, double h = kPi / 4) {
  std::vector<Eigen::Vector2d> s;
  for (double ii = -kPi; ii <= kPi - h + 1e-12; ii += h)
    for (double jj = -kPi / 2; jj <= kPi / 2 - h + 1e-12; jj += h)
      s.emplace_back(as_run ? Eigen::Vector2d((ii + h) / 2, (jj + h) / 2)   // App. A.1.1
                            : Eigen::Vector2d(ii + h / 2, jj + h / 2));     // cell center
  return s;
}

inline std::vector<Eigen::Vector2d> starts_rcsp(int m = 32, unsigned seed = 1) {
  std::mt19937 g(seed);
  std::uniform_real_distribution<double> u1(-kPi, kPi), u2(-kPi / 2, kPi / 2);
  std::vector<Eigen::Vector2d> s;
  for (int k = 0; k < m; ++k) s.emplace_back(u1(g), u2(g));
  return s;
}

// Fibonacci lattice on S^2 (Gonzalez 2010, Math. Geosci. 42:49-64).
inline std::vector<Vector3d> fibonacci_sphere(int n) {
  std::vector<Vector3d> P; P.reserve(n);
  const double ga = kPi * (3.0 - std::sqrt(5.0));
  for (int k = 0; k < n; ++k) {
    const double z = 1.0 - (2.0 * k + 1.0) / n, r = std::sqrt(std::max(0.0, 1 - z * z));
    P.emplace_back(r * std::cos(ga * k), r * std::sin(ga * k), z);
  }
  return P;
}

// Global sampling on S^2, then local refinement from the `refine` best samples.
inline Result sphere_search(const Objective& obj, int n, int refine = 8) {
  auto t0 = std::chrono::steady_clock::now();
  const auto P = fibonacci_sphere(n);
  std::vector<double> val(P.size());
#pragma omp parallel for schedule(dynamic, 16)
  for (int k = 0; k < static_cast<int>(P.size()); ++k) val[k] = obj.eval(P[k]);
  std::vector<int> idx(P.size());
  for (int k = 0; k < static_cast<int>(idx.size()); ++k) idx[k] = k;
  std::partial_sort(idx.begin(), idx.begin() + std::min<int>(refine, idx.size()), idx.end(),
                    [&](int a, int b) { return val[a] < val[b]; });
  Counted f(obj);
  Result r; r.objective = obj.name(); r.search = "sphere"; r.fval = 1e300;
  for (int k = 0; k < std::min<int>(refine, idx.size()); ++k) {
    const auto a = angles_from_direction(P[idx[k]]);
    if (val[idx[k]] < r.fval) { r.fval = val[idx[k]]; r.t1 = a(0); r.t2 = a(1); }
    auto [x, fx] = local_solve(obj, f, a);
    if (fx < r.fval) { r.fval = fx; r.t1 = x(0); r.t2 = x(1); }
  }
  r.evals = static_cast<long>(P.size()) + f.count();
  r.seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  return r;
}

// ------------------------------------------------ Ezair et al. (2015) search
// Their two-stage scheme: sample the orientations every 5 degrees
// (theta in [0,360) x phi in [-90,90): 72 x 36 = 2592 samples), then run a
// derivative-free bound-constrained method from the best `nstart` samples
// (they use 100) and keep the best stationary point. The local method is the
// coordinate-direction derivative-free line search of Lucidi & Sciandrone
// (2002), "A derivative-free algorithm for bound constrained optimization",
// Comput. Optim. Appl. 21:119-142. Parameters (gamma, theta, delta, initial
// step, tolerance) are ours: the paper does not report them.
inline std::pair<Eigen::Vector2d, double> local_dfl(const Counted& f, Eigen::Vector2d x, double step0,
                                                    double tol = 1e-4, double gamma = 1e-6,
                                                    double shrink = 0.5, double expand = 0.5,
                                                    int maxeval = 2000) {
  x = clamp_box(x);
  double fx = f(x(0), x(1));
  Eigen::Vector2d alpha(step0, step0);
  long start = f.count();
  while (alpha.maxCoeff() > tol && f.count() - start < maxeval) {
    for (int i = 0; i < 2; ++i) {
      bool moved = false;
      for (double sgn : {+1.0, -1.0}) {
        const double amax = sgn > 0 ? kUB(i) - x(i) : x(i) - kLB(i);
        double a = std::min(alpha(i), amax);
        if (a <= 1e-15) continue;
        Eigen::Vector2d y = x; y(i) += sgn * a;
        double fy = f(y(0), y(1));
        if (fy <= fx - gamma * a * a) {
          // expansion: keep enlarging the step while sufficient decrease holds
          while (true) {
            const double a2 = std::min(a / expand, amax);
            if (a2 <= a) break;
            Eigen::Vector2d z = x; z(i) += sgn * a2;
            const double fz = f(z(0), z(1));
            if (fz > fx - gamma * a2 * a2) break;
            a = a2; y = z; fy = fz;
          }
          x = y; fx = fy; alpha(i) = a; moved = true;
          break;
        }
      }
      if (!moved) alpha(i) *= shrink;
    }
  }
  return {x, fx};
}

inline Result ezair_search(const Objective& obj, int nstart = 100, double step_deg = 5.0) {
  auto t0 = std::chrono::steady_clock::now();
  const double st = step_deg * kPi / 180.0;
  const int n1 = static_cast<int>(std::lround(2 * kPi / st)), n2 = static_cast<int>(std::lround(kPi / st));
  std::vector<Eigen::Vector2d> P;
  for (int i = 0; i < n1; ++i)
    for (int j = 0; j < n2; ++j) P.emplace_back(-kPi + i * st, -kPi / 2 + j * st);
  std::vector<double> val(P.size());
#pragma omp parallel for schedule(dynamic, 8)
  for (int k = 0; k < static_cast<int>(P.size()); ++k) val[k] = obj.eval_angles(P[k](0), P[k](1));
  std::vector<int> idx(P.size());
  for (int k = 0; k < static_cast<int>(idx.size()); ++k) idx[k] = k;
  const int ns = std::min<int>(nstart, idx.size());
  std::partial_sort(idx.begin(), idx.begin() + ns, idx.end(), [&](int a, int b) { return val[a] < val[b]; });
  Counted f(obj);
  Result r; r.objective = obj.name(); r.search = "ezair"; r.fval = val[idx[0]];
  r.t1 = P[idx[0]](0); r.t2 = P[idx[0]](1);
  std::vector<std::pair<Eigen::Vector2d, double>> loc(ns);
#pragma omp parallel for schedule(dynamic, 1)
  for (int k = 0; k < ns; ++k) loc[k] = local_dfl(f, P[idx[k]], st / 2);
  for (auto& [x, fx] : loc)
    if (fx < r.fval) { r.fval = fx; r.t1 = x(0); r.t2 = x(1); }
  r.evals = static_cast<long>(P.size()) + f.count();
  r.seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  return r;
}

}  // namespace ob
