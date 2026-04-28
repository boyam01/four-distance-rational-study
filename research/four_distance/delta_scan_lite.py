#!/usr/bin/env python3
"""Lightweight fixed-delta fiber intersection scan.

This is a small-scale comparative scan.  It is intended to test whether the
intersection sparsity seen at delta=289/260 also appears for nearby/related
fixed-delta fibers.  It is not a proof search over all deltas.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

if __package__ in (None, ""):
    import os

    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.fiber_intersection_search import load_u_sets, verify_u
    from research.four_distance.fiber_secant_search import build_fiber_curve
    from research.four_distance.modular_sieve_verifier import prime_list
    from research.four_distance.sage_fiber_bridge import verify_sage_points
    from research.four_distance.slope_tools import fraction_to_str
else:
    from .fiber_intersection_search import load_u_sets, verify_u
    from .fiber_secant_search import build_fiber_curve
    from .modular_sieve_verifier import prime_list
    from .sage_fiber_bridge import verify_sage_points
    from .slope_tools import fraction_to_str


DEFAULT_DELTAS = [
    Fraction(13, 6),
    Fraction(289, 260),
    Fraction(867, 416),
    Fraction(289, 29),
    Fraction(332, 255),
    Fraction(249, 130),
]

SUMMARY_FIELDS = [
    "delta",
    "fibers_with_basepoints",
    "B_rank",
    "B_rank_bounds",
    "C_rank",
    "C_rank_bounds",
    "D_rank",
    "D_rank_bounds",
    "UB_size",
    "UC_size",
    "UD_size",
    "UB_UC_size",
    "UB_UD_size",
    "UC_UD_size",
    "triple_size",
    "true_solution_count",
    "best_live_in_unit_defect",
    "improved_over_seed_defect",
    "symmetry_chain_detected",
    "notes",
]


@dataclass(frozen=True)
class SourceCandidate:
    delta: Fraction
    u: Fraction
    defects: tuple[int, int, int]
    mcc_live: bool
    point_in_unit: bool
    height: int

    @property
    def two_good_one_bad(self) -> bool:
        return sum(value == 1 for value in self.defects) == 2

    @property
    def remaining_defect(self) -> int:
        bad = [value for value in self.defects if value != 1]
        return bad[0] if len(bad) == 1 else 10**18


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _parse_int(value: str, default: int = 10**18) -> int:
    try:
        return int(value)
    except Exception:
        return default


def load_source_candidates(paths: list[Path]) -> list[SourceCandidate]:
    candidates: list[SourceCandidate] = []
    for path in paths:
        for row in _read_csv(path):
            try:
                delta = Fraction(row["delta"])
                u = Fraction(row["u"])
                defects = (
                    int(row["defect_B"]),
                    int(row["defect_C"]),
                    int(row["defect_D"]),
                )
            except Exception:
                continue
            candidates.append(
                SourceCandidate(
                    delta=delta,
                    u=u,
                    defects=defects,
                    mcc_live=_parse_bool(row.get("mcc_live", "")),
                    point_in_unit=_parse_bool(row.get("point_in_unit", "")),
                    height=_parse_int(row.get("height", ""), default=10**12),
                )
            )
    return candidates


def select_deltas(candidates: list[SourceCandidate], max_deltas: int) -> list[Fraction]:
    selected: list[Fraction] = []
    seen: set[Fraction] = set()
    used_denominators: set[int] = set()

    def add(delta: Fraction) -> None:
        if delta not in seen and len(selected) < max_deltas:
            selected.append(delta)
            seen.add(delta)
            used_denominators.add(delta.denominator)

    for delta in DEFAULT_DELTAS:
        add(delta)

    ranked = sorted(
        candidates,
        key=lambda item: (
            not item.mcc_live,
            not item.point_in_unit,
            not item.two_good_one_bad,
            item.remaining_defect,
            item.delta.denominator in used_denominators,
            item.delta.denominator,
            item.height,
            item.delta.numerator,
        ),
    )
    for item in ranked:
        add(item.delta)
    return selected


def _known_us_by_delta_fiber(candidates: list[SourceCandidate]) -> dict[tuple[Fraction, str], list[Fraction]]:
    output: dict[tuple[Fraction, str], list[Fraction]] = defaultdict(list)
    for item in candidates:
        for label, defect in zip(("B", "C", "D"), item.defects):
            if defect == 1 and item.u not in output[(item.delta, label)]:
                output[(item.delta, label)].append(item.u)
    return output


def build_lite_curve_input(path: Path, deltas: list[Fraction], candidates: list[SourceCandidate]) -> None:
    known = _known_us_by_delta_fiber(candidates)
    rows: list[dict[str, Any]] = []
    for delta in deltas:
        for label in ("B", "C", "D"):
            curve = build_fiber_curve(label, delta, known.get((delta, label), []))
            rows.append(
                {
                    "delta": fraction_to_str(delta),
                    "fiber": label,
                    "curve_label": curve.label,
                    "polynomial": curve.polynomial,
                    "known_basepoints": ";".join(curve.known_basepoints),
                }
            )
    _write_csv(path, ["delta", "fiber", "curve_label", "polynomial", "known_basepoints"], rows)


def run_sage_lite(args: argparse.Namespace, selected: list[Fraction], curves_input: Path, curves_output: Path, points_output: Path) -> tuple[bool, str]:
    if args.dry_run:
        _write_csv(curves_output, [], [])
        _write_csv(points_output, ["delta", "fiber", "curve_label", "u", "W", "source", "n", "status"], [])
        return False, "dry_run"
    sage = shutil.which("sage")
    if not sage:
        return False, "sage executable not found"
    command = [
        sage,
        "research/four_distance/sage_fiber_rank.sage",
        "--all",
        "--max-multiple",
        str(args.max_multiple),
        "--combo-bound",
        str(args.combo_bound),
        "--strategic-only",
        "--sieve-primes",
        str(args.sieve_primes),
        "--curves-csv",
        str(curves_input),
        "--verified-csv",
        str(args.source_candidates),
        "--output-curves",
        str(curves_output),
        "--output-points",
        str(points_output),
    ]
    for delta in selected:
        command.extend(["--delta", fraction_to_str(delta)])
    result = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
    if result.returncode != 0:
        return False, result.stderr or result.stdout
    return True, result.stdout.strip()


def _rank_lookup(curves: list[dict[str, str]], delta: Fraction, fiber: str, field: str) -> str:
    delta_text = fraction_to_str(delta)
    for row in curves:
        if row.get("delta") == delta_text and row.get("fiber") == fiber:
            return row.get(field, "")
    return ""


def _fibers_with_basepoints(curves: list[dict[str, str]], delta: Fraction) -> str:
    delta_text = fraction_to_str(delta)
    labels = [row.get("fiber", "") for row in curves if row.get("delta") == delta_text and row.get("known_basepoints")]
    return "+".join(sorted(filter(None, labels)))


def _seed_defect(candidates: list[SourceCandidate], delta: Fraction) -> int | None:
    defects = [item.remaining_defect for item in candidates if item.delta == delta and item.two_good_one_bad]
    return min(defects) if defects else None


def _symmetry_chain(rows: list[dict[str, Any]]) -> bool:
    for i, left in enumerate(rows):
        try:
            x_left = Fraction(str(left["x"]))
            y_left = Fraction(str(left["y"]))
        except Exception:
            continue
        for right in rows[i + 1 :]:
            try:
                x_right = Fraction(str(right["x"]))
                y_right = Fraction(str(right["y"]))
            except Exception:
                continue
            if y_left == y_right and x_left + x_right == 1:
                return True
    return False


def summarize_delta(
    delta: Fraction,
    points_path: Path,
    curves: list[dict[str, str]],
    verified: list[dict[str, Any]],
    candidates: list[SourceCandidate],
    notes: str,
) -> dict[str, Any]:
    sets = load_u_sets(points_path, delta)
    U = {fiber: set(values) for fiber, values in sets.items()}
    intersections = {
        "BC": U["B"] & U["C"],
        "BD": U["B"] & U["D"],
        "CD": U["C"] & U["D"],
        "BCD": U["B"] & U["C"] & U["D"],
    }
    intersection_rows: list[dict[str, Any]] = []
    for label, values in intersections.items():
        source_fibers = set(label)
        for u in sorted(values):
            source_rows = {fiber: sets[fiber].get(u, []) for fiber in source_fibers}
            try:
                intersection_rows.append(verify_u(delta, u, source_fibers, source_rows))
            except ZeroDivisionError:
                continue

    delta_text = fraction_to_str(delta)
    delta_verified = [row for row in verified if row.get("delta") == delta_text]
    true_count = sum(1 for row in delta_verified if row.get("true_solution") is True)
    live_defects = [
        int(row["remaining_defect"])
        for row in delta_verified
        if row.get("two_good_one_bad") is True
        and row.get("mcc_live") is True
        and row.get("point_in_unit") is True
        and str(row.get("remaining_defect", "")).isdigit()
    ]
    best_live = min(live_defects) if live_defects else None
    seed_defect = _seed_defect(candidates, delta)
    improved = best_live is not None and seed_defect is not None and best_live < seed_defect
    return {
        "delta": delta_text,
        "fibers_with_basepoints": _fibers_with_basepoints(curves, delta),
        "B_rank": _rank_lookup(curves, delta, "B", "rank"),
        "B_rank_bounds": _rank_lookup(curves, delta, "B", "rank_bounds"),
        "C_rank": _rank_lookup(curves, delta, "C", "rank"),
        "C_rank_bounds": _rank_lookup(curves, delta, "C", "rank_bounds"),
        "D_rank": _rank_lookup(curves, delta, "D", "rank"),
        "D_rank_bounds": _rank_lookup(curves, delta, "D", "rank_bounds"),
        "UB_size": len(U["B"]),
        "UC_size": len(U["C"]),
        "UD_size": len(U["D"]),
        "UB_UC_size": len(intersections["BC"]),
        "UB_UD_size": len(intersections["BD"]),
        "UC_UD_size": len(intersections["CD"]),
        "triple_size": len(intersections["BCD"]),
        "true_solution_count": true_count,
        "best_live_in_unit_defect": best_live if best_live is not None else "",
        "improved_over_seed_defect": improved,
        "symmetry_chain_detected": _symmetry_chain(intersection_rows),
        "notes": notes,
    }


def write_report(path: Path, rows: list[dict[str, Any]], sage_ok: bool, sage_message: str, args: argparse.Namespace) -> None:
    true_deltas = [row["delta"] for row in rows if int(row.get("true_solution_count") or 0) > 0]
    triple_deltas = [row["delta"] for row in rows if int(row.get("triple_size") or 0) > 0]
    dense_deltas = [
        row["delta"]
        for row in rows
        if max(int(row.get("UB_UC_size") or 0), int(row.get("UB_UD_size") or 0), int(row.get("UC_UD_size") or 0)) > 2
    ]
    improved = [row["delta"] for row in rows if str(row.get("improved_over_seed_defect")) == "True"]
    sparse = [
        row["delta"]
        for row in rows
        if int(row.get("triple_size") or 0) == 0
        and max(int(row.get("UB_UC_size") or 0), int(row.get("UB_UD_size") or 0), int(row.get("UC_UD_size") or 0)) <= 2
    ]
    lines = [
        "# Delta Scan Lite Report",
        "",
        "## Summary",
        f"- deltas tested: {len(rows)}",
        f"- Sage run: {'yes' if sage_ok else 'no'}",
        f"- Sage message: {sage_message}",
        f"- max_multiple: {args.max_multiple}",
        f"- combo_bound: {args.combo_bound}",
        f"- sieve_primes: {args.sieve_primes}",
        f"- true solutions found: {', '.join(true_deltas) if true_deltas else 'none'}",
        f"- deltas with triple intersections: {', '.join(triple_deltas) if triple_deltas else 'none'}",
        f"- deltas with dense pairwise intersections: {', '.join(dense_deltas) if dense_deltas else 'none'}",
        f"- deltas with improvement over seed defect: {', '.join(improved) if improved else 'none'}",
        f"- deltas showing same sparse pattern as 289/260: {', '.join(sparse) if sparse else 'none'}",
        "",
        "## Per Delta Table",
        "",
        "| delta | base fibers | ranks B/C/D | |UB| | |UC| | |UD| | BC | BD | CD | BCD | true | best live defect | improved | symmetry | notes |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        ranks = "B:%s %s; C:%s %s; D:%s %s" % (
            row["B_rank"],
            row["B_rank_bounds"],
            row["C_rank"],
            row["C_rank_bounds"],
            row["D_rank"],
            row["D_rank_bounds"],
        )
        lines.append(
            "| {delta} | {fibers_with_basepoints} | {ranks} | {UB_size} | {UC_size} | {UD_size} | "
            "{UB_UC_size} | {UB_UD_size} | {UC_UD_size} | {triple_size} | {true_solution_count} | "
            "{best_live_in_unit_defect} | {improved_over_seed_defect} | {symmetry_chain_detected} | {notes} |".format(
                ranks=ranks,
                **row,
            )
        )
    lines.extend(["", "## Interpretation"])
    if true_deltas:
        lines.append("FOUND TRUE FOUR-DISTANCE SOLUTION in this finite lightweight delta scan. Inspect CSV rows.")
    else:
        lines.append("No true solution found in this finite lightweight delta scan.")
        lines.append("This is not a proof of non-existence.")
    if sparse and len(sparse) >= max(1, len(rows) // 2):
        lines.append("The completed rows suggest the sparse intersection pattern is not unique to delta=289/260.")
    if dense_deltas or triple_deltas:
        lines.append("Any dense or triple-intersection delta should be treated as a new priority target.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_scan(args: argparse.Namespace) -> tuple[Path, Path]:
    source_paths = [args.source_candidates]
    if args.reverse_one_sided.exists():
        source_paths.append(args.reverse_one_sided)
    candidates = load_source_candidates(source_paths)
    selected = [Fraction(delta) for delta in args.delta] if args.delta else select_deltas(candidates, args.max_deltas)

    args.data_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    curves_input = args.data_dir / "delta_scan_lite_input_curves.csv"
    curves_output = args.data_dir / "delta_scan_lite_curves.csv"
    points_output = args.data_dir / "delta_scan_lite_points.csv"
    verified_output = args.data_dir / "delta_scan_lite_verified_candidates.csv"
    if args.dry_run:
        summary_output = args.data_dir / "delta_scan_lite_dry_run_summary.csv"
        report_output = args.reports_dir / "delta_scan_lite_dry_run_report.md"
    else:
        summary_output = args.data_dir / "delta_scan_lite_summary.csv"
        report_output = args.reports_dir / "delta_scan_lite_report.md"

    build_lite_curve_input(curves_input, selected, candidates)
    sage_ok, sage_message = run_sage_lite(args, selected, curves_input, curves_output, points_output)
    curves = _read_csv(curves_output)
    if args.dry_run or not points_output.exists():
        _write_csv(verified_output, [], [])
        verified: list[dict[str, Any]] = []
        notes = "dry_run" if args.dry_run else "sage_not_run"
    else:
        verified, _stats = verify_sage_points(
            points_output,
            verified_output,
            primes=prime_list(args.sieve_primes),
            strategic_only=True,
        )
        notes = "ok" if sage_ok else "sage_failed"

    rows = [summarize_delta(delta, points_output, curves, verified, candidates, notes) for delta in selected]
    _write_csv(summary_output, SUMMARY_FIELDS, rows)
    write_report(report_output, rows, sage_ok, sage_message, args)
    return summary_output, report_output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delta", action="append")
    parser.add_argument("--max-deltas", type=int, default=10)
    parser.add_argument("--max-multiple", type=int, default=50)
    parser.add_argument("--combo-bound", type=int, default=10)
    parser.add_argument("--sieve-primes", type=int, default=1000)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source-candidates", type=Path, default=Path("research/four_distance/data/fiber_secant_candidates.csv"))
    parser.add_argument(
        "--reverse-one-sided",
        type=Path,
        default=Path("research/four_distance/data/reverse_nearmiss_one_sided_H1000.csv"),
    )
    parser.add_argument("--data-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    args = parser.parse_args()
    summary, report = run_scan(args)
    print(f"summary: {summary}")
    print(f"report: {report}")


if __name__ == "__main__":
    main()
