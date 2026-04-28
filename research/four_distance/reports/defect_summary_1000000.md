# Four Distance K2,2 Seed Scan Report

## Executive Summary
- Found true four-distance solution: no
- Search LIMIT: N <= 1000000
- Primitive oriented three-distance seed count: 432
- Distinct defect count: 216
- Minimum defect: 17
- Minimum defect seed: N=52 (p,q,r,s)=(24,45,28,7)
- Minimum live defect: 730
- Minimum live defect seed: N=867 (p,q,r,s)=(416,780,451,87)
- Minimum N live seed: N=195 (p,q,r,s)=(48,140,147,55)
- 17 seed status: present; live=False
- 730 seed status: present; live=True

## Known Seed Verification

### Seed A defect 17
```text
N=52, p=45, q=24, r=7, s=28
P=(45/52,6/13)
p^2+q^2=2601=51^2
r^2+q^2=625=25^2
p^2+s^2=2809=53^2
r^2+s^2=833=7*sqrt(17)
defect=17
slopes:
A=8/15, B=28/45, C=7/24, D=1/4
delta=13/6
A_in_S=True, B_in_S=True, C_in_S=True, D_in_S=False
A*C == B*D == A+B-1: True
B == A*(delta-1), P from delta: True
point_from_delta=(45/52,6/13)
McCloskey 3-adic gate:
x=45/52, yc=-1/26, v3_x=2, v3_yc=0, live=False
```

### Seed B defect 730
```text
N=867, p=416, q=780, r=451, s=87
P=(416/867,260/289)
p^2+q^2=781456=884^2
r^2+q^2=811801=901^2
p^2+s^2=180625=425^2
r^2+s^2=210970=17*sqrt(730)
defect=730
slopes:
A=15/8, B=87/416, C=451/780, D=451/87
delta=289/260
A_in_S=True, B_in_S=True, C_in_S=True, D_in_S=False
A*C == B*D == A+B-1: True
B == A*(delta-1), P from delta: True
point_from_delta=(416/867,260/289)
McCloskey 3-adic gate:
x=416/867, yc=231/578, v3_x=-1, v3_yc=1, live=True
```

## Defect Distribution

| defect | count | min_N | example seed | mcc_live_count |
|---:|---:|---:|---|---:|
| 17 | 2 | 52 | N=52 (p,q,r,s)=(24,45,28,7) | 0 |
| 730 | 2 | 867 | N=867 (p,q,r,s)=(416,780,451,87) | 2 |
| 1745 | 2 | 306916 | N=306916 (p,q,r,s)=(66585,145908,240331,161008) | 0 |
| 2753 | 2 | 329476 | N=329476 (p,q,r,s)=(51867,230520,277609,98956) | 0 |
| 5617 | 2 | 7800 | N=7800 (p,q,r,s)=(693,2924,7107,4876) | 2 |
| 5713 | 2 | 996 | N=996 (p,q,r,s)=(520,765,476,231) | 2 |
| 9193 | 2 | 306456 | N=306456 (p,q,r,s)=(35535,41128,270921,265328) | 2 |
| 10193 | 2 | 700 | N=700 (p,q,r,s)=(297,396,403,304) | 0 |
| 11698 | 2 | 20625 | N=20625 (p,q,r,s)=(1704,20128,18921,497) | 2 |
| 11986 | 2 | 9375 | N=9375 (p,q,r,s)=(7072,7896,2303,1479) | 2 |
| 12017 | 2 | 44944 | N=44944 (p,q,r,s)=(4365,42228,40579,2716) | 0 |
| 14177 | 2 | 3364 | N=3364 (p,q,r,s)=(900,945,2464,2419) | 0 |
| 18922 | 2 | 12675 | N=12675 (p,q,r,s)=(4884,8288,7791,4387) | 2 |
| 24634 | 2 | 195 | N=195 (p,q,r,s)=(48,140,147,55) | 2 |
| 35722 | 2 | 12675 | N=12675 (p,q,r,s)=(784,9588,11891,3087) | 2 |
| 51137 | 2 | 22472 | N=22472 (p,q,r,s)=(13260,14805,9212,7667) | 0 |
| 60314 | 2 | 21125 | N=21125 (p,q,r,s)=(7524,12768,13601,8357) | 0 |
| 69386 | 2 | 21125 | N=21125 (p,q,r,s)=(4416,17388,16709,3737) | 0 |
| 120929 | 2 | 420500 | N=420500 (p,q,r,s)=(67896,404547,352604,15953) | 0 |
| 143546 | 2 | 171125 | N=171125 (p,q,r,s)=(103584,152388,67541,18737) | 0 |
| 151505 | 2 | 10952 | N=10952 (p,q,r,s)=(396,1155,10556,9797) | 0 |
| 211553 | 2 | 399748 | N=399748 (p,q,r,s)=(46215,231756,353533,167992) | 0 |
| 235418 | 2 | 21853 | N=21853 (p,q,r,s)=(5040,11220,16813,10633) | 0 |
| 239857 | 2 | 58956 | N=58956 (p,q,r,s)=(1157,51480,57799,7476) | 2 |
| 326993 | 2 | 174824 | N=174824 (p,q,r,s)=(51120,66975,123704,107849) | 0 |
| 379738 | 2 | 14739 | N=14739 (p,q,r,s)=(5040,10780,9699,3959) | 2 |
| 506417 | 2 | 11492 | N=11492 (p,q,r,s)=(3135,7524,8357,3968) | 0 |
| 507809 | 2 | 740 | N=740 (p,q,r,s)=(168,315,572,425) | 0 |
| 737281 | 2 | 907740 | N=907740 (p,q,r,s)=(449995,522192,457745,385548) | 2 |
| 871690 | 2 | 1443 | N=1443 (p,q,r,s)=(644,960,799,483) | 2 |
| 1432817 | 2 | 26588 | N=26588 (p,q,r,s)=(8856,16605,17732,9983) | 0 |
| 1517266 | 2 | 2145 | N=2145 (p,q,r,s)=(920,2016,1225,129) | 2 |
| 1826897 | 2 | 613832 | N=613832 (p,q,r,s)=(246675,540540,367157,73292) | 0 |
| 1871857 | 2 | 504600 | N=504600 (p,q,r,s)=(313313,452016,191287,52584) | 2 |
| 1911073 | 2 | 181548 | N=181548 (p,q,r,s)=(133480,151515,48068,30033) | 2 |
| 1921298 | 2 | 239575 | N=239575 (p,q,r,s)=(47424,69768,192151,169807) | 0 |
| 2202481 | 2 | 20280 | N=20280 (p,q,r,s)=(4795,8772,15485,11508) | 2 |
| 2565721 | 2 | 11484 | N=11484 (p,q,r,s)=(3640,9867,7844,1617) | 2 |
| 3529633 | 2 | 969252 | N=969252 (p,q,r,s)=(554775,714340,414477,254912) | 2 |
| 3596905 | 2 | 301752 | N=301752 (p,q,r,s)=(19680,39721,282072,262031) | 2 |

Target low defects:

- defect=2: absent
- defect=3: absent
- defect=5: absent
- defect=6: absent
- defect=7: absent
- defect=10: absent
- defect=13: absent
- defect=17: present, count=2
- defect=730: present, count=2

## McCloskey Gate Analysis

The gate `v3(x) < 0 or v3(yc) < 0` is a necessary condition for a true four-distance solution in the centered rectangle model.
For three-distance seeds it is only a live/dead computational label, not a proof of existence or non-existence.
- Seed 17 is dead under this label.
- Seed 730 is live under this label.
- Live seed count: 270

## Slope Closure Analysis

Known seeds satisfy `A*C = B*D = A+B-1`; their obstruction is exactly `D not in S`.

- defect 17: A=8/15, C=7/24 -> B=28/45, D=1/4, D_in_S=False, defect=17
- defect 730: A=15/8, C=451/780 -> B=87/416, D=451/87, D_in_S=False, defect=730

Best low-defect D candidates from this K2,2 scan are the top rows in the defect table above.

Exact slope closure scan artifact:

- CSV: `research/four_distance/data/slope_candidates_H1000.csv`
- Height: 1000
- S slopes generated: 358
- Closure candidates recorded: 29
- Found D in S: no
- Best defects in slope closure: 17, 730, 5713, 10193, 11986

## Local 730 Search

Artifacts:

- CSV: `research/four_distance/data/local_730_candidates_H1000.csv`
- Report: `research/four_distance/reports/local_730_report_H1000.md`
- Height: 1000
- Window: 1/100
- S slopes generated: 358
- Real-near A count: 1
- Real-near C count: 3
- Candidate rows before top cut: 18
- Found D in S: no
- Better-than-730 non-solution candidate: no

Top real-near result is exactly the known live seed:

```text
A=15/8, C=451/780, B=87/416, D=451/87, defect_D=730, N=867, p=416, q=780
```

This local-search miss is not a theorem.

## Elliptic Prep

Artifact:

- Report: `research/four_distance/reports/elliptic_prep_13-6_289-260_2-1_3-1_1-2_3-2_4-3_5-4.md`
- Sage status: Sage not found; genus/rank attempts skipped.

For delta `13/6`, cleared denominator equations include:

```text
C in S: W_C^2 = 9*u^4 + 78*u^3 + 187*u^2 - 78*u + 9
B in S: W_B^2 = 9*u^4 + 31*u^2 + 9
D in S: W_D^2 = 9*u^4 + 78*u^3 + 200*u^2 - 78*u + 9
```

For delta `289/260`, cleared denominator equations include:

```text
C in S: W_C^2 = 16900*u^4 + 75140*u^3 + 117321*u^2 - 75140*u + 16900
B in S: W_B^2 = 16900*u^4 - 32959*u^2 + 16900
D in S: W_D^2 = 2*(8450*u^4 + 37570*u^3 + 25281*u^2 - 37570*u + 8450)
```

## Conclusion

No true four-distance solution was found up to N <= 1000000 in this exact integer scan.
This is computed evidence only; it is not a proof that no solution exists beyond the searched limit.
