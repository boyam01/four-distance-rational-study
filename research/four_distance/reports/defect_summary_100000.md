# Four Distance K2,2 Seed Scan Report

## Executive Summary
- Found true four-distance solution: no
- Search LIMIT: N <= 100000
- Primitive oriented three-distance seed count: 134
- Distinct defect count: 67
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
| 5617 | 2 | 7800 | N=7800 (p,q,r,s)=(693,2924,7107,4876) | 2 |
| 5713 | 2 | 996 | N=996 (p,q,r,s)=(520,765,476,231) | 2 |
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
| 151505 | 2 | 10952 | N=10952 (p,q,r,s)=(396,1155,10556,9797) | 0 |
| 235418 | 2 | 21853 | N=21853 (p,q,r,s)=(5040,11220,16813,10633) | 0 |
| 239857 | 2 | 58956 | N=58956 (p,q,r,s)=(1157,51480,57799,7476) | 2 |
| 379738 | 2 | 14739 | N=14739 (p,q,r,s)=(5040,10780,9699,3959) | 2 |
| 506417 | 2 | 11492 | N=11492 (p,q,r,s)=(3135,7524,8357,3968) | 0 |
| 507809 | 2 | 740 | N=740 (p,q,r,s)=(168,315,572,425) | 0 |
| 871690 | 2 | 1443 | N=1443 (p,q,r,s)=(644,960,799,483) | 2 |
| 1432817 | 2 | 26588 | N=26588 (p,q,r,s)=(8856,16605,17732,9983) | 0 |
| 1517266 | 2 | 2145 | N=2145 (p,q,r,s)=(920,2016,1225,129) | 2 |
| 2202481 | 2 | 20280 | N=20280 (p,q,r,s)=(4795,8772,15485,11508) | 2 |
| 2565721 | 2 | 11484 | N=11484 (p,q,r,s)=(3640,9867,7844,1617) | 2 |
| 3771226 | 2 | 27189 | N=27189 (p,q,r,s)=(17424,17732,9765,9457) | 2 |
| 4521217 | 2 | 8400 | N=8400 (p,q,r,s)=(164,1677,8236,6723) | 2 |
| 6844114 | 2 | 6015 | N=6015 (p,q,r,s)=(3432,5600,2583,415) | 2 |
| 7110353 | 2 | 77500 | N=77500 (p,q,r,s)=(15477,53064,62023,24436) | 0 |
| 12683378 | 2 | 60401 | N=60401 (p,q,r,s)=(12480,23400,47921,37001) | 0 |
| 26085121 | 2 | 34500 | N=34500 (p,q,r,s)=(10153,26796,24347,7704) | 2 |
| 26423905 | 2 | 90168 | N=90168 (p,q,r,s)=(2920,85239,87248,4929) | 2 |
| 29059546 | 2 | 40365 | N=40365 (p,q,r,s)=(2740,37488,37625,2877) | 2 |
| 40555441 | 2 | 6240 | N=6240 (p,q,r,s)=(711,3080,5529,3160) | 2 |
| 53197258 | 2 | 11997 | N=11997 (p,q,r,s)=(4704,11900,7293,97) | 2 |
| 55141697 | 2 | 43700 | N=43700 (p,q,r,s)=(7524,35343,36176,8357) | 0 |
| 60608353 | 2 | 11352 | N=11352 (p,q,r,s)=(4935,6944,6417,4408) | 2 |
| 68463994 | 2 | 9165 | N=9165 (p,q,r,s)=(1540,5952,7625,3213) | 2 |
| 72781921 | 2 | 49500 | N=49500 (p,q,r,s)=(6844,49383,42656,117) | 2 |

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
- Live seed count: 78

## Slope Closure Analysis

Known seeds satisfy `A*C = B*D = A+B-1`; their obstruction is exactly `D not in S`.

- defect 17: A=8/15, C=7/24 -> B=28/45, D=1/4, D_in_S=False, defect=17
- defect 730: A=15/8, C=451/780 -> B=87/416, D=451/87, D_in_S=False, defect=730

Best low-defect D candidates from this K2,2 scan are the top rows in the defect table above.

## Local 730 Search

Run `python research/four_distance/local_730_search.py --height H --window-num 1 --window-den 100` for the real-near and 3-adic-compatible candidate tables.
This K2,2 report does not treat a local-search miss as a theorem.

## Elliptic Prep

Run `python research/four_distance/elliptic_prep.py --delta 289/260` to generate fixed-delta cleared-denominator curve equations.
Sage availability is optional and skipped without failing.

## Conclusion

No true four-distance solution was found up to N <= 100000 in this exact integer scan.
This is computed evidence only; it is not a proof that no solution exists beyond the searched limit.
