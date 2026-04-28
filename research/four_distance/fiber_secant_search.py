#!/usr/bin/env python3
"""Fixed-delta fiber/secant experiments for four-distance near-misses.

This module is a finite exact-arithmetic experiment harness.  It prepares the
quartic fibers for B,C,D in S and, when Sage is unavailable, uses a small
experimental rational secant fallback to generate additional rational u values.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from fractions import Fraction
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.reverse_closure_search import four_distance_squares, point_to_integral
    from research.four_distance.slope_tools import (
        certificate_lines,
        fraction_height,
        fraction_to_str,
        in_S,
        is_square,
        mcc_gate,
        squarefree_part,
        valuation_to_str,
        verify_seed,
    )
else:
    from .reverse_closure_search import four_distance_squares, point_to_integral
    from .slope_tools import (
        certificate_lines,
        fraction_height,
        fraction_to_str,
        in_S,
        is_square,
        mcc_gate,
        squarefree_part,
        valuation_to_str,
        verify_seed,
    )


DELTA_730 = Fraction(289, 260)
DELTA_17 = Fraction(13, 6)
U_730 = Fraction(3, 5)
U_17 = Fraction(1, 4)


def slope_defect(alpha: Fraction) -> int:
    n = alpha.numerator * alpha.numerator + alpha.denominator * alpha.denominator
    if is_square(n):
        return 1
    return squarefree_part(n)


def rational_square_root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    if not is_square(value.numerator) or not is_square(value.denominator):
        return None
    return Fraction(math.isqrt(value.numerator), math.isqrt(value.denominator))


def A_of_u(u: Fraction) -> Fraction:
    return Fraction(2) * u / (1 - u * u)


def B_of_u_delta(u: Fraction, delta: Fraction) -> Fraction:
    A = A_of_u(u)
    return A * (delta - 1)


def C_of_u_delta(u: Fraction, delta: Fraction) -> Fraction:
    A = A_of_u(u)
    return delta - Fraction(1, 1) / A


def D_of_u_delta(u: Fraction, delta: Fraction) -> Fraction:
    A = A_of_u(u)
    return (A * delta - 1) / (A * (delta - 1))


def point_from_u_delta(u: Fraction, delta: Fraction) -> tuple[Fraction, Fraction]:
    A = A_of_u(u)
    x = Fraction(1, 1) / (A * delta)
    y = Fraction(1, 1) / delta
    return x, y


def fiber_value(label: str, u: Fraction, delta: Fraction) -> Fraction:
    if label == "B":
        return B_of_u_delta(u, delta)
    if label == "C":
        return C_of_u_delta(u, delta)
    if label == "D":
        return D_of_u_delta(u, delta)
    raise ValueError(f"unknown fiber label: {label}")


def fiber_point_status(label: str, u: Fraction, delta: Fraction) -> bool:
    return slope_defect(fiber_value(label, u, delta)) == 1


@dataclass(frozen=True)
class FiberCurve:
    label: str
    delta: Fraction
    numerator: str
    denominator: str
    polynomial: str
    denominator_square: str
    known_basepoints: list[str]
    sage_status: str
    rank_info: str


def _sympy_rational(value: Fraction) -> Any:
    import sympy as sp

    return sp.Rational(value.numerator, value.denominator)


def build_fiber_curve(label: str, delta: Fraction, known_us: list[Fraction]) -> FiberCurve:
    import sympy as sp

    u = sp.symbols("u")
    d = sp.Rational(delta.numerator, delta.denominator)
    A = 2 * u / (1 - u**2)
    expressions = {
        "B": A * (d - 1),
        "C": d - 1 / A,
        "D": (A * d - 1) / (A * (d - 1)),
    }
    reduced = sp.together(expressions[label])
    num, den = sp.fraction(reduced)
    polynomial = sp.factor(num**2 + den**2)
    denominator_square = sp.factor(den**2)
    basepoints: list[str] = []
    for u0 in known_us:
        if u0 in (0, 1, -1):
            continue
        try:
            F_value = evaluate_polynomial_str(str(polynomial), u0)
        except Exception:
            continue
        root = rational_square_root(F_value)
        if root is not None and fiber_point_status(label, u0, delta):
            basepoints.append(f"u={fraction_to_str(u0)}, W={fraction_to_str(root)}")
    sage_status, rank_info = try_sage_curve(str(polynomial))
    return FiberCurve(
        label=f"{label}_fiber",
        delta=delta,
        numerator=str(sp.factor(num)),
        denominator=str(sp.factor(den)),
        polynomial=str(polynomial),
        denominator_square=str(denominator_square),
        known_basepoints=basepoints,
        sage_status=sage_status,
        rank_info=rank_info,
    )


def try_sage_curve(polynomial: str) -> tuple[str, str]:
    try:
        from sage.all import HyperellipticCurve, PolynomialRing, QQ  # type: ignore
    except Exception:
        return "Sage unavailable; rank/generator search skipped.", "skipped"
    try:  # pragma: no cover - Sage is usually unavailable in CI/local Python.
        ring = PolynomialRing(QQ, "u")
        u = ring.gen()
        F = ring(polynomial.replace("**", "^"))
        curve = HyperellipticCurve(F)
        jac = curve.jacobian()
        rank_info = "rank unavailable"
        try:
            rank_info = f"rank_bounds={jac.rank_bounds()}"
        except Exception:
            pass
        return "Sage available; constructed HyperellipticCurve.", rank_info
    except Exception as exc:  # pragma: no cover
        return f"Sage available but curve construction failed: {exc}", "failed"


@lru_cache(maxsize=None)
def evaluate_polynomial_str(polynomial: str, u_value: Fraction) -> Fraction:
    import sympy as sp

    u = sp.symbols("u")
    expr = sp.sympify(polynomial)
    value = sp.factor(expr.subs(u, sp.Rational(u_value.numerator, u_value.denominator)))
    return Fraction(int(value.p), int(value.q)) if hasattr(value, "p") else Fraction(str(value))


def rational_u_grid(height: int) -> list[Fraction]:
    values: set[Fraction] = set()
    for den in range(1, height + 1):
        for num in range(-height, height + 1):
            if num == 0:
                continue
            value = Fraction(num, den)
            if value not in (1, -1):
                values.add(value)
    return sorted(values)


def rational_points_on_fiber(label: str, delta: Fraction, polynomial: str, height: int, known_us: list[Fraction]) -> list[tuple[Fraction, Fraction]]:
    points: dict[Fraction, Fraction] = {}
    for u0 in itertools.chain(known_us, rational_u_grid(height)):
        if u0 in (0, 1, -1):
            continue
        try:
            if not fiber_point_status(label, u0, delta):
                continue
            root = rational_square_root(evaluate_polynomial_str(polynomial, u0))
        except Exception:
            continue
        if root is not None:
            points[u0] = root
    return sorted(points.items(), key=lambda item: (fraction_height(item[0]), item[0]))


def secant_residual_us(polynomial: str, points: list[tuple[Fraction, Fraction]], max_pairs: int) -> set[Fraction]:
    """Experimental secant fallback: intersect lines through known points with quartic."""
    import sympy as sp

    u = sp.symbols("u")
    F = sp.sympify(polynomial)
    output: set[Fraction] = set()
    limited = points[:max_pairs]
    for (u1, w1), (u2, w2) in itertools.combinations(limited, 2):
        if u1 == u2:
            continue
        slope = (w2 - w1) / (u2 - u1)
        intercept = w1 - slope * u1
        line = _sympy_rational(slope) * u + _sympy_rational(intercept)
        numerator = sp.fraction(sp.together(line**2 - F))[0]
        poly = sp.Poly(sp.factor(numerator), u, domain=sp.QQ)
        for root in (u1, u2):
            divisor = sp.Poly(u - _sympy_rational(root), u, domain=sp.QQ)
            poly, rem = sp.div(poly, divisor)
            if rem.as_expr() != 0:
                break
        roots = sp.roots(poly.as_expr(), u)
        for root, multiplicity in roots.items():
            if getattr(root, "is_Rational", False):
                candidate = Fraction(int(root.p), int(root.q))
                if candidate not in (0, 1, -1):
                    output.add(candidate)
    return output


def candidate_from_u(delta: Fraction, u: Fraction, source: str, main_fiber: str) -> dict[str, Any] | None:
    try:
        A = A_of_u(u)
        B = B_of_u_delta(u, delta)
        C = C_of_u_delta(u, delta)
        D = D_of_u_delta(u, delta)
        x, y = point_from_u_delta(u, delta)
    except ZeroDivisionError:
        return None
    defect_B = slope_defect(B)
    defect_C = slope_defect(C)
    defect_D = slope_defect(D)
    N, p, q, r, s = point_to_integral(x, y)
    gate = mcc_gate(N, p, q)
    four_ok, failures = four_distance_squares(x, y)
    point_in_unit = 0 < p < N and 0 < q < N
    true_solution = defect_B == defect_C == defect_D == 1 and four_ok and point_in_unit
    if true_solution:
        print("FOUND TRUE SOLUTION certificate")
        print("\n".join(certificate_lines(verify_seed(N, p, q))))
    notes = "TRUE_SOLUTION" if true_solution else "near_miss"
    if failures:
        notes += ":" + ";".join(failures)
    distance_to_730 = abs(u - U_730)
    return {
        "delta": fraction_to_str(delta),
        "u": fraction_to_str(u),
        "source": source,
        "main_fiber": main_fiber,
        "A": fraction_to_str(A),
        "B": fraction_to_str(B),
        "C": fraction_to_str(C),
        "D": fraction_to_str(D),
        "defect_B": defect_B,
        "defect_C": defect_C,
        "defect_D": defect_D,
        "score": defect_B * defect_C * defect_D,
        "x": fraction_to_str(x),
        "y": fraction_to_str(y),
        "N": N,
        "p": p,
        "q": q,
        "r": r,
        "s": s,
        "v3_x": valuation_to_str(gate.v3_x),
        "v3_yc": valuation_to_str(gate.v3_yc),
        "mcc_live": gate.live,
        "point_in_unit": point_in_unit,
        "four_distance_ok": four_ok,
        "true_solution": true_solution,
        "height": max(fraction_height(A), fraction_height(B), fraction_height(C), fraction_height(D), fraction_height(u)),
        "distance_to_u730": fraction_to_str(distance_to_730),
        "notes": notes,
    }


def candidate_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        not bool(row["true_solution"]),
        int(row["defect_D"]),
        int(row["score"]),
        not bool(row["mcc_live"]),
        not bool(row["point_in_unit"]),
        int(row["height"]),
        Fraction(row["distance_to_u730"]),
    )


def two_good_one_bad(defects: tuple[int, int, int]) -> tuple[bool, int | None]:
    bad = [value for value in defects if value != 1]
    if len(bad) == 1:
        return True, bad[0]
    return False, None


def known_us_for_delta(delta: Fraction) -> list[Fraction]:
    known = [U_730, U_17]
    if delta == DELTA_730:
        known.insert(0, U_730)
    if delta == DELTA_17:
        known.insert(0, U_17)
    return list(dict.fromkeys(known))


def collect_deltas(args: argparse.Namespace) -> list[Fraction]:
    deltas: list[Fraction] = []
    if args.all or not args.delta and not args.from_one_sided:
        deltas.extend([DELTA_730, DELTA_17])
    for text in args.delta or []:
        deltas.append(Fraction(text))
    if args.from_one_sided:
        deltas.extend(read_one_sided_deltas(args.from_one_sided, args.max_deltas))
    return list(dict.fromkeys(deltas))


def read_one_sided_deltas(path: Path, max_deltas: int) -> list[Fraction]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    rows.sort(
        key=lambda row: (
            row.get("point_in_unit") != "True",
            row.get("mcc_live") != "True",
            int(row.get("score", "0") or 0),
        )
    )
    deltas: list[Fraction] = []
    for row in rows:
        try:
            A = Fraction(row["A"])
            C = Fraction(row["C"])
            deltas.append(C + Fraction(1, 1) / A)
        except Exception:
            continue
        if len(dict.fromkeys(deltas)) >= max_deltas:
            break
    return list(dict.fromkeys(deltas))


CURVE_FIELDS = ["curve_label", "delta", "numerator", "denominator", "polynomial", "denominator_square", "known_basepoints", "sage_status", "rank_info"]
CANDIDATE_FIELDS = [
    "delta",
    "u",
    "source",
    "main_fiber",
    "A",
    "B",
    "C",
    "D",
    "defect_B",
    "defect_C",
    "defect_D",
    "score",
    "x",
    "y",
    "N",
    "p",
    "q",
    "r",
    "s",
    "v3_x",
    "v3_yc",
    "mcc_live",
    "point_in_unit",
    "four_distance_ok",
    "true_solution",
    "height",
    "distance_to_u730",
    "notes",
]


def run_search(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    data_dir = args.output_dir
    report_dir = args.reports_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    curves_path = data_dir / "fiber_secant_curves.csv"
    candidates_path = data_dir / "fiber_secant_candidates.csv"
    report_path = report_dir / "fiber_secant_report.md"
    deltas = collect_deltas(args)
    if args.resume and candidates_path.exists() and curves_path.exists() and report_path.exists():
        print("resume requested and existing fiber outputs found; leaving existing files in place")
        return curves_path, candidates_path, report_path

    curve_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    fiber_labels = ["B", "C", "D"] if args.main == "all" else [args.main]
    all_curve_labels = ["B", "C", "D"]

    for delta in deltas:
        known_us = known_us_for_delta(delta)
        built_curves = {label: build_fiber_curve(label, delta, known_us) for label in all_curve_labels}
        for curve in built_curves.values():
            curve_rows.append(
                {
                    "curve_label": curve.label,
                    "delta": fraction_to_str(curve.delta),
                    "numerator": curve.numerator,
                    "denominator": curve.denominator,
                    "polynomial": curve.polynomial,
                    "denominator_square": curve.denominator_square,
                    "known_basepoints": "; ".join(curve.known_basepoints),
                    "sage_status": curve.sage_status,
                    "rank_info": curve.rank_info,
                }
            )

        u_candidates: dict[Fraction, str] = {}
        for u0 in known_us:
            if u0 not in (0, 1, -1):
                u_candidates[u0] = "known"
        for label in fiber_labels:
            curve = built_curves[label]
            points = rational_points_on_fiber(label, delta, curve.polynomial, min(args.max_multiple, 80), known_us)
            for u0, _w in points[: args.max_multiple]:
                u_candidates.setdefault(u0, f"{label}_sample")
            for u0 in secant_residual_us(curve.polynomial, points, args.max_multiple):
                u_candidates.setdefault(u0, f"{label}_experimental_secant")

        for u0, source in u_candidates.items():
            row = candidate_from_u(delta, u0, source, args.main)
            if row is not None:
                candidate_rows.append(row)

    dedup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in candidate_rows:
        key = (row["delta"], row["u"])
        old = dedup.get(key)
        if old is None or candidate_sort_key(row) < candidate_sort_key(old):
            dedup[key] = row
    candidate_rows = sorted(dedup.values(), key=candidate_sort_key)

    with curves_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CURVE_FIELDS)
        writer.writeheader()
        writer.writerows(curve_rows)
    with candidates_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_FIELDS)
        writer.writeheader()
        writer.writerows(candidate_rows)
    write_report(report_path, deltas, curve_rows, candidate_rows)
    return curves_path, candidates_path, report_path


def write_report(path: Path, deltas: list[Fraction], curve_rows: list[dict[str, Any]], candidate_rows: list[dict[str, Any]]) -> None:
    sage_available = any(str(row["sage_status"]).startswith("Sage available") for row in curve_rows)
    true_rows = [row for row in candidate_rows if row["true_solution"] is True]
    best = candidate_rows[:20]
    delta_730_rows = [row for row in candidate_rows if row["delta"] == fraction_to_str(DELTA_730)]
    lines = [
        "# Fiber Secant Search Report",
        "",
        "## Summary",
        f"- Sage available? {'yes' if sage_available else 'no'}",
        f"- deltas tested: {', '.join(fraction_to_str(delta) for delta in deltas)}",
        f"- fibers built: {len(curve_rows)}",
        "- ranks/rank_bounds if available: "
        + "; ".join(sorted(set(str(row["rank_info"]) for row in curve_rows))),
        f"- candidates generated: {len(candidate_rows)}",
        f"- true solutions found: {len(true_rows)}",
        "",
        "## Delta 289/260 Analysis",
    ]
    for row in curve_rows:
        if row["delta"] == fraction_to_str(DELTA_730):
            lines.extend(
                [
                    f"### {row['curve_label']}",
                    f"- polynomial: `{row['polynomial']}`",
                    f"- known rational basepoints: {row['known_basepoints'] or 'none'}",
                    f"- sage: {row['sage_status']}",
                ]
            )
    u730 = candidate_from_u(DELTA_730, U_730, "known", "all")
    if u730:
        lines.extend(
            [
                "",
                "u0=3/5 status:",
                f"- A={u730['A']}, B={u730['B']}, C={u730['C']}, D={u730['D']}",
                f"- defects: B={u730['defect_B']}, C={u730['defect_C']}, D={u730['defect_D']}",
                f"- P=({u730['x']},{u730['y']})",
            ]
        )
    single_defect_diagnostics = [row for row in delta_730_rows if int(row["defect_D"]) < 730 and row["true_solution"] is not True]
    two_good_improvements = []
    for row in delta_730_rows:
        ok, remaining = two_good_one_bad((int(row["defect_B"]), int(row["defect_C"]), int(row["defect_D"])))
        if ok and remaining is not None and remaining < 730:
            two_good_improvements.append(row)
    lines.append(f"- generated u candidates: {len(delta_730_rows)}")
    lines.append(f"- single-defect diagnostic improvements: {len(single_defect_diagnostics)}")
    lines.append(f"- two-good-one-bad improvements over 730: {len(two_good_improvements)}")
    lines.extend(
        [
            "",
            "## One-sided Fiber Analysis",
            "| delta | u | source | defect_B | defect_C | defect_D | score | mcc_live | point_in_unit |",
            "|---|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in best:
        lines.append(
            f"| {row['delta']} | {row['u']} | {row['source']} | {row['defect_B']} | {row['defect_C']} | {row['defect_D']} | {row['score']} | {row['mcc_live']} | {row['point_in_unit']} |"
        )
    lines.extend(["", "## Conclusion"])
    if true_rows:
        lines.append("FOUND TRUE SOLUTION in this finite fiber/secant run. Inspect the CSV certificate rows.")
    else:
        lines.append("no true solution found in this finite fiber/secant run.")
    lines.append("The secant fallback is experimental and is not a complete group-law or Mordell-Weil computation.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delta", action="append")
    parser.add_argument("--main", choices=["B", "C", "D", "all"], default="all")
    parser.add_argument("--max-multiple", type=int, default=50)
    parser.add_argument("--from-one-sided", type=Path)
    parser.add_argument("--max-deltas", type=int, default=20)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    args = parser.parse_args()
    curves_path, candidates_path, report_path = run_search(args)
    print(f"curves: {curves_path}")
    print(f"candidates: {candidates_path}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
