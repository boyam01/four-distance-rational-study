#!/usr/bin/env python3
"""Local exact searches around the live defect-730 seed."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.slope_tools import (
        D_defect,
        certificate_lines,
        fraction_height,
        fraction_to_str,
        generate_S_slopes,
        in_S,
        mcc_gate,
        point_from_slopes,
        valuation_to_str,
        verify_seed,
    )
else:
    from .slope_tools import (
        D_defect,
        certificate_lines,
        fraction_height,
        fraction_to_str,
        generate_S_slopes,
        in_S,
        mcc_gate,
        point_from_slopes,
        valuation_to_str,
        verify_seed,
    )


A0 = Fraction(15, 8)
C0 = Fraction(451, 780)


def _candidate_row(A: Fraction, C: Fraction, mode: str) -> dict[str, Any] | None:
    B = A * C + 1 - A
    if B == 0 or not in_S(B):
        return None
    D = A * C / B
    D_in = in_S(D)
    N, p, q, x, y = point_from_slopes(A, B)
    if not (0 < p < N and 0 < q < N):
        return None
    gate = mcc_gate(N, p, q)
    defect = 1 if D_in else D_defect(D)
    if D_in:
        seed = verify_seed(N, p, q)
        print("FOUND TRUE FOUR-DISTANCE SOLUTION")
        print("\n".join(certificate_lines(seed)))
    return {
        "mode": mode,
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
        "dist_A0": fraction_to_str(abs(A - A0)),
        "dist_C0": fraction_to_str(abs(C - C0)),
    }


def run_local_search(height: int, window: Fraction, output_dir: Path, reports_dir: Path, top: int) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    slopes = generate_S_slopes(height)
    rows: list[dict[str, Any]] = []

    near_A = [A for A in slopes if abs(A - A0) <= window]
    near_C = [C for C in slopes if abs(C - C0) <= window]
    for A in near_A:
        for C in near_C:
            row = _candidate_row(A, C, "real_near")
            if row:
                rows.append(row)

    for A in slopes:
        for C in slopes:
            row = _candidate_row(A, C, "mcc_priority")
            if row and row["mcc_live"]:
                rows.append(row)

    dedup: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["A"], row["C"], row["B"], row["D"], row["mode"])
        dedup[key] = row
    rows = list(dedup.values())
    rows.sort(
        key=lambda row: (
            not bool(row["D_in_S"]),
            int(row["defect_D"]),
            not bool(row["mcc_live"]),
            int(row["height"]),
            int(row["N"]),
        )
    )

    csv_path = output_dir / f"local_730_candidates_H{height}.csv"
    fields = [
        "mode",
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
        "dist_A0",
        "dist_C0",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows[:top]:
            writer.writerow(row)

    better = [row for row in rows if int(row["defect_D"]) < 730 and not bool(row["D_in_S"])]
    true_rows = [row for row in rows if bool(row["D_in_S"])]
    report_path = reports_dir / f"local_730_report_H{height}.md"
    lines = [
        "# Local 730 Search Report",
        "",
        f"- Height: {height}",
        f"- Window: {fraction_to_str(window)}",
        f"- S slopes generated: {len(slopes)}",
        f"- Real-near A count: {len(near_A)}",
        f"- Real-near C count: {len(near_C)}",
        f"- Candidate rows before top cut: {len(rows)}",
        f"- Found D in S: {'yes' if true_rows else 'no'}",
        f"- Better-than-730 non-solution candidate: {'yes' if better else 'no'}",
        "",
        "## Top Candidates",
        "",
        "| mode | defect_D | D_in_S | mcc_live | N | p | q | A | C | B | D |",
        "|---|---:|---|---|---:|---:|---:|---|---|---|---|",
    ]
    for row in rows[:30]:
        lines.append(
            f"| {row['mode']} | {row['defect_D']} | {row['D_in_S']} | {row['mcc_live']} | "
            f"{row['N']} | {row['p']} | {row['q']} | {row['A']} | {row['C']} | {row['B']} | {row['D']} |"
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "This local search is exact arithmetic evidence only. It is not a theorem and does not exhaust slopes above the selected height.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")
    return csv_path, report_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--window-num", type=int, default=1)
    parser.add_argument("--window-den", type=int, default=100)
    parser.add_argument("--output-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    parser.add_argument("--top", type=int, default=500)
    args = parser.parse_args()
    run_local_search(args.height, Fraction(args.window_num, args.window_den), args.output_dir, args.reports_dir, args.top)


if __name__ == "__main__":
    main()

