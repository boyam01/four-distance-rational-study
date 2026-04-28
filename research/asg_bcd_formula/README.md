# ASG/BCD Formula Pack

This directory is a small public extraction of the exact-arithmetic formulas
used by the four-distance study.  It is research-only and contains no trading
runtime, no exchange integration, no credentials, no order logic, and no
private telemetry.

## Core Objects

The rational Pythagorean slope set is:

```text
S = { alpha=a/b in Q : a^2+b^2 is a square }
```

The Love-style square relation is:

```text
A*C = B*D = A+B-1
```

The fixed-delta fiber parametrization is:

```text
A = 2u/(1-u^2)
B = A*(delta-1)
C = delta - 1/A
D = (A*delta - 1)/(A*(delta-1))
P = (1/(A*delta), 1/delta)
```

The three B/C/D conditions are:

```text
B in S
C in S
D in S
```

Each condition has a squarefree defect:

```text
defect(alpha) = squarefree_part(num(alpha)^2 + den(alpha)^2)
```

`defect=1` means the condition passes.

## Known Exact Examples

The live defect 730 seed:

```text
delta=289/260
u=3/5
A=15/8
B=87/416
C=451/780
D=451/87
defects=(1,1,730)
P=(416/867,260/289)
```

The symmetry partner on the same delta slice:

```text
delta=289/260
u=15/26
A=780/451
B=87/451
C=8/15
D=416/87
defects=(730,1,1)
P=(451/867,260/289)
```

The defect 17 seed:

```text
delta=13/6
u=1/4
A=8/15
B=28/45
C=7/24
D=1/4
defects=(1,1,17)
P=(45/52,6/13)
```

## Use

```python
from fractions import Fraction

from research.asg_bcd_formula import bcd_from_u_delta

point = bcd_from_u_delta(Fraction(3, 5), Fraction(289, 260))
print(point.as_dict())
```

Run the tests:

```bash
pytest research/asg_bcd_formula/tests -q
```

## Non-Claims

This package does not solve the unit-square four-distance problem.  It only
exports exact formulas and known finite near-miss examples for reuse.
