# Delta 289/260 Case Study

## Status

No true four-distance solution was found in this finite Mordell-Weil/fiber run.
This is not a proof of non-existence.

## Seed

The live seed is:

```text
delta = 289/260
u = 3/5
A = 15/8
B = 87/416
C = 451/780
D = 451/87
defects = (1,1,730)
P = (416/867,260/289)
```

Its mirror chain point is:

```text
u = 15/26
A = 780/451
B = 87/451
C = 8/15
D = 416/87
defects = (730,1,1)
P = (451/867,260/289)
```

## Fibers

```text
B_fiber:
W^2 = 16900*u^4 - 32959*u^2 + 16900

C_fiber:
W^2 = 16900*u^4 + 75140*u^3 + 117321*u^2 - 75140*u + 16900

D_fiber:
W^2 = 2*(8450*u^4 + 37570*u^3 + 25281*u^2 - 37570*u + 8450)
```

## Sage Rank Data

```text
B_fiber:
rank = 1
rank_bounds = (1,3)
rank certified = no
torsion = Z/4 + Z/2

C_fiber:
rank = 2
rank_bounds = (2,2)
rank certified = yes
torsion = Z/4

D_fiber:
rank = 2
rank_bounds = (2,4)
rank certified = no
torsion = Z/2
basepoint = u=15/26, W=2125/26
```

## Intersection Audit

At the completed checkpoint:

```text
max_multiple = 100
combo_bound = 20
```

the exact generated u-sets satisfy:

```text
|U_B| = 200
|U_C| = 1680
|U_D| = 901

U_B ∩ U_C = {3/5}
U_C ∩ U_D = {15/26}
U_B ∩ U_D = empty
U_B ∩ U_C ∩ U_D = empty
```

Therefore no generated `u` in this finite run satisfies `B,C,D in S`.

## Symmetry Warning

The two chain points are mirror points:

```text
416/867 + 451/867 = 1
```

Thus the transition

```text
(1,1,730) <-> (730,1,1)
```

is likely an `x -> 1-x` structural symmetry of this slice.  It should not be
overinterpreted as strong near-solution evidence.

## Larger Attempt Note

The `max_multiple=500` family of attempts did not complete under the available
execution window.  No negative conclusion is claimed for those larger settings.

## Conclusion

No true solution was found in this finite delta `289/260` Sage/Mordell-Weil
fiber run.  This is exact computed evidence for the recorded generated points,
not a proof of non-existence.
