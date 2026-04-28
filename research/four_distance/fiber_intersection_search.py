#!/usr/bin/env python3
"""Exact u-set intersection audit for fixed-delta Mordell-Weil fiber orbits."""

from __future__ import annotations

import argparse
import csv
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

if __package__ in (None, ""):
    import os

    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.fiber_secant_search import (
        B_of_u_delta,
        C_of_u_delta,
        D_of_u_delta,
        point_from_u_delta,
        slope_defect,
    )
    from research.four_distance.modular_sieve_verifier import defect_below_limit, slope_norm
    from research.four_distance.reverse_closure_search import four_distance_squares, point_to_integral
    from research.four_distance.sage_fiber_bridge import two_good_one_bad
    from research.four_distance.slope_tools import certificate_lines, fraction_to_str, mcc_gate, verify_seed
else:
    from .fiber_secant_search import B_of_u_delta, C_of_u_delta, D_of_u_delta, point_from_u_delta, slope_defect
    from .modular_sieve_verifier import defect_below_limit, slope_norm
    from .reverse_closure_search import four_distance_squares, point_to_integral
    from .sage_fiber_bridge import two_good_one_bad
    from .slope_tools import certificate_lines, fraction_to_str, mcc_gate, verify_seed


FIELDS = [
    "delta",
    "intersection",
    "u",
    "fibers",
    "sources",
    "defect_B",
    "defect_C",
    "defect_D",
    "remaining_defect",
    "x",
    "y",
    "N",
    "p",
    "q",
    "r",
    "s",
    "mcc_live",
    "point_in_unit",
    "four_distance_ok",
    "true_solution",
    "notes",
]


def delta_slug(delta: str) -> str:
    return delta.replace("/", "_")


def load_u_sets(points_csv: Path, delta: Fraction) -> dict[str, dict[Fraction, list[dict[str, str]]]]:
    sets = {"B": {}, "C": {}, "D": {}}
    if not points_csv.exists():
        return sets
    with points_csv.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if Fraction(row.get("delta", "0")) != delta:
                continue
            fiber = row.get("fiber", "")
            if fiber not in sets:
                continue
            try:
                u = Fraction(row["u"])
            except Exception:
                continue
            sets[fiber].setdefault(u, []).append(row)
    return sets


def _defect_for(alpha: Fraction, square_known: bool, bit_threshold: int = 5000) -> int | str:
    if square_known:
        return 1
    norm = slope_norm(alpha)
    small = defect_below_limit(norm, 729)
    if small is not None:
        return small
    if norm.bit_length() <= bit_threshold:
        return slope_defect(alpha)
    return "no_small_defect_below_730"


def verify_u(delta: Fraction, u: Fraction, fibers: set[str], source_rows: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    B = B_of_u_delta(u, delta)
    C = C_of_u_delta(u, delta)
    D = D_of_u_delta(u, delta)
    square_B = "B" in fibers
    square_C = "C" in fibers
    square_D = "D" in fibers
    defect_B = _defect_for(B, square_B)
    defect_C = _defect_for(C, square_C)
    defect_D = _defect_for(D, square_D)
    defects = (defect_B, defect_C, defect_D)
    exact_defects = all(isinstance(value, int) for value in defects)
    remaining = ""
    if exact_defects:
        _two_good, rem = two_good_one_bad((int(defect_B), int(defect_C), int(defect_D)))
        remaining = rem if rem is not None else ""

    x, y = point_from_u_delta(u, delta)
    N, p, q, r, s = point_to_integral(x, y)
    gate = mcc_gate(N, p, q)
    four_ok, failures = four_distance_squares(x, y)
    point_in_unit = 0 < p < N and 0 < q < N
    true_solution = defect_B == defect_C == defect_D == 1 and four_ok and point_in_unit
    if true_solution:
        print("FOUND TRUE FOUR-DISTANCE SOLUTION")
        print("\n".join(certificate_lines(verify_seed(N, p, q))))
    sources = []
    for fiber in sorted(source_rows):
        labels = sorted({row.get("source", "") for row in source_rows[fiber] if row.get("source")})
        sources.append("%s:%s" % (fiber, "+".join(labels)))
    notes = "TRUE_SOLUTION" if true_solution else "intersection_near_miss"
    if failures:
        notes += ":" + ";".join(failures)
    return {
        "delta": fraction_to_str(delta),
        "intersection": "".join(sorted(fibers)),
        "u": fraction_to_str(u),
        "fibers": "+".join(sorted(fibers)),
        "sources": "|".join(sources),
        "defect_B": defect_B,
        "defect_C": defect_C,
        "defect_D": defect_D,
        "remaining_defect": remaining,
        "x": fraction_to_str(x),
        "y": fraction_to_str(y),
        "N": N,
        "p": p,
        "q": q,
        "r": r,
        "s": s,
        "mcc_live": gate.live,
        "point_in_unit": point_in_unit,
        "four_distance_ok": four_ok,
        "true_solution": true_solution,
        "notes": notes,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, delta: Fraction, counts: dict[str, int], intersections: dict[str, set[Fraction]], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Intersection Summary",
        "",
        f"- delta: {fraction_to_str(delta)}",
        f"- |U_B|: {counts['B']}",
        f"- |U_C|: {counts['C']}",
        f"- |U_D|: {counts['D']}",
        f"- |U_B ∩ U_C|: {len(intersections['BC'])}",
        f"- |U_B ∩ U_D|: {len(intersections['BD'])}",
        f"- |U_C ∩ U_D|: {len(intersections['CD'])}",
        f"- |U_B ∩ U_C ∩ U_D|: {len(intersections['BCD'])}",
        "",
        "## Known Chain",
        "1. u=3/5, defects=(1,1,730), P=(416/867,260/289)",
        "2. u=15/26, defects=(730,1,1), P=(451/867,260/289)",
        "",
        "## Pairwise Intersections",
    ]
    for label in ("BC", "BD", "CD"):
        lines.append("")
        lines.append("### U_%s ∩ U_%s" % (label[0], label[1]))
        subset = [row for row in rows if row["intersection"] == label]
        if not subset:
            lines.append("- none")
            continue
        for row in subset[:100]:
            lines.append(
                "- u=%s defects=(%s,%s,%s) P=(%s,%s) mcc_live=%s point_in_unit=%s"
                % (
                    row["u"],
                    row["defect_B"],
                    row["defect_C"],
                    row["defect_D"],
                    row["x"],
                    row["y"],
                    row["mcc_live"],
                    row["point_in_unit"],
                )
            )
    lines.extend(["", "## Triple Intersections"])
    triple = [row for row in rows if row["intersection"] == "BCD"]
    if not triple:
        lines.append("- none")
    for row in triple:
        lines.append(
            "- u=%s defects=(%s,%s,%s) true_solution=%s"
            % (row["u"], row["defect_B"], row["defect_C"], row["defect_D"], row["true_solution"])
        )
    lines.extend(["", "## Interpretation"])
    if any(row["true_solution"] is True for row in rows):
        lines.append("FOUND TRUE FOUR-DISTANCE SOLUTION. Inspect CSV and certificate output.")
    else:
        lines.append("no true solution found in this finite fiber intersection audit.")
        lines.append("This is not a proof of non-existence.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(delta_text: str, points_csv: Path, data_dir: Path, reports_dir: Path) -> tuple[Path, Path]:
    delta = Fraction(delta_text)
    sets = load_u_sets(points_csv, delta)
    U = {fiber: set(values) for fiber, values in sets.items()}
    intersections = {
        "BC": U["B"] & U["C"],
        "BD": U["B"] & U["D"],
        "CD": U["C"] & U["D"],
        "BCD": U["B"] & U["C"] & U["D"],
    }
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, Fraction]] = set()
    for label, values in intersections.items():
        fibers = set(label)
        for u in sorted(values):
            key = (label, u)
            if key in seen:
                continue
            seen.add(key)
            source_rows = {fiber: sets[fiber].get(u, []) for fiber in fibers}
            rows.append(verify_u(delta, u, fibers, source_rows))

    slug = delta_slug(delta_text)
    csv_path = data_dir / f"fiber_intersections_delta_{slug}.csv"
    report_path = reports_dir / f"fiber_intersections_delta_{slug}.md"
    alias_report = reports_dir / f"fiber_intersection_report_delta_{slug}.md"
    write_csv(csv_path, rows)
    counts = {fiber: len(U[fiber]) for fiber in ("B", "C", "D")}
    write_report(report_path, delta, counts, intersections, rows)
    alias_report.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    return csv_path, report_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delta", default="289/260")
    parser.add_argument("--points-csv", type=Path, default=Path("research/four_distance/data/sage_fiber_points.csv"))
    parser.add_argument("--data-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    args = parser.parse_args()
    csv_path, report_path = run(args.delta, args.points_csv, args.data_dir, args.reports_dir)
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
