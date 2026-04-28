# Reproducibility

This artifact is designed to be rerun from the repository root.

## Runtime

Observed local runtime:

```text
Windows Python: 3.10.10
WSL Python: 3.12.3
Sage conda environment Python: 3.11.15
SageMath: 10.7
WSL: Ubuntu on WSL2
```

Sage is expected to be available as `sage` on `PATH`.  On the workstation used
for the recorded run, Sage lives in the WSL Miniforge conda environment named
`sage`.

Example WSL activation:

```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate sage
cd "/mnt/c/Users/ians0/Documents/New project"
```

## Tests

```bash
pytest research/four_distance/tests -q
```

Recorded checkpoint:

```text
37 passed
```

All tests should pass; the exact count may change as new tests are added.

## Delta 289/260 Case Study

```bash
sage research/four_distance/sage_fiber_rank.sage --delta 289/260 --all --max-multiple 100 --combo-bound 20 --strategic-only --sieve-primes 2000
python research/four_distance/sage_fiber_bridge.py --from-sage-csv research/four_distance/data/sage_fiber_points.csv --strategic-only --sieve-primes 2000
python research/four_distance/fiber_intersection_search.py --delta 289/260
```

Expected high-level result:

```text
true_solution_count = 0
U_B ∩ U_C = {3/5}
U_C ∩ U_D = {15/26}
U_B ∩ U_D = empty
triple intersection = empty
```

## Lightweight Delta Scan

```bash
python research/four_distance/delta_scan_lite.py --max-deltas 10 --max-multiple 50 --combo-bound 10 --sieve-primes 1000
```

Outputs:

- `research/four_distance/data/delta_scan_lite_summary.csv`
- `research/four_distance/reports/delta_scan_lite_report.md`

The scan is intentionally small.  It tests whether sparse fiber intersections
are common across a few selected deltas; it is not a global search.

## Exact Arithmetic Policy

All core mathematical predicates use exact arithmetic.  The code uses
`math.isqrt`, Python `int`, and `fractions.Fraction`.  Modular residue sieves
are only rejection filters; any positive squarehood result must still pass an
exact integer square test.

## What Negative Output Means

When a report says no true solution was found, it means no solution was found in
that finite run and under that run's generation policy.  It does not prove that
the unit-square four-distance problem has no solution.
