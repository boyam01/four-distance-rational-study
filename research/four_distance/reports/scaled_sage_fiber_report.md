# Sage Fiber Rank Report

## Summary
- Sage available: yes
- curves processed: 3
- Sage u points generated: 2782
- verified candidates: 4
- true_solution_count: 0
- two_good_one_bad candidates: 4
- best live/in-unit two_good_one_bad defect: 730
- 730 improvement status: no improvement over 730 found in this run.

## Scaled Mordell-Weil Search
- max_multiple: 100
- combo_bound: 20
- strategic_only: True
- sieve_primes: 2000
- candidates generated: 2782
- total candidates verified: 4
- modular sieve rejected: 4
- exact square checks: 4
- exact square success: 4
- exact square fail: 0
- true_solution_count: 0
- two_good_one_bad count: 4
- best live/in-unit defect: 730
- improved over 730: no

## Curves
| delta | fiber | method | rank | rank_bounds | torsion | combo_bound | generated | point_generation_status |
|---|---|---|---|---|---|---|---|---|
| 289/260 | B | HyperellipticCurve+Jacobian+PlaneCubic+EllipticCurve_from_cubic | 1 | (1, 3) | Torsion Subgroup isomorphic to Z/4 + Z/2 associated to the Elliptic Curve defined by y^2 + x*y + y = x^3 + x^2 - 94033660*x + 350747740940 over Rational Field |  | 200 | generated:199 |
| 289/260 | C | HyperellipticCurve+Jacobian+PlaneCubic+EllipticCurve_from_cubic | 2 | (2, 2) | Torsion Subgroup isomorphic to Z/4 associated to the Elliptic Curve defined by y^2 + x*y + y = x^3 - x^2 - 711033247*x + 6904813888519 over Rational Field | 20 | 1680 | generated:1679 |
| 289/260 | D | HyperellipticCurve+Jacobian+PlaneCubic+EllipticCurve_from_cubic | 2 | (2, 4) | Torsion Subgroup isomorphic to Z/2 associated to the Elliptic Curve defined by y^2 = x^3 - 7640631548*x + 257059113306128 over Rational Field | 20 | 1680 | generated:900 |

## Delta 289/260 Fiber Results

### B_fiber
- polynomial: 16900*u**4 - 32959*u**2 + 16900
- known basepoints: u=3/5,W=85,source=discovered_from_verified_candidate+hardcoded_seed_730+known_basepoint
- rank: 1
- rank_bounds: (1, 3)
- torsion: Torsion Subgroup isomorphic to Z/4 + Z/2 associated to the Elliptic Curve defined by y^2 + x*y + y = x^3 + x^2 - 94033660*x + 350747740940 over Rational Field
- generators: [(-1693/4 : 5000709/8 : 1)]
- combo_bound: n/a
- combinations checked: 200
- generated u count: 200
- best two_good_one_bad from B orbit: u=3/5 defects=(1,1,730) remaining=730

### C_fiber
- polynomial: 16900*u**4 + 75140*u**3 + 117321*u**2 - 75140*u + 16900
- known basepoints: u=3/5,W=901/5,source=discovered_from_verified_candidate+hardcoded_seed_730+known_basepoint;u=15/26,W=170,source=discovered_from_verified_candidate
- rank: 2
- rank_bounds: (2, 2)
- torsion: Torsion Subgroup isomorphic to Z/4 associated to the Elliptic Curve defined by y^2 + x*y + y = x^3 - x^2 - 711033247*x + 6904813888519 over Rational Field
- generators: [(12377 : 10386 : 1), (2679613/144 : 574859533/1728 : 1)]
- combo_bound: 20
- combinations checked: 1680
- generated u count: 1681
- best two_good_one_bad from C orbit: u=15/26 defects=(730,1,1) remaining=730

### D_fiber
- polynomial: 2*(8450*u**4 + 37570*u**3 + 25281*u**2 - 37570*u + 8450)
- known basepoints: u=15/26,W=2125/26,source=discovered_from_verified_candidate+hardcoded_from_C_orbit
- rank: 2
- rank_bounds: (2, 4)
- torsion: Torsion Subgroup isomorphic to Z/2 associated to the Elliptic Curve defined by y^2 = x^3 - 7640631548*x + 257059113306128 over Rational Field
- generators: [(49813 : 243049 : 1), (52006 : 597584 : 1)]
- combo_bound: 20
- combinations checked: 1680
- generated u count: 901
- best two_good_one_bad from D orbit: u=15/26 defects=(730,1,1) remaining=730

## Two-good-one-bad chain
1. u=3/5 defects=(1,1,730) P=(416/867,260/289) remaining=730 mcc_live=True point_in_unit=True
2. u=15/26 defects=(730,1,1) P=(451/867,260/289) remaining=730 mcc_live=True point_in_unit=True

## Rank Certification
### B_fiber
- rank_bounds before/after: (1, 3)
- rank certified: no
- generators used: [(-1693/4 : 5000709/8 : 1)]
- saturation status: ([(-1693/4 : 5000709/8 : 1)], 1, 1.45658849495839)
- extra generators found: no
### D_fiber
- rank_bounds before/after: (2, 4)
- rank certified: no
- generators used: [(49813 : 243049 : 1), (52006 : 597584 : 1)]
- saturation status: ([(49813 : 243049 : 1), (52006 : 597584 : 1)], 1, 8.96917427461178)
- extra generators found: no

## Improvement Status
- true_solution_count: 0
- best live/in-unit two_good_one_bad defect: 730
- improved over 730: no

## Best Verified Candidates
| delta | fiber | u | defects | two_good_one_bad | mcc_live | point_in_unit | notes |
|---|---|---|---|---|---|---|---|
| 289/260 | B | 3/5 | (1,1,730) | True | True | True | near_miss:(1-x)^2+(1-y)^2;sieve:D_failed_mod_13 |
| 289/260 | C | 15/26 | (730,1,1) | True | True | True | near_miss:x^2+(1-y)^2;sieve:B_failed_mod_13 |
| 289/260 | C | 3/5 | (1,1,730) | True | True | True | near_miss:(1-x)^2+(1-y)^2;sieve:D_failed_mod_13 |
| 289/260 | D | 15/26 | (730,1,1) | True | True | True | near_miss:x^2+(1-y)^2;sieve:B_failed_mod_13 |

## Scaled Attempt Notes
- Completed checkpoint: max_multiple=100, combo_bound=20, strategic_only=True, sieve_primes=2000.
- Attempted level 1: max_multiple=500, combo_bound=50, strategic_only=True, sieve_primes=2000. This did not complete within the 15 minute execution window and was stopped.
- Attempted reduced level 1: max_multiple=500, combo_bound=30. This also did not complete within the 15 minute execution window and was stopped.
- Attempted reduced level 1: max_multiple=500, combo_bound=20. This also did not complete within the 15 minute execution window and was stopped.
- Therefore no negative conclusion is claimed for max_multiple=500. The next implementation step is checkpointed/streaming generation by fiber and coefficient range, or a faster inverse-map path.

## Conclusion
no true solution found in this finite Mordell-Weil/fiber run.
This is not a proof of non-existence.
