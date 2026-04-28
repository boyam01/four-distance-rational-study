#!/usr/bin/env python3
"""Reverse closure raw-audit and near-miss defect landscape."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from functools import lru_cache
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

if __package__ in (None, ""):
    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.reverse_closure_search import (
        A0,
        D0,
        four_distance_squares,
        generate_S,
        point_to_integral,
        rational_square,
    )
    from research.four_distance.slope_tools import (
        fraction_height,
        fraction_to_str,
        in_S,
        is_square,
        mcc_gate,
        squarefree_part,
        valuation_to_str,
    )
else:
    from .reverse_closure_search import A0, D0, four_distance_squares, generate_S, point_to_integral, rational_square
    from .slope_tools import (
        fraction_height,
        fraction_to_str,
        in_S,
        is_square,
        mcc_gate,
        squarefree_part,
        valuation_to_str,
    )


TOP_FIELDS = [
    "category",
    "A",
    "D",
    "B",
    "C",
    "defect_B",
    "defect_C",
    "score",
    "B_in_S",
    "C_in_S",
    "one_sided",
    "both_small",
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
    "love_relation_ok",
    "four_distance_ok",
    "point_in_unit",
    "height",
    "distance_to_D0",
    "distance_to_A0",
    "notes",
]

RAW_FIELDS = [
    "A",
    "D",
    "B",
    "C",
    "reciprocal_fake",
    "degenerate_infinity",
    "nondegenerate",
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
    "love_relation_ok",
    "four_distance_ok",
    "point_in_unit",
    "notes",
]


def _fraction_key(text: str) -> Fraction:
    return Fraction(text)


@lru_cache(maxsize=None)
def slope_defect(alpha: Fraction) -> int:
    """Return squarefree_part(a^2+b^2) for reduced alpha=a/b."""
    n = alpha.numerator * alpha.numerator + alpha.denominator * alpha.denominator
    if is_square(n):
        return 1
    return squarefree_part(n)


def reverse_formula(A: Fraction, D: Fraction) -> tuple[Fraction, Fraction]:
    B = (A - 1) / (D - 1)
    C = D * (A - 1) / (A * (D - 1))
    return B, C


def is_reciprocal_fake(A: Fraction, D: Fraction, B: Fraction, C: Fraction) -> bool:
    return A != 0 and D == Fraction(1, 1) / A and B == -A and C == -Fraction(1, 1) / A


def _point_fields(A: Fraction, B: Fraction) -> dict[str, Any]:
    if A + B == 0:
        return {
            "x": "",
            "y": "",
            "N": "",
            "p": "",
            "q": "",
            "r": "",
            "s": "",
            "v3_x": "",
            "v3_yc": "",
            "mcc_live": False,
            "four_distance_ok": False,
            "point_in_unit": False,
            "notes": "degenerate_infinity",
        }
    x = Fraction(1, 1) / (A + B)
    y = A / (A + B)
    N, p, q, r, s = point_to_integral(x, y)
    gate = mcc_gate(N, p, q)
    four_ok, failures = four_distance_squares(x, y)
    point_in_unit = 0 < p < N and 0 < q < N
    if four_ok and point_in_unit:
        notes = "TRUE_SOLUTION"
    elif four_ok:
        notes = "rational_four_distance_outside_unit"
    else:
        notes = "algebraic_but_failed:" + ";".join(failures)
    return {
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
        "four_distance_ok": four_ok,
        "point_in_unit": point_in_unit,
        "notes": notes,
    }


def love_relation_ok(A: Fraction, D: Fraction, B: Fraction, C: Fraction) -> bool:
    return A * C == B * D == A + B - 1


def build_top_row(A: Fraction, D: Fraction, B: Fraction, C: Fraction, threshold: int, category: str) -> dict[str, Any]:
    defect_B = slope_defect(B)
    defect_C = slope_defect(C)
    point = _point_fields(A, B)
    return {
        "category": category,
        "A": fraction_to_str(A),
        "D": fraction_to_str(D),
        "B": fraction_to_str(B),
        "C": fraction_to_str(C),
        "defect_B": defect_B,
        "defect_C": defect_C,
        "score": defect_B * defect_C,
        "B_in_S": defect_B == 1,
        "C_in_S": defect_C == 1,
        "one_sided": (defect_B == 1) ^ (defect_C == 1),
        "both_small": defect_B <= threshold and defect_C <= threshold,
        **point,
        "love_relation_ok": love_relation_ok(A, D, B, C),
        "height": max(fraction_height(A), fraction_height(D), fraction_height(B), fraction_height(C)),
        "distance_to_D0": fraction_to_str(abs(D - D0)),
        "distance_to_A0": fraction_to_str(abs(A - A0)),
    }


def build_raw_row(A: Fraction, D: Fraction, B: Fraction, C: Fraction) -> dict[str, Any]:
    reciprocal = is_reciprocal_fake(A, D, B, C)
    infinity = A + B == 0
    nondegenerate = B != 0 and C != 0 and not infinity
    point = _point_fields(A, B)
    notes = "reciprocal_fake" if reciprocal else point["notes"]
    return {
        "A": fraction_to_str(A),
        "D": fraction_to_str(D),
        "B": fraction_to_str(B),
        "C": fraction_to_str(C),
        "reciprocal_fake": reciprocal,
        "degenerate_infinity": infinity,
        "nondegenerate": nondegenerate,
        **point,
        "love_relation_ok": love_relation_ok(A, D, B, C),
        "notes": notes,
    }


def _trim_top(rows: list[dict[str, Any]], key: Callable[[dict[str, Any]], tuple[Any, ...]], limit: int) -> list[dict[str, Any]]:
    if len(rows) <= limit * 4:
        return rows
    return sorted(rows, key=key)[:limit]


def _top_key_score(row: dict[str, Any]) -> tuple[Any, ...]:
    return (int(row["score"]), int(row["defect_B"]), int(row["defect_C"]), int(row["height"]), _fraction_key(row["distance_to_D0"]))


def _top_key_B1(row: dict[str, Any]) -> tuple[Any, ...]:
    return (int(row["defect_C"]), int(row["score"]), int(row["height"]), _fraction_key(row["distance_to_D0"]))


def _top_key_C1(row: dict[str, Any]) -> tuple[Any, ...]:
    return (int(row["defect_B"]), int(row["score"]), int(row["height"]), _fraction_key(row["distance_to_D0"]))


def _top_key_mcc(row: dict[str, Any]) -> tuple[Any, ...]:
    return (int(row["score"]), int(row["height"]), _fraction_key(row["distance_to_D0"]), _fraction_key(row["distance_to_A0"]))


def _top_key_730(row: dict[str, Any]) -> tuple[Any, ...]:
    return (_fraction_key(row["distance_to_D0"]), row["mcc_live"] != "True" and row["mcc_live"] is not True, int(row["height"]), _fraction_key(row["distance_to_A0"]))


def _jsonable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: str(value) for key, value in row.items()} for row in rows]


def _restore_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return rows


def _checkpoint_path(output_dir: Path, height: int) -> Path:
    return output_dir / f"reverse_nearmiss_H{height}.checkpoint.json"


def _write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def scan_nearmiss(
    height: int,
    output_dir: Path,
    reports_dir: Path,
    top: int,
    threshold: int,
    resume: bool,
    checkpoint: bool,
) -> tuple[dict[str, Any], dict[str, Path]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    slopes = generate_S(height)
    checkpoint_file = _checkpoint_path(output_dir, height)
    start_i = 0
    start_j = 0
    stats: dict[str, Any] = {
        "complete": False,
        "height": height,
        "S_size": len(slopes),
        "pairs_checked": 0,
        "raw_BC_in_S_count": 0,
        "reciprocal_fake_count": 0,
        "degenerate_infinity_count": 0,
        "nondegenerate_BC_in_S_count": 0,
        "true_solution_count": 0,
        "min_score": None,
        "min_defect_B": None,
        "min_defect_C": None,
        "one_sided_count": 0,
        "min_mcc_live_score": None,
        "last_i": 0,
        "last_j": 0,
        "timestamp": int(time.time()),
        "true_solution_found": False,
    }
    raw_rows: list[dict[str, Any]] = []
    top_score: list[dict[str, Any]] = []
    one_sided: list[dict[str, Any]] = []
    mcc_score: list[dict[str, Any]] = []
    closest_730: list[dict[str, Any]] = []

    if resume and checkpoint_file.exists():
        payload = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        if int(payload.get("height", -1)) != height:
            raise ValueError("checkpoint height mismatch")
        stats.update(payload["stats"])
        start_i = int(payload["last_i"])
        start_j = int(payload["last_j"]) + 1
        if start_j >= len(slopes):
            start_i += 1
            start_j = 0
        raw_rows = _restore_rows(payload.get("raw_rows", []))
        top_score = _restore_rows(payload.get("top_score", []))
        one_sided = _restore_rows(payload.get("one_sided", []))
        mcc_score = _restore_rows(payload.get("mcc_score", []))
        closest_730 = _restore_rows(payload.get("closest_730", []))

    progress_next = ((int(stats["pairs_checked"]) // 1_000_000) + 1) * 1_000_000

    for i in range(start_i, len(slopes)):
        A = slopes[i]
        j0 = start_j if i == start_i else 0
        for j in range(j0, len(slopes)):
            D = slopes[j]
            if A == 0 or D == 1:
                continue
            B, C = reverse_formula(A, D)
            row = build_top_row(A, D, B, C, threshold, "")
            stats["pairs_checked"] += 1
            score = int(row["score"])
            defect_B = int(row["defect_B"])
            defect_C = int(row["defect_C"])
            stats["min_score"] = score if stats["min_score"] is None else min(int(stats["min_score"]), score)
            stats["min_defect_B"] = defect_B if stats["min_defect_B"] is None else min(int(stats["min_defect_B"]), defect_B)
            stats["min_defect_C"] = defect_C if stats["min_defect_C"] is None else min(int(stats["min_defect_C"]), defect_C)

            top_score.append({**row, "category": "top_score"})
            top_score = _trim_top(top_score, _top_key_score, top)
            closest_730.append({**row, "category": "closest_730"})
            closest_730 = _trim_top(closest_730, _top_key_730, top)
            if row["one_sided"]:
                stats["one_sided_count"] += 1
                one_sided.append({**row, "category": "one_sided"})
                one_sided = _trim_top(one_sided, _top_key_B1 if row["B_in_S"] else _top_key_C1, top * 2)
            if row["mcc_live"]:
                stats["min_mcc_live_score"] = score if stats["min_mcc_live_score"] is None else min(int(stats["min_mcc_live_score"]), score)
                mcc_score.append({**row, "category": "mcc_live_score"})
                mcc_score = _trim_top(mcc_score, _top_key_mcc, top)

            if row["B_in_S"] and row["C_in_S"]:
                stats["raw_BC_in_S_count"] += 1
                raw = build_raw_row(A, D, B, C)
                raw_rows.append(raw)
                if raw["reciprocal_fake"]:
                    stats["reciprocal_fake_count"] += 1
                if raw["degenerate_infinity"]:
                    stats["degenerate_infinity_count"] += 1
                if raw["nondegenerate"]:
                    stats["nondegenerate_BC_in_S_count"] += 1
                if raw["notes"] == "TRUE_SOLUTION":
                    stats["true_solution_count"] += 1
                    stats["true_solution_found"] = True

            if stats["pairs_checked"] >= progress_next:
                print(f"progress: pairs_checked={stats['pairs_checked']}, i={i}, j={j}")
                progress_next += 1_000_000
                if checkpoint:
                    stats["last_i"] = i
                    stats["last_j"] = j
                    stats["timestamp"] = int(time.time())
                    _write_checkpoint(
                        checkpoint_file,
                        {
                            "height": height,
                            "last_i": i,
                            "last_j": j,
                            "stats": stats,
                            "raw_rows": _jsonable_rows(raw_rows),
                            "top_score": _jsonable_rows(sorted(top_score, key=_top_key_score)[:top]),
                            "one_sided": _jsonable_rows(sorted(one_sided, key=_top_key_score)[: top * 2]),
                            "mcc_score": _jsonable_rows(sorted(mcc_score, key=_top_key_mcc)[:top]),
                            "closest_730": _jsonable_rows(sorted(closest_730, key=_top_key_730)[:top]),
                        },
                    )

    stats["complete"] = True
    stats["last_i"] = len(slopes) - 1
    stats["last_j"] = len(slopes) - 1
    stats["timestamp"] = int(time.time())

    top_score = sorted(top_score, key=_top_key_score)[:top]
    B1 = [row for row in one_sided if row["B_in_S"]]
    C1 = [row for row in one_sided if row["C_in_S"]]
    one_sided = sorted(B1, key=_top_key_B1)[:top] + sorted(C1, key=_top_key_C1)[:top]
    mcc_score = sorted(mcc_score, key=_top_key_mcc)[:top]
    closest_730 = sorted(closest_730, key=_top_key_730)[:top]

    paths = {
        "raw": output_dir / f"reverse_nearmiss_H{height}.csv",
        "top_score": output_dir / f"reverse_nearmiss_top_score_H{height}.csv",
        "one_sided": output_dir / f"reverse_nearmiss_one_sided_H{height}.csv",
        "closest_730": output_dir / f"reverse_nearmiss_closest730_H{height}.csv",
        "mcc_score": output_dir / f"reverse_nearmiss_mcc_score_H{height}.csv",
        "report": reports_dir / f"reverse_nearmiss_H{height}.md",
    }
    _write_csv(paths["raw"], RAW_FIELDS, raw_rows)
    _write_csv(paths["top_score"], TOP_FIELDS, top_score)
    _write_csv(paths["one_sided"], TOP_FIELDS, one_sided)
    _write_csv(paths["closest_730"], TOP_FIELDS, closest_730)
    _write_csv(paths["mcc_score"], TOP_FIELDS, mcc_score)
    write_report(paths["report"], stats, top_score, one_sided, mcc_score, closest_730)

    if checkpoint:
        _write_checkpoint(
            checkpoint_file,
            {
                "height": height,
                "last_i": stats["last_i"],
                "last_j": stats["last_j"],
                "stats": stats,
                "raw_rows": _jsonable_rows(raw_rows),
                "top_score": _jsonable_rows(top_score),
                "one_sided": _jsonable_rows(one_sided),
                "mcc_score": _jsonable_rows(mcc_score),
                "closest_730": _jsonable_rows(closest_730),
            },
        )
    return stats, paths


def write_report(
    path: Path,
    stats: dict[str, Any],
    top_score: list[dict[str, Any]],
    one_sided: list[dict[str, Any]],
    mcc_score: list[dict[str, Any]],
    closest_730: list[dict[str, Any]],
) -> None:
    expected_fake = int(stats["S_size"]) - 1
    sanity_ok = int(stats["reciprocal_fake_count"]) == expected_fake
    min_score = stats["min_score"] if stats["min_score"] is not None else "none"
    min_defect_B = stats["min_defect_B"]
    min_defect_C = stats["min_defect_C"]
    min_mcc_score = stats["min_mcc_live_score"] if stats["min_mcc_live_score"] is not None else "none"
    closest = closest_730[0] if closest_730 else None

    lines = [
        "# Reverse Near-Miss Report",
        "",
        "## Summary",
        f"- height: {stats['height']}",
        f"- |S|: {stats['S_size']}",
        f"- A,D pairs checked: {stats['pairs_checked']}",
        f"- raw_BC_in_S_count: {stats['raw_BC_in_S_count']}",
        f"- reciprocal_fake_count: {stats['reciprocal_fake_count']}",
        f"- degenerate_infinity_count: {stats['degenerate_infinity_count']}",
        f"- nondegenerate_BC_in_S_count: {stats['nondegenerate_BC_in_S_count']}",
        f"- true_solution_count: {stats['true_solution_count']}",
        "",
        "## Sanity Check",
        "reciprocal fake divisor accounted for." if sanity_ok else f"WARNING: reciprocal_fake_count={stats['reciprocal_fake_count']} but expected |S|-1={expected_fake}.",
        "",
        "## Near-Miss Landscape",
        f"- min score: {min_score}",
        f"- min defect_B: {min_defect_B if min_defect_B is not None else 'none'}",
        f"- min defect_C: {min_defect_C if min_defect_C is not None else 'none'}",
        f"- one-sided closure present: {'yes' if int(stats['one_sided_count']) else 'no'}",
        f"- smallest mcc_live score: {min_mcc_score}",
        f"- closest to D0=451/87: {closest['D'] if closest else 'none'}"
        + (f" with defect_B={closest['defect_B']}, defect_C={closest['defect_C']}, distance={closest['distance_to_D0']}" if closest else ""),
        "",
        "### Top Score Candidates",
        "| A | D | B | C | defect_B | defect_C | score | mcc_live | notes |",
        "|---|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in top_score[:20]:
        lines.append(
            f"| {row['A']} | {row['D']} | {row['B']} | {row['C']} | {row['defect_B']} | {row['defect_C']} | {row['score']} | {row['mcc_live']} | {row['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
        ]
    )
    if int(stats["true_solution_count"]):
        lines.append("A true solution was found in this finite scan; inspect the certificate rows before making a mathematical claim.")
    else:
        lines.append(f"no true solution found up to this height ({stats['height']}).")
    lines.append("This is exact finite computation only and is not a global proof.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--top", type=int, default=200)
    parser.add_argument("--threshold", type=int, default=1000)
    parser.add_argument("--output-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--checkpoint", action="store_true")
    args = parser.parse_args()
    stats, paths = scan_nearmiss(args.height, args.output_dir, args.reports_dir, args.top, args.threshold, args.resume, args.checkpoint)
    print(json.dumps({key: str(value) for key, value in stats.items()}, indent=2))
    for label, path in paths.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
