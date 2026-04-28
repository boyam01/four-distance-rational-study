# Unit Square Four-Distance Exact Research Module

This module studies the unit-square four-distance rationality problem with
exact arithmetic.  It is a computation harness and research artifact, not a
proof of non-existence.

## Problem

For a point

```text
P = (p/N, q/N),   r = N-p,   s = N-q
```

the four distances to `(0,0)`, `(1,0)`, `(0,1)`, `(1,1)` are rational exactly
when all four integer quantities are squares:

```text
p^2 + q^2
r^2 + q^2
p^2 + s^2
r^2 + s^2
```

A three-distance seed requires the first three expressions to be squares.  If
the fourth is not a square, the squarefree part of the fourth expression is
recorded as the defect.

## Framework

The module implements four complementary exact-arithmetic workflows.

- `k22_search.py`: scans K2,2 Pythagorean-leg seeds using adjacency sets.
- `slope_tools.py`: verifies exact slopes, defects, certificates, and the
  McCloskey 3-adic gate.
- `reverse_closure_search.py` and `reverse_nearmiss.py`: audit Love-style
  closure from slope pairs and near-misses.
- `sage_fiber_rank.sage`, `sage_fiber_bridge.py`, and
  `fiber_intersection_search.py`: build fixed-delta quartic fibers, run Sage
  rank/generator searches, bridge generated points back into exact Python
  verification, and compute `U_B`, `U_C`, `U_D` intersections.

The slope set is

```text
S = { a/b in Q : a^2 + b^2 is a square }.
```

The Love-style relation used here is

```text
A*C = B*D = A+B-1.
```

For a fixed `delta`, the fiber parametrization is

```text
A = 2u/(1-u^2)
B = A*(delta-1)
C = delta - 1/A
D = (A*delta - 1)/(A*(delta-1))
P = (1/(A*delta), 1/delta)
```

A true four-distance solution on a fixed delta slice requires `B,C,D in S`
because `A in S` is built into the parametrization.

## Exact Arithmetic Guarantees

- Squarehood is checked with Python `int` and `math.isqrt`.
- Rational arithmetic uses `fractions.Fraction`.
- Defects are integer squarefree parts; large candidates use modular sieve and
  bounded small-defect checks before full factorization.
- No floating-point comparisons are used for squarehood, rationality, defects,
  or 3-adic valuations.
- The McCloskey 3-adic gate is treated only as a necessary condition for true
  solutions and as a live/dead label for seeds.  It is not used as a proof that
  a three-distance seed can or cannot complete.

## Known Seeds

Defect 17 seed:

```text
N=52, p=45, q=24, r=7, s=28
P=(45/52,6/13)
45^2 + 24^2 = 51^2
7^2 + 24^2 = 25^2
45^2 + 28^2 = 53^2
7^2 + 28^2 = 833 = 49*17
McCloskey label: dead
```

Defect 730 seed:

```text
N=867, p=416, q=780, r=451, s=87
P=(416/867,260/289)
416^2 + 780^2 = 884^2
451^2 + 780^2 = 901^2
416^2 + 87^2 = 425^2
451^2 + 87^2 = 210970 = 17^2*730
McCloskey label: live
```

## Delta 289/260 Case Study

For `delta=289/260`, the three quartic fibers are:

```text
B_fiber: W^2 = 16900*u^4 - 32959*u^2 + 16900
C_fiber: W^2 = 16900*u^4 + 75140*u^3 + 117321*u^2 - 75140*u + 16900
D_fiber: W^2 = 2*(8450*u^4 + 37570*u^3 + 25281*u^2 - 37570*u + 8450)
```

Recorded Sage results:

```text
B rank=1, rank_bounds=(1,3), rank certified=no
C rank=2, rank_bounds=(2,2), rank certified=yes
D rank=2, rank_bounds=(2,4), rank certified=no
```

At the completed `max_multiple=100`, `combo_bound=20` checkpoint:

```text
|U_B| = 200
|U_C| = 1680
|U_D| = 901
U_B ∩ U_C = {3/5}
U_C ∩ U_D = {15/26}
U_B ∩ U_D = empty
U_B ∩ U_C ∩ U_D = empty
```

The two chain points are:

```text
u=3/5, defects=(1,1,730), P=(416/867,260/289)
u=15/26, defects=(730,1,1), P=(451/867,260/289)
```

These are mirror points under `x -> 1-x` because

```text
416/867 + 451/867 = 1.
```

The `(1,1,730) <-> (730,1,1)` chain is therefore likely a structural symmetry
of this delta slice.  It should not be overinterpreted as evidence that the
slice is close to a true solution.

## Reproducibility Commands

Core tests:

```bash
pytest research/four_distance/tests -q
```

Delta `289/260` Sage/fiber checkpoint:

```bash
sage research/four_distance/sage_fiber_rank.sage --delta 289/260 --all --max-multiple 100 --combo-bound 20 --strategic-only --sieve-primes 2000
python research/four_distance/sage_fiber_bridge.py --from-sage-csv research/four_distance/data/sage_fiber_points.csv --strategic-only --sieve-primes 2000
python research/four_distance/fiber_intersection_search.py --delta 289/260
```

Lightweight multi-delta scan:

```bash
python research/four_distance/delta_scan_lite.py --max-deltas 10 --max-multiple 50 --combo-bound 10 --sieve-primes 1000
```

## Current Interpretation

No true solution was found in the recorded finite computations.  This is not a
proof of non-existence.  It is exact computed evidence for the tested bounds,
orientations, generated Mordell-Weil points, and selected delta slices.
