# Delta Scan Lite Report

## Summary
- deltas tested: 10
- Sage run: yes
- Sage message: wrote research/four_distance/data/delta_scan_lite_curves.csv; wrote research/four_distance/data/delta_scan_lite_points.csv
- max_multiple: 50
- combo_bound: 10
- sieve_primes: 1000
- true solutions found: none
- deltas with triple intersections: none
- deltas with dense pairwise intersections: none
- deltas with improvement over seed defect: none
- deltas showing same sparse pattern as 289/260: 13/6, 289/260, 867/416, 289/29, 332/255, 249/130, 249/119, 3125/493, 9375/2303, 3125/2632

## Per Delta Table

| delta | base fibers | ranks B/C/D | |UB| | |UC| | |UD| | BC | BD | CD | BCD | true | best live defect | improved | symmetry | notes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 13/6 | B+C+D | B:1 (1, 1); C:2 (2, 2); D:2 (2, 2) | 106 | 446 | 439 | 2 | 1 | 2 | 0 | 0 |  | False | True | ok |
| 289/260 | B+C+D | B:1 (1, 3); C:2 (2, 2); D:2 (2, 4) | 106 | 442 | 252 | 2 | 0 | 2 | 0 | 0 | 730 | False | True | ok |
| 867/416 | B+C+D | B:1 (1, 1); C:1 (1, 3); D:3 (3, 3) | 105 | 102 | 439 | 2 | 0 | 2 | 0 | 0 | 730 | False | True | ok |
| 289/29 | B+D | B:1 (1, 3); C: unavailable:'HyperellipticJacobian_generic_with_category' object has no attribute 'rank_bounds'; D:2 (2, 4) | 106 | 0 | 439 | 0 | 2 | 0 | 0 | 0 | 730 | False | False | ok |
| 332/255 | B+C+D | B:1 (1, 1); C:1 (1, 3); D:2 (2, 2) | 105 | 102 | 252 | 2 | 0 | 2 | 0 | 0 | 5713 | False | True | ok |
| 249/130 | B+C+D | B:2 (2, 2); C:2 (2, 2); D:2 (2, 2) | 448 | 442 | 251 | 2 | 0 | 2 | 0 | 0 | 5713 | False | True | ok |
| 249/119 | B+D | B:2 (2, 2); C: unavailable:'HyperellipticJacobian_generic_with_category' object has no attribute 'rank_bounds'; D:2 (2, 2) | 451 | 0 | 439 | 0 | 2 | 0 | 0 | 0 | 5713 | False | False | ok |
| 3125/493 | B+D | B:3 (3, 3); C: unavailable:'HyperellipticJacobian_generic_with_category' object has no attribute 'rank_bounds'; D:3 (3, 3) | 447 | 0 | 442 | 0 | 2 | 0 | 0 | 0 | 11986 | False | False | ok |
| 9375/2303 | B+D | B:1 (1, 3); C: unavailable:'HyperellipticJacobian_generic_with_category' object has no attribute 'rank_bounds'; D:4 (4, 4) | 101 | 0 | 241 | 0 | 2 | 0 | 0 | 0 | 11986 | False | False | ok |
| 3125/2632 | B+C+D | B:3 (3, 3); C:1 (1, 3); D:3 (3, 3) | 446 | 101 | 442 | 0 | 0 | 2 | 0 | 0 | 11986 | False | False | ok |

## Interpretation
No true solution found in this finite lightweight delta scan.
This is not a proof of non-existence.
The completed rows suggest the sparse intersection pattern is not unique to delta=289/260.
