#!/usr/bin/env python3
"""Bridge Sage fiber rank output back into exact Python verification."""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
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
        DELTA_17,
        DELTA_730,
        U_17,
        U_730,
        A_of_u,
        B_of_u_delta,
        C_of_u_delta,
        D_of_u_delta,
        candidate_from_u,
        point_from_u_delta,
        slope_defect,
    )
    from research.four_distance.reverse_closure_search import four_distance_squares, point_to_integral
    from research.four_distance.modular_sieve_verifier import (
        defect_below_limit,
        prime_list,
        quadratic_residues_mod,
        slope_norm,
    )
    from research.four_distance.slope_tools import certificate_lines, fraction_to_str, verify_seed
    from research.four_distance.slope_tools import mcc_gate
else:
    from .fiber_secant_search import (
        DELTA_17,
        DELTA_730,
        U_17,
        U_730,
        A_of_u,
        B_of_u_delta,
        C_of_u_delta,
        D_of_u_delta,
        candidate_from_u,
        point_from_u_delta,
        slope_defect,
    )
    from .reverse_closure_search import four_distance_squares, point_to_integral
    from .modular_sieve_verifier import defect_below_limit, prime_list, quadratic_residues_mod, slope_norm
    from .slope_tools import certificate_lines, fraction_to_str, verify_seed
    from .slope_tools import mcc_gate


CURVE_FIELDS = [
    "delta",
    "fiber",
    "curve_label",
    "polynomial",
    "known_basepoints",
    "method_used",
    "elliptic_curve",
    "rank",
    "rank_bounds",
    "rank_bounds_before",
    "rank_bounds_after",
    "rank_certified",
    "torsion",
    "generators",
    "extra_generators_found",
    "saturation_status",
    "integral_model",
    "cremona_label",
    "combo_bound",
    "combinations_checked",
    "point_generation_status",
    "basepoint_warnings",
    "error",
]

POINT_FIELDS = ["delta", "fiber", "curve_label", "u", "W", "source", "n", "status"]

VERIFIED_FIELDS = [
    "delta",
    "fiber",
    "curve_label",
    "u",
    "W",
    "source",
    "A",
    "B",
    "C",
    "D",
    "defect_B",
    "defect_C",
    "defect_D",
    "two_good_one_bad",
    "remaining_defect",
    "score",
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


def two_good_one_bad(defects: tuple[int, int, int]) -> tuple[bool, int | None]:
    bad = [value for value in defects if value != 1]
    if len(bad) == 1:
        return True, bad[0]
    return False, None


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


def _placeholder_curves_from_fiber_secant(path: Path) -> list[dict[str, Any]]:
    rows = _read_csv(path)
    output: list[dict[str, Any]] = []
    for row in rows:
        output.append(
            {
                "delta": row.get("delta", ""),
                "fiber": row.get("curve_label", "").replace("_fiber", ""),
                "curve_label": row.get("curve_label", ""),
                "polynomial": row.get("polynomial", ""),
                "known_basepoints": row.get("known_basepoints", ""),
                "method_used": "skipped",
                "elliptic_curve": "",
                "rank": "",
                "rank_bounds": "",
                "rank_bounds_before": "",
                "rank_bounds_after": "",
                "rank_certified": "",
                "torsion": "",
                "generators": "",
                "extra_generators_found": "",
                "saturation_status": "",
                "integral_model": "",
                "cremona_label": "",
                "combo_bound": "",
                "combinations_checked": "",
                "point_generation_status": "sage_executable_not_found",
                "basepoint_warnings": "",
                "error": "Sage executable not found. Mordell-Weil rank/generator search not performed.",
            }
        )
    return output


def run_sage(args: argparse.Namespace, curves_path: Path, points_path: Path) -> tuple[bool, str]:
    sage = shutil.which("sage")
    if not sage:
        curves = _placeholder_curves_from_fiber_secant(args.curves_csv)
        _write_csv(curves_path, CURVE_FIELDS, curves)
        _write_csv(points_path, POINT_FIELDS, [])
        return False, "Sage executable not found. Mordell-Weil rank/generator search not performed."

    command = [
        sage,
        "research/four_distance/sage_fiber_rank.sage",
        "--max-multiple",
        str(args.max_multiple),
        "--output-curves",
        str(curves_path),
        "--output-points",
        str(points_path),
        "--curves-csv",
        str(args.curves_csv),
        "--verified-csv",
        str(args.data_dir / "sage_fiber_verified_candidates.csv"),
        "--combo-bound",
        str(args.combo_bound),
    ]
    if args.all:
        command.append("--all")
    if args.fiber:
        command.extend(["--fiber", args.fiber])
    for delta in args.delta or []:
        command.extend(["--delta", delta])
    if args.strategic_only:
        command.append("--strategic-only")
    if args.sieve_primes:
        command.extend(["--sieve-primes", str(args.sieve_primes)])
    if args.rank_diagnostic:
        command.append("--rank-diagnostic")
    result = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return True, result.stdout.strip()


def _new_stats() -> dict[str, int]:
    return {
        "total_candidates": 0,
        "rejected_by_mod_sieve": 0,
        "reached_exact_square_check": 0,
        "exact_square_success": 0,
        "exact_square_fail": 0,
        "strategic_rows_written": 0,
    }


def _approx_slope_norm_bits(alpha: Fraction) -> int:
    return 2 * max(abs(alpha.numerator).bit_length(), alpha.denominator.bit_length()) + 1


def _slope_squarehood(alpha: Fraction, primes: list[int], stats: dict[str, int] | None) -> tuple[bool, int, str]:
    a = alpha.numerator
    b = alpha.denominator
    for p in primes:
        if p <= 2:
            continue
        residue = ((a % p) * (a % p) + (b % p) * (b % p)) % p
        if residue not in quadratic_residues_mod(p):
            if stats is not None:
                stats["rejected_by_mod_sieve"] += 1
            return False, _approx_slope_norm_bits(alpha), f"failed_mod_{p}"
    if stats is not None:
        stats["reached_exact_square_check"] += 1
    n = a * a + b * b
    root = math.isqrt(n)
    if root * root == n:
        if stats is not None:
            stats["exact_square_success"] += 1
        return True, n.bit_length(), "exact_square"
    if stats is not None:
        stats["exact_square_fail"] += 1
    return False, n.bit_length(), "exact_not_square_after_sieve"


def _safe_slope_defect(alpha: Fraction, is_s: bool, bit_count: int, must_factor: bool, max_factor_bits: int) -> int | str:
    if is_s:
        return 1
    if must_factor:
        n = slope_norm(alpha)
        small = defect_below_limit(n, 729)
        if small is not None:
            return small
        if bit_count <= max_factor_bits:
            return slope_defect(alpha)
        return "no_small_defect_below_730"
    if bit_count <= max_factor_bits:
        return slope_defect(alpha)
    return "unfactored_bits_%s" % bit_count


def _fraction_output(value: Fraction, full: bool) -> str:
    if full:
        return fraction_to_str(value)
    return "omitted_fraction(num_bits=%s,den_bits=%s)" % (
        abs(value.numerator).bit_length(),
        value.denominator.bit_length(),
    )


def _int_output(value: int, full: bool) -> int | str:
    if full:
        return value
    return "omitted_int_bits_%s" % abs(value).bit_length()


def _short_cell(value: Any, limit: int = 96) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def verify_point_row(
    row: dict[str, str],
    max_factor_bits: int = 5000,
    primes: list[int] | None = None,
    stats: dict[str, int] | None = None,
    strategic_only: bool = False,
) -> dict[str, Any] | None:
    try:
        delta = Fraction(row["delta"])
        u = Fraction(row["u"])
    except Exception:
        return None
    try:
        A = A_of_u(u)
        B = B_of_u_delta(u, delta)
        C = C_of_u_delta(u, delta)
        D = D_of_u_delta(u, delta)
        x, y = point_from_u_delta(u, delta)
    except ZeroDivisionError:
        return None

    primes = primes or []
    row_fiber = row.get("fiber", "")
    if row_fiber == "B":
        B_square, B_bits, B_reason = True, 0, "fiber_point"
    else:
        B_square, B_bits, B_reason = _slope_squarehood(B, primes, stats)
    if row_fiber == "C":
        C_square, C_bits, C_reason = True, 0, "fiber_point"
    else:
        C_square, C_bits, C_reason = _slope_squarehood(C, primes, stats)
    if row_fiber == "D":
        D_square, D_bits, D_reason = True, 0, "fiber_point"
    else:
        D_square, D_bits, D_reason = _slope_squarehood(D, primes, stats)
    square_count = sum((B_square, C_square, D_square))
    must_factor = square_count >= 2
    defect_B = _safe_slope_defect(B, B_square, B_bits, must_factor, max_factor_bits)
    defect_C = _safe_slope_defect(C, C_square, C_bits, must_factor, max_factor_bits)
    defect_D = _safe_slope_defect(D, D_square, D_bits, must_factor, max_factor_bits)

    exact_defects = all(isinstance(value, int) for value in (defect_B, defect_C, defect_D))
    if exact_defects:
        defects = (int(defect_B), int(defect_C), int(defect_D))
        two_good, remaining = two_good_one_bad(defects)
        score: int | str = defects[0] * defects[1] * defects[2]
    else:
        two_good = square_count == 2
        remaining_values = [value for value in (defect_B, defect_C, defect_D) if value != 1]
        remaining = remaining_values[0] if len(remaining_values) == 1 else None
        score = ""

    if strategic_only and square_count < 2:
        return None

    N, p, q, r, s = point_to_integral(x, y)
    gate = mcc_gate(N, p, q)
    four_ok, failures = four_distance_squares(x, y)
    point_in_unit = 0 < p < N and 0 < q < N
    true_solution = B_square and C_square and D_square and four_ok and point_in_unit
    max_squarehood_bits = max(B_bits, C_bits, D_bits)
    full_output = true_solution or square_count >= 2 or max_squarehood_bits <= max_factor_bits
    if true_solution:
        print("FOUND TRUE FOUR-DISTANCE SOLUTION")
        print("\n".join(certificate_lines(verify_seed(N, p, q))))
    notes = "TRUE_SOLUTION" if true_solution else "near_miss"
    if failures:
        notes += ":" + ";".join(failures)
    if not exact_defects:
        notes += ";non_strategic_large_defect_not_factored"
    if not full_output:
        notes += ";large_exact_values_abbreviated"
    sieve_notes = []
    for label, reason in (("B", B_reason), ("C", C_reason), ("D", D_reason)):
        if reason.startswith("failed_mod_"):
            sieve_notes.append("%s_%s" % (label, reason))
    if sieve_notes:
        notes += ";sieve:" + ",".join(sieve_notes)
    return {
        "delta": fraction_to_str(delta),
        "fiber": row.get("fiber", ""),
        "curve_label": row.get("curve_label", ""),
        "u": _fraction_output(u, full_output),
        "W": row.get("W", "") if full_output else "omitted",
        "source": row.get("source", ""),
        "A": _fraction_output(A, full_output),
        "B": _fraction_output(B, full_output),
        "C": _fraction_output(C, full_output),
        "D": _fraction_output(D, full_output),
        "defect_B": defect_B,
        "defect_C": defect_C,
        "defect_D": defect_D,
        "two_good_one_bad": two_good,
        "remaining_defect": remaining if remaining is not None else "",
        "score": score,
        "x": _fraction_output(x, full_output),
        "y": _fraction_output(y, full_output),
        "N": _int_output(N, full_output),
        "p": _int_output(p, full_output),
        "q": _int_output(q, full_output),
        "r": _int_output(r, full_output),
        "s": _int_output(s, full_output),
        "mcc_live": gate.live,
        "point_in_unit": point_in_unit,
        "four_distance_ok": four_ok,
        "true_solution": true_solution,
        "notes": notes,
    }


def verify_sage_points(
    points_path: Path,
    verified_path: Path,
    primes: list[int] | None = None,
    strategic_only: bool = False,
    max_factor_bits: int = 5000,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows = _read_csv(points_path)
    strategic_u: set[str] | None = None
    if strategic_only:
        fibers_by_u: dict[str, set[str]] = {}
        for row in rows:
            u_text = row.get("u", "")
            if not u_text or u_text.startswith("omitted_fraction"):
                continue
            fibers_by_u.setdefault(u_text, set()).add(row.get("fiber", ""))
        strategic_u = {u_text for u_text, fibers in fibers_by_u.items() if len(fibers & {"B", "C", "D"}) >= 2}
    verified: list[dict[str, Any]] = []
    stats = _new_stats()
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        if strategic_u is not None and row.get("u", "") not in strategic_u:
            continue
        raw_key = (row.get("delta", ""), row.get("u", ""), row.get("fiber", ""))
        if raw_key in seen:
            continue
        seen.add(raw_key)
        stats["total_candidates"] += 1
        item = verify_point_row(
            row,
            max_factor_bits=max_factor_bits,
            primes=primes,
            stats=stats,
            strategic_only=strategic_only,
        )
        if item is None:
            continue
        if strategic_only and not item["true_solution"] and not item["two_good_one_bad"]:
            continue
        if item["true_solution"] or item["two_good_one_bad"]:
            stats["strategic_rows_written"] += 1
        verified.append(item)
    verified.sort(
        key=lambda row: (
            row["true_solution"] is not True,
            row["two_good_one_bad"] is not True,
            int(row["remaining_defect"] or 10**18)
            if str(row["remaining_defect"] or "").isdigit()
            else 10**18,
            int(row["score"]) if str(row["score"] or "").isdigit() else 10**18,
            row["mcc_live"] is not True,
            row["point_in_unit"] is not True,
        )
    )
    _write_csv(verified_path, VERIFIED_FIELDS, verified)
    return verified, stats


def write_report(
    report_path: Path,
    sage_available: bool,
    sage_message: str,
    curves: list[dict[str, str]],
    points: list[dict[str, str]],
    verified: list[dict[str, Any]],
    stats: dict[str, int],
    args: argparse.Namespace,
) -> None:
    true_rows = [row for row in verified if row["true_solution"] is True]
    two_good = [row for row in verified if row["two_good_one_bad"] is True]
    live_in_unit_two_good = [
        row
        for row in two_good
        if row["mcc_live"] is True and row["point_in_unit"] is True
    ]
    best_live = min(
        (
            int(row["remaining_defect"])
            for row in live_in_unit_two_good
            if str(row["remaining_defect"] or "").isdigit()
        ),
        default=None,
    )
    improved = best_live is not None and best_live < 730
    lines = [
        "# Sage Fiber Rank Report",
        "",
        "## Summary",
        f"- Sage available: {'yes' if sage_available else 'no'}",
        f"- curves processed: {len(curves)}",
        f"- Sage u points generated: {len(points)}",
        f"- verified candidates: {len(verified)}",
        f"- true_solution_count: {len(true_rows)}",
        f"- two_good_one_bad candidates: {len(two_good)}",
        f"- best live/in-unit two_good_one_bad defect: {best_live if best_live is not None else 'none'}",
        f"- 730 improvement status: {'IMPROVED_OVER_730' if improved else 'no improvement over 730 found in this run.'}",
        "",
        "## Scaled Mordell-Weil Search",
        f"- max_multiple: {args.max_multiple}",
        f"- combo_bound: {args.combo_bound}",
        f"- strategic_only: {args.strategic_only}",
        f"- sieve_primes: {args.sieve_primes}",
        f"- candidates generated: {len(points)}",
        f"- total candidates verified: {stats.get('total_candidates', 0)}",
        f"- modular sieve rejected: {stats.get('rejected_by_mod_sieve', 0)}",
        f"- exact square checks: {stats.get('reached_exact_square_check', 0)}",
        f"- exact square success: {stats.get('exact_square_success', 0)}",
        f"- exact square fail: {stats.get('exact_square_fail', 0)}",
        f"- true_solution_count: {len(true_rows)}",
        f"- two_good_one_bad count: {len(two_good)}",
        f"- best live/in-unit defect: {best_live if best_live is not None else 'none'}",
        f"- improved over 730: {'yes' if improved else 'no'}",
        "",
    ]
    if not sage_available:
        lines.extend([sage_message, ""])
    lines.extend(
        [
            "## Curves",
            "| delta | fiber | method | rank | rank_bounds | torsion | combo_bound | generated | point_generation_status |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in curves:
        lines.append(
            f"| {row.get('delta','')} | {row.get('fiber','')} | {row.get('method_used','')} | "
            f"{row.get('rank','')} | {row.get('rank_bounds','')} | {row.get('torsion','')} | "
            f"{row.get('combo_bound','')} | {row.get('combinations_checked','')} | {row.get('point_generation_status','')} |"
        )

    delta_rows = [row for row in curves if row.get("delta") == "289/260"]
    if delta_rows:
        point_counts: dict[str, int] = {}
        for item in points:
            if item.get("delta") == "289/260":
                point_counts[item.get("fiber", "")] = point_counts.get(item.get("fiber", ""), 0) + 1
        best_by_fiber: dict[str, dict[str, Any]] = {}
        for item in verified:
            if item.get("delta") != "289/260" or item.get("two_good_one_bad") is not True:
                continue
            fiber = str(item.get("fiber", ""))
            current = best_by_fiber.get(fiber)
            item_defect = int(item.get("remaining_defect") or 10**18)
            current_defect = int(current.get("remaining_defect") or 10**18) if current else 10**18
            if current is None or item_defect < current_defect:
                best_by_fiber[fiber] = item
        lines.extend(["", "## Delta 289/260 Fiber Results"])
        for fiber in ("B", "C", "D"):
            row = next((item for item in delta_rows if item.get("fiber") == fiber), None)
            if row is None:
                continue
            best = best_by_fiber.get(fiber)
            best_text = "none"
            if best:
                best_text = "u=%s defects=(%s,%s,%s) remaining=%s" % (
                    _short_cell(best.get("u", ""), 64),
                    best.get("defect_B", ""),
                    best.get("defect_C", ""),
                    best.get("defect_D", ""),
                    best.get("remaining_defect", ""),
                )
            lines.extend(
                [
                    "",
                    "### %s_fiber" % fiber,
                    "- polynomial: %s" % (row.get("polynomial") or "unavailable"),
                    "- known basepoints: %s" % (row.get("known_basepoints") or "none"),
                    "- rank: %s" % (row.get("rank") or "unavailable"),
                    "- rank_bounds: %s" % (row.get("rank_bounds") or "unavailable"),
                    "- torsion: %s" % (row.get("torsion") or "unavailable"),
                    "- generators: %s" % (row.get("generators") or "unavailable"),
                    "- combo_bound: %s" % (row.get("combo_bound") or "n/a"),
                    "- combinations checked: %s" % (row.get("combinations_checked") or "0"),
                    "- generated u count: %s" % point_counts.get(fiber, 0),
                    "- best two_good_one_bad from %s orbit: %s" % (fiber, best_text),
                ]
            )
            if row.get("basepoint_warnings"):
                lines.append("- basepoint warnings: %s" % row.get("basepoint_warnings"))

    chain_rows = []
    chain_seen = set()
    for row in verified:
        if row.get("delta") != "289/260" or row.get("two_good_one_bad") is not True:
            continue
        key = (
            row.get("u"),
            row.get("x"),
            row.get("y"),
            row.get("defect_B"),
            row.get("defect_C"),
            row.get("defect_D"),
        )
        if key in chain_seen:
            continue
        chain_seen.add(key)
        chain_rows.append(row)
    if chain_rows:
        lines.extend(["", "## Two-good-one-bad chain"])
        for index, row in enumerate(chain_rows[:50], start=1):
            lines.append(
                "%s. u=%s defects=(%s,%s,%s) P=(%s,%s) remaining=%s mcc_live=%s point_in_unit=%s"
                % (
                    index,
                    _short_cell(row.get("u", ""), 72),
                    row.get("defect_B", ""),
                    row.get("defect_C", ""),
                    row.get("defect_D", ""),
                    _short_cell(row.get("x", ""), 48),
                    _short_cell(row.get("y", ""), 48),
                    row.get("remaining_defect", ""),
                    row.get("mcc_live", ""),
                    row.get("point_in_unit", ""),
                )
            )

    lines.extend(
        [
            "",
            "## Rank Certification",
        ]
    )
    for row in curves:
        if row.get("fiber") not in ("B", "D"):
            continue
        bounds = row.get("rank_bounds", "")
        rank = row.get("rank", "")
        certified = "yes" if bounds and rank and bounds == f"({rank}, {rank})" else "no"
        lines.extend(
            [
                f"### {row.get('fiber')}_fiber",
                f"- rank_bounds before/after: {bounds}",
                f"- rank certified: {certified}",
                f"- generators used: {row.get('generators','')}",
                f"- saturation status: {row.get('saturation_status','') or 'not available'}",
                f"- extra generators found: {row.get('extra_generators_found','') or 'unknown'}",
            ]
        )
    lines.extend(
        [
            "",
            "## Improvement Status",
            "- true_solution_count: %s" % len(true_rows),
            "- best live/in-unit two_good_one_bad defect: %s" % (best_live if best_live is not None else "none"),
            "- improved over 730: %s" % ("yes" if improved else "no"),
        ]
    )
    lines.extend(
        [
            "",
            "## Best Verified Candidates",
            "| delta | fiber | u | defects | two_good_one_bad | mcc_live | point_in_unit | notes |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in verified[:30]:
        lines.append(
            f"| {row['delta']} | {row['fiber']} | {_short_cell(row['u'])} | "
            f"({row['defect_B']},{row['defect_C']},{row['defect_D']}) | {row['two_good_one_bad']} | "
            f"{row['mcc_live']} | {row['point_in_unit']} | {_short_cell(row['notes'])} |"
        )
    lines.extend(["", "## Conclusion"])
    if true_rows:
        lines.append("FOUND TRUE FOUR-DISTANCE SOLUTION. Inspect the exact certificate and verified CSV.")
    elif sage_available:
        lines.append("no true solution found in this finite Mordell-Weil/fiber run.")
        lines.append("This is not a proof of non-existence.")
    else:
        lines.append("Sage executable not found. Mordell-Weil rank/generator search not performed.")
        lines.append("No conclusion about the Sage fiber search is made.")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines) + "\n"
    report_path.write_text(content, encoding="utf-8")
    scaled_path = report_path.parent / "scaled_sage_fiber_report.md"
    if scaled_path != report_path:
        scaled_path.write_text(content, encoding="utf-8")
    print(f"wrote {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-sage", action="store_true")
    parser.add_argument("--from-sage-csv", type=Path)
    parser.add_argument("--delta", action="append")
    parser.add_argument("--fiber", choices=["B", "C", "D"], default="B")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--max-multiple", type=int, default=100)
    parser.add_argument("--combo-bound", type=int, default=20)
    parser.add_argument("--sieve-primes", type=int, default=0)
    parser.add_argument("--strategic-only", action="store_true")
    parser.add_argument("--factor-bit-threshold", type=int, default=5000)
    parser.add_argument("--rank-diagnostic", action="store_true")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--curves-csv", type=Path, default=Path("research/four_distance/data/fiber_secant_curves.csv"))
    parser.add_argument("--data-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    args = parser.parse_args()

    curves_path = args.data_dir / "sage_fiber_curves.csv"
    points_path = args.from_sage_csv or (args.data_dir / "sage_fiber_points.csv")
    verified_path = args.data_dir / "sage_fiber_verified_candidates.csv"
    report_path = args.reports_dir / "sage_fiber_rank_report.md"

    sage_available = False
    sage_message = ""
    if args.run_sage:
        sage_available, sage_message = run_sage(args, curves_path, points_path)
    elif not points_path.exists():
        _write_csv(points_path, POINT_FIELDS, [])

    curves = _read_csv(curves_path)
    points = _read_csv(points_path)
    if not args.run_sage:
        sage_available = any(
            row.get("method_used")
            and row.get("method_used") != "skipped"
            and row.get("point_generation_status") != "sage_executable_not_found"
            for row in curves
        )
    primes = prime_list(args.sieve_primes) if args.sieve_primes else []
    verified, stats = verify_sage_points(
        points_path,
        verified_path,
        primes=primes,
        strategic_only=args.strategic_only,
        max_factor_bits=args.factor_bit_threshold,
    )
    write_report(report_path, sage_available, sage_message, curves, points, verified, stats, args)
    print(f"curves: {curves_path}")
    print(f"points: {points_path}")
    print(f"verified: {verified_path}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
