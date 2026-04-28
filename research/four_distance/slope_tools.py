#!/usr/bin/env python3
"""Exact arithmetic and slope utilities for the four-distance problem."""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


class PositiveInfinity:
    """A non-float +inf sentinel for valuations."""

    def __repr__(self) -> str:
        return "inf"

    def __str__(self) -> str:
        return "inf"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PositiveInfinity)

    def __lt__(self, other: object) -> bool:
        return False

    def __le__(self, other: object) -> bool:
        return isinstance(other, PositiveInfinity)

    def __gt__(self, other: object) -> bool:
        return not isinstance(other, PositiveInfinity)

    def __ge__(self, other: object) -> bool:
        return True

    def __hash__(self) -> int:
        return hash("PositiveInfinity")


INF = PositiveInfinity()


def is_square(n: int) -> bool:
    """Return True iff n is a non-negative perfect square, using only integers."""
    if n < 0:
        raise ValueError("is_square requires n >= 0")
    root = math.isqrt(n)
    return root * root == n


def _trial_squarefree_part(n: int) -> int:
    result = 1
    d = 2
    while d * d <= n:
        parity = 0
        while n % d == 0:
            n //= d
            parity ^= 1
        if parity:
            result *= d
        d += 1 if d == 2 else 2
    if n > 1:
        result *= n
    return result


def squarefree_part(n: int) -> int:
    """Return the squarefree part of a positive integer."""
    if n <= 0:
        raise ValueError("squarefree_part requires a positive integer")
    try:
        from sympy import factorint  # type: ignore

        result = 1
        for prime, exponent in factorint(n).items():
            if exponent & 1:
                result *= int(prime)
        return result
    except Exception:
        return _trial_squarefree_part(n)


def square_part_and_defect(n: int) -> tuple[int, int]:
    """Return k,d with n = k^2*d and d squarefree."""
    defect = squarefree_part(n)
    square_part = n // defect
    root = math.isqrt(square_part)
    if root * root != square_part:
        raise ArithmeticError(f"bad squarefree decomposition for {n}")
    return root, defect


def _vp_int(n: int, p: int) -> int:
    n = abs(n)
    count = 0
    while n and n % p == 0:
        n //= p
        count += 1
    return count


def v_p_fraction(frac: Fraction, p: int) -> int | PositiveInfinity:
    """Return v_p(frac) for a reduced Fraction; return +inf for zero."""
    if p <= 1:
        raise ValueError("p must be prime-like and > 1")
    if frac == 0:
        return INF
    return _vp_int(frac.numerator, p) - _vp_int(frac.denominator, p)


def fraction_to_str(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def valuation_to_str(value: int | PositiveInfinity) -> str:
    return "inf" if value == INF else str(value)


def in_S(alpha: Fraction) -> bool:
    """Return True iff sqrt(1 + alpha^2) is rational."""
    a = alpha.numerator
    b = alpha.denominator
    return is_square(a * a + b * b)


def canonical_key_under_square_symmetry(N: int, p: int, q: int) -> tuple[int, int, int]:
    """Canonicalize a rational point under square D4 symmetries."""
    candidates = (
        (p, q),
        (N - p, q),
        (p, N - q),
        (N - p, N - q),
        (q, p),
        (N - q, p),
        (q, N - p),
        (N - q, N - p),
    )
    p0, q0 = min(candidates)
    return (N, p0, q0)


@dataclass(frozen=True)
class McCloskeyGate:
    x: Fraction
    yc: Fraction
    v3_x: int | PositiveInfinity
    v3_yc: int | PositiveInfinity
    live: bool


def mcc_gate(N: int, p: int, q: int) -> McCloskeyGate:
    """McCloskey 3-adic necessary gate for a true four-distance solution."""
    x = Fraction(p, N)
    yc = Fraction(2 * q - N, 2 * N)
    v3_x = v_p_fraction(x, 3)
    v3_yc = v_p_fraction(yc, 3)
    return McCloskeyGate(x=x, yc=yc, v3_x=v3_x, v3_yc=v3_yc, live=(v3_x < 0 or v3_yc < 0))


@dataclass(frozen=True)
class SlopeData:
    A: Fraction
    B: Fraction
    C: Fraction
    D: Fraction
    delta: Fraction
    x: Fraction
    y: Fraction
    A_in_S: bool
    B_in_S: bool
    C_in_S: bool
    D_in_S: bool
    love_relation_ok: bool
    delta_relations_ok: bool
    point_from_delta: tuple[Fraction, Fraction]


def slope_from_seed(N: int, p: int, q: int) -> SlopeData:
    """Compute Love-style slope data from an oriented seed."""
    r = N - p
    s = N - q
    if min(p, q, r, s) <= 0:
        raise ValueError("seed must be an interior point")

    A = Fraction(q, p)
    B = Fraction(s, p)
    C = Fraction(r, q)
    D = Fraction(r, s)
    delta = C + Fraction(1, 1) / A
    x = Fraction(p, N)
    y = Fraction(q, N)
    point_from_delta = (Fraction(1, 1) / (A * delta), Fraction(1, 1) / delta)

    love_value = A * C
    love_relation_ok = love_value == B * D == A + B - 1
    delta_relations_ok = (
        B == A * (delta - 1)
        and x == point_from_delta[0]
        and y == point_from_delta[1]
    )
    return SlopeData(
        A=A,
        B=B,
        C=C,
        D=D,
        delta=delta,
        x=x,
        y=y,
        A_in_S=in_S(A),
        B_in_S=in_S(B),
        C_in_S=in_S(C),
        D_in_S=in_S(D),
        love_relation_ok=love_relation_ok,
        delta_relations_ok=delta_relations_ok,
        point_from_delta=point_from_delta,
    )


@dataclass(frozen=True)
class SeedVerification:
    N: int
    p: int
    q: int
    r: int
    s: int
    pq_sq: int
    rq_sq: int
    ps_sq: int
    rs_sq: int
    h_pq: int | None
    h_rq: int | None
    h_ps: int | None
    h_rs: int | None
    first_three_square: bool
    true_solution: bool
    defect: int
    fourth_factor: str
    primitive: bool
    canonical_key: tuple[int, int, int]
    mcc: McCloskeyGate
    slopes: SlopeData

    @property
    def point(self) -> tuple[Fraction, Fraction]:
        return (Fraction(self.p, self.N), Fraction(self.q, self.N))


def _square_root_or_none(n: int) -> int | None:
    root = math.isqrt(n)
    return root if root * root == n else None


def verify_seed(N: int, p: int, q: int) -> SeedVerification:
    """Verify an oriented K2,2 seed using exact integer arithmetic."""
    if not (0 < p < N and 0 < q < N):
        raise ValueError("requires 0 < p,q < N")
    r = N - p
    s = N - q
    pq_sq = p * p + q * q
    rq_sq = r * r + q * q
    ps_sq = p * p + s * s
    rs_sq = r * r + s * s
    h_pq = _square_root_or_none(pq_sq)
    h_rq = _square_root_or_none(rq_sq)
    h_ps = _square_root_or_none(ps_sq)
    h_rs = _square_root_or_none(rs_sq)
    first_three_square = h_pq is not None and h_rq is not None and h_ps is not None
    true_solution = first_three_square and h_rs is not None
    if h_rs is None:
        root, defect = square_part_and_defect(rs_sq)
        fourth_factor = f"{root}*sqrt({defect})"
    else:
        defect = 1
        fourth_factor = str(h_rs)

    return SeedVerification(
        N=N,
        p=p,
        q=q,
        r=r,
        s=s,
        pq_sq=pq_sq,
        rq_sq=rq_sq,
        ps_sq=ps_sq,
        rs_sq=rs_sq,
        h_pq=h_pq,
        h_rq=h_rq,
        h_ps=h_ps,
        h_rs=h_rs,
        first_three_square=first_three_square,
        true_solution=true_solution,
        defect=defect,
        fourth_factor=fourth_factor,
        primitive=math.gcd(math.gcd(p, q), N) == 1,
        canonical_key=canonical_key_under_square_symmetry(N, p, q),
        mcc=mcc_gate(N, p, q),
        slopes=slope_from_seed(N, p, q),
    )


def certificate_lines(seed: SeedVerification) -> list[str]:
    """Return a complete exact certificate for a seed or true solution."""
    slopes = seed.slopes
    lines = [
        f"N={seed.N}, p={seed.p}, q={seed.q}, r={seed.r}, s={seed.s}",
        f"P=({fraction_to_str(Fraction(seed.p, seed.N))},{fraction_to_str(Fraction(seed.q, seed.N))})",
        f"p^2+q^2={seed.pq_sq}={seed.h_pq}^2" if seed.h_pq is not None else f"p^2+q^2={seed.pq_sq} not square",
        f"r^2+q^2={seed.rq_sq}={seed.h_rq}^2" if seed.h_rq is not None else f"r^2+q^2={seed.rq_sq} not square",
        f"p^2+s^2={seed.ps_sq}={seed.h_ps}^2" if seed.h_ps is not None else f"p^2+s^2={seed.ps_sq} not square",
        f"r^2+s^2={seed.rs_sq}={seed.h_rs}^2" if seed.h_rs is not None else f"r^2+s^2={seed.rs_sq}={seed.fourth_factor}",
        f"defect={seed.defect}",
        "slopes:",
        f"A={fraction_to_str(slopes.A)}, B={fraction_to_str(slopes.B)}, C={fraction_to_str(slopes.C)}, D={fraction_to_str(slopes.D)}",
        f"delta={fraction_to_str(slopes.delta)}",
        f"A_in_S={slopes.A_in_S}, B_in_S={slopes.B_in_S}, C_in_S={slopes.C_in_S}, D_in_S={slopes.D_in_S}",
        f"A*C == B*D == A+B-1: {slopes.love_relation_ok}",
        f"B == A*(delta-1), P from delta: {slopes.delta_relations_ok}",
        f"point_from_delta=({fraction_to_str(slopes.point_from_delta[0])},{fraction_to_str(slopes.point_from_delta[1])})",
        "McCloskey 3-adic gate:",
        f"x={fraction_to_str(seed.mcc.x)}, yc={fraction_to_str(seed.mcc.yc)}, v3_x={valuation_to_str(seed.mcc.v3_x)}, v3_yc={valuation_to_str(seed.mcc.v3_yc)}, live={seed.mcc.live}",
    ]
    return lines


def seed_csv_row(seed: SeedVerification, row_id: int, duplicate_of: str) -> dict[str, Any]:
    slopes = seed.slopes
    fourth_norm = (
        f"{seed.h_rs}/{seed.N}"
        if seed.h_rs is not None
        else f"{seed.fourth_factor}/{seed.N}"
    )
    return {
        "row_id": row_id,
        "N": seed.N,
        "p": seed.p,
        "q": seed.q,
        "r": seed.r,
        "s": seed.s,
        "h_pq": seed.h_pq if seed.h_pq is not None else "",
        "h_rq": seed.h_rq if seed.h_rq is not None else "",
        "h_ps": seed.h_ps if seed.h_ps is not None else "",
        "h_rs_square": seed.h_rs is not None,
        "h_rs_or_sqrt_factor": seed.h_rs if seed.h_rs is not None else seed.fourth_factor,
        "fourth_norm": fourth_norm,
        "defect": seed.defect,
        "primitive": seed.primitive,
        "canonical_key": f"{seed.canonical_key[0]}:{seed.canonical_key[1]}:{seed.canonical_key[2]}",
        "duplicate_of": duplicate_of,
        "x": fraction_to_str(seed.mcc.x),
        "y": fraction_to_str(Fraction(seed.q, seed.N)),
        "yc": fraction_to_str(seed.mcc.yc),
        "v3_x": valuation_to_str(seed.mcc.v3_x),
        "v3_yc": valuation_to_str(seed.mcc.v3_yc),
        "mcc_live": seed.mcc.live,
        "A": fraction_to_str(slopes.A),
        "B": fraction_to_str(slopes.B),
        "C": fraction_to_str(slopes.C),
        "D": fraction_to_str(slopes.D),
        "delta": fraction_to_str(slopes.delta),
        "A_in_S": slopes.A_in_S,
        "B_in_S": slopes.B_in_S,
        "C_in_S": slopes.C_in_S,
        "D_in_S": slopes.D_in_S,
        "love_relation_ok": slopes.love_relation_ok and slopes.delta_relations_ok,
        "notes": "TRUE_SOLUTION" if seed.true_solution else "THREE_DISTANCE_SEED",
    }


SEED_CSV_FIELDS = [
    "row_id",
    "N",
    "p",
    "q",
    "r",
    "s",
    "h_pq",
    "h_rq",
    "h_ps",
    "h_rs_square",
    "h_rs_or_sqrt_factor",
    "fourth_norm",
    "defect",
    "primitive",
    "canonical_key",
    "duplicate_of",
    "x",
    "y",
    "yc",
    "v3_x",
    "v3_yc",
    "mcc_live",
    "A",
    "B",
    "C",
    "D",
    "delta",
    "A_in_S",
    "B_in_S",
    "C_in_S",
    "D_in_S",
    "love_relation_ok",
    "notes",
]


def generate_pythagorean_adjacency(limit: int) -> dict[int, set[int]]:
    """Generate all legs a,b<=limit for integer right triangles."""
    adjacency: dict[int, set[int]] = {}
    max_m = math.isqrt(2 * limit) + 2
    for m in range(2, max_m + 1):
        for n in range(1, m):
            if ((m - n) & 1) == 0 or math.gcd(m, n) != 1:
                continue
            a = m * m - n * n
            b = 2 * m * n
            high = max(a, b)
            if high > limit:
                continue
            for k in range(1, limit // high + 1):
                x = k * a
                y = k * b
                adjacency.setdefault(x, set()).add(y)
                adjacency.setdefault(y, set()).add(x)
    return adjacency


def generate_S_slopes(height: int) -> list[Fraction]:
    """Generate positive rational slopes in S with numerator/denominator <= height."""
    slopes: set[Fraction] = set()
    adjacency = generate_pythagorean_adjacency(height)
    for a, neighbors in adjacency.items():
        if a > height:
            continue
        for b in neighbors:
            if b <= height:
                slopes.add(Fraction(a, b))
    return sorted(slopes)


def fraction_height(frac: Fraction) -> int:
    return max(abs(frac.numerator), abs(frac.denominator))


def point_from_slopes(A: Fraction, B: Fraction) -> tuple[int, int, int, Fraction, Fraction]:
    """Return N,p,q,x,y from x=1/(A+B), y=A/(A+B)."""
    denom = A + B
    if denom == 0:
        raise ValueError("A+B is zero")
    x = Fraction(1, 1) / denom
    y = A / denom
    N = math.lcm(x.denominator, y.denominator)
    p = x.numerator * (N // x.denominator)
    q = y.numerator * (N // y.denominator)
    return N, p, q, x, y


def D_defect(D: Fraction) -> int:
    return squarefree_part(D.numerator * D.numerator + D.denominator * D.denominator)


def _slope_search(height: int, output_dir: Path, top: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    slopes = generate_S_slopes(height)
    out_path = output_dir / f"slope_candidates_H{height}.csv"
    rows: list[dict[str, Any]] = []
    true_count = 0
    for A in slopes:
        for C in slopes:
            B = A * C + 1 - A
            if B == 0 or not in_S(B):
                continue
            D = A * C / B
            D_in = in_S(D)
            N, p, q, x, y = point_from_slopes(A, B)
            if not (0 < p < N and 0 < q < N):
                continue
            gate = mcc_gate(N, p, q)
            defect = 1 if D_in else D_defect(D)
            if D_in:
                true_count += 1
                seed = verify_seed(N, p, q)
                print("FOUND TRUE FOUR-DISTANCE SOLUTION")
                print("\n".join(certificate_lines(seed)))
            rows.append(
                {
                    "A": fraction_to_str(A),
                    "C": fraction_to_str(C),
                    "B": fraction_to_str(B),
                    "D": fraction_to_str(D),
                    "D_in_S": D_in,
                    "defect_D": defect,
                    "delta": fraction_to_str(C + Fraction(1, 1) / A),
                    "N": N,
                    "p": p,
                    "q": q,
                    "x": fraction_to_str(x),
                    "y": fraction_to_str(y),
                    "v3_x": valuation_to_str(gate.v3_x),
                    "v3_yc": valuation_to_str(gate.v3_yc),
                    "mcc_live": gate.live,
                    "height": max(fraction_height(A), fraction_height(C), fraction_height(B), fraction_height(D)),
                }
            )
    rows.sort(key=lambda row: (not bool(row["D_in_S"]), int(row["defect_D"]), not bool(row["mcc_live"]), int(row["height"]), int(row["N"])))
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "A",
            "C",
            "B",
            "D",
            "D_in_S",
            "defect_D",
            "delta",
            "N",
            "p",
            "q",
            "x",
            "y",
            "v3_x",
            "v3_yc",
            "mcc_live",
            "height",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows[:top]:
            writer.writerow(row)
    print(f"slopes={len(slopes)}, candidates={len(rows)}, true_solutions={true_count}, wrote={out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Exact slope closure search.")
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--top", type=int, default=500)
    args = parser.parse_args()
    _slope_search(args.height, args.output_dir, args.top)


if __name__ == "__main__":
    if __package__ is None:
        sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    main()
