# Fiber Secant Search Report

## Summary
- Sage available? no
- deltas tested: 289/260, 13/6, 289/29, 867/451, 867/416, 332/77, 249/119, 332/255, 249/130, 3125/493, 9375/2303, 3125/2632, 9375/7072, 65/49, 39/11, 65/16, 39/28, 12675/11891, 4225/1029, 12675/784, 4225/3196
- fibers built: 63
- ranks/rank_bounds if available: skipped
- candidates generated: 252
- true solutions found: 0

## Delta 289/260 Analysis
### B_fiber
- polynomial: `16900*u**4 - 32959*u**2 + 16900`
- known rational basepoints: u=3/5, W=85
- sage: Sage unavailable; rank/generator search skipped.
### C_fiber
- polynomial: `16900*u**4 + 75140*u**3 + 117321*u**2 - 75140*u + 16900`
- known rational basepoints: u=3/5, W=901/5
- sage: Sage unavailable; rank/generator search skipped.
### D_fiber
- polynomial: `2*(8450*u**4 + 37570*u**3 + 25281*u**2 - 37570*u + 8450)`
- known rational basepoints: none
- sage: Sage unavailable; rank/generator search skipped.

u0=3/5 status:
- A=15/8, B=87/416, C=451/780, D=451/87
- defects: B=1, C=1, D=730
- P=(416/867,260/289)
- generated u candidates: 11
- single-defect diagnostic improvements: 3
- two-good-one-bad improvements over 730: 0

## One-sided Fiber Analysis
| delta | u | source | defect_B | defect_C | defect_D | score | mcc_live | point_in_unit |
|---|---|---|---:|---:|---:|---:|---|---|
| 13/6 | 3/4 | C_sample | 17 | 1 | 1 | 17 | False | True |
| 13/6 | -4/3 | C_sample | 17 | 1 | 1 | 17 | False | True |
| 289/260 | 15/26 | C_sample | 730 | 1 | 1 | 730 | True | True |
| 867/416 | 13/16 | C_sample | 730 | 1 | 1 | 730 | True | True |
| 289/29 | 3/29 | B_sample | 1 | 730 | 1 | 730 | True | True |
| 867/416 | -16/13 | C_sample | 730 | 1 | 1 | 730 | True | True |
| 289/260 | -26/15 | C_sample | 730 | 1 | 1 | 730 | True | True |
| 289/29 | -29/3 | B_sample | 1 | 730 | 1 | 730 | True | True |
| 332/255 | 5/9 | C_sample | 5713 | 1 | 1 | 5713 | True | True |
| 249/130 | 13/20 | C_sample | 5713 | 1 | 1 | 5713 | True | True |
| 249/119 | 2/7 | B_sample | 1 | 5713 | 1 | 5713 | True | True |
| 249/130 | -20/13 | C_sample | 5713 | 1 | 1 | 5713 | True | True |
| 332/255 | -9/5 | C_sample | 5713 | 1 | 1 | 5713 | True | True |
| 249/119 | -7/2 | B_sample | 1 | 5713 | 1 | 5713 | True | True |
| 3125/2632 | 3/4 | C_sample | 11986 | 1 | 1 | 11986 | True | True |
| 9375/7072 | 13/16 | C_sample | 11986 | 1 | 1 | 11986 | True | True |
| 9375/2303 | 1/7 | B_sample | 1 | 11986 | 1 | 11986 | True | True |
| 3125/493 | 3/29 | B_sample | 1 | 11986 | 1 | 11986 | True | True |
| 9375/7072 | -16/13 | C_sample | 11986 | 1 | 1 | 11986 | True | True |
| 3125/2632 | -4/3 | C_sample | 11986 | 1 | 1 | 11986 | True | True |

## Conclusion
no true solution found in this finite fiber/secant run.
The secant fallback is experimental and is not a complete group-law or Mordell-Weil computation.
