#!/usr/bin/env python3
"""Exact K2,2 Pythagorean-leg seed search."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.slope_tools import (
        SEED_CSV_FIELDS,
        certificate_lines,
        fraction_to_str,
        generate_pythagorean_adjacency,
        seed_csv_row,
        verify_seed,
    )
else:
    from .slope_tools import (
        SEED_CSV_FIELDS,
        certificate_lines,
        fraction_to_str,
        generate_pythagorean_adjacency,
        seed_csv_row,
        verify_seed,
    )


def _bool_value(value: str) -> bool:
    return value in ("True", "true", "1", "yes")


def _load_existing(csv_path: Path) -> tuple[set[tuple[int, int, int]], dict[str, int], int]:
    seen_oriented: set[tuple[int, int, int]] = set()
    canonical_first: dict[str, int] = {}
    max_row_id = 0
    if not csv_path.exists():
        return seen_oriented, canonical_first, max_row_id
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            N = int(row["N"])
            p = int(row["p"])
            q = int(row["q"])
            row_id = int(row["row_id"])
            key = row["canonical_key"]
            seen_oriented.add((N, p, q))
            canonical_first.setdefault(key, row_id)
            max_row_id = max(max_row_id, row_id)
    return seen_oriented, canonical_first, max_row_id


def _load_checkpoint(checkpoint_path: Path, resume: bool, limit_n: int) -> int:
    if not resume or not checkpoint_path.exists():
        return 0
    with checkpoint_path.open("r", encoding="utf-8") as handle:
        checkpoint = json.load(handle)
    if int(checkpoint.get("limit_n", -1)) != limit_n:
        raise ValueError("checkpoint limit_n mismatch")
    return int(checkpoint.get("q_index", 0))


def _save_checkpoint(checkpoint_path: Path, limit_n: int, q_index: int) -> None:
    tmp = checkpoint_path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump({"limit_n": limit_n, "q_index": q_index}, handle, indent=2)
    tmp.replace(checkpoint_path)


def search_k22(
    limit_n: int,
    output_dir: Path,
    primitive_only: bool,
    resume: bool,
    checkpoint_every: int,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"k22_seeds_N{limit_n}.csv"
    checkpoint_path = output_dir / f"k22_seeds_N{limit_n}.checkpoint.json"

    start = time.time()
    adjacency = generate_pythagorean_adjacency(limit_n)
    q_values = sorted(q for q in adjacency if 0 < q < limit_n)
    print(
        f"built adjacency: limit_n={limit_n}, nodes={len(adjacency)}, "
        f"edges={sum(len(v) for v in adjacency.values()) // 2}, seconds={time.time() - start:.3f}"
    )

    start_index = _load_checkpoint(checkpoint_path, resume, limit_n)
    seen_oriented, canonical_first, max_row_id = _load_existing(csv_path) if resume else (set(), {}, 0)
    mode = "a" if resume and csv_path.exists() else "w"
    row_id = max_row_id
    true_solution_found = False
    next_progress_q = ((q_values[start_index] // 10000) + 1) * 10000 if start_index < len(q_values) else limit_n + 1

    with csv_path.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SEED_CSV_FIELDS)
        if mode == "w":
            writer.writeheader()

        for q_index in range(start_index, len(q_values)):
            q = q_values[q_index]
            if q >= next_progress_q:
                print(f"progress: q={q}, q_index={q_index}/{len(q_values)}, rows={row_id}")
                while next_progress_q <= q:
                    next_progress_q += 10000

            q_neighbors = sorted(adjacency[q])
            for p in q_neighbors:
                if not (0 < p < limit_n):
                    continue
                p_neighbors = adjacency.get(p, set())
                for r in q_neighbors:
                    if r <= 0:
                        continue
                    N = p + r
                    if N > limit_n or q >= N:
                        continue
                    s = N - q
                    if s <= 0 or s >= N:
                        continue
                    if s not in p_neighbors:
                        continue
                    if primitive_only and math.gcd(math.gcd(p, q), N) != 1:
                        continue
                    oriented = (N, p, q)
                    if oriented in seen_oriented:
                        continue
                    seen_oriented.add(oriented)

                    seed = verify_seed(N, p, q)
                    if not seed.first_three_square:
                        raise ArithmeticError(f"internal adjacency error for {oriented}")
                    row_id += 1
                    canonical_key = f"{seed.canonical_key[0]}:{seed.canonical_key[1]}:{seed.canonical_key[2]}"
                    duplicate_of = ""
                    if canonical_key in canonical_first:
                        duplicate_of = str(canonical_first[canonical_key])
                    else:
                        canonical_first[canonical_key] = row_id
                    writer.writerow(seed_csv_row(seed, row_id, duplicate_of))

                    if seed.true_solution:
                        true_solution_found = True
                        print("FOUND TRUE FOUR-DISTANCE SOLUTION")
                        print("\n".join(certificate_lines(seed)))

            if checkpoint_every > 0 and (q_index + 1) % checkpoint_every == 0:
                _save_checkpoint(checkpoint_path, limit_n, q_index + 1)

    _save_checkpoint(checkpoint_path, limit_n, len(q_values))
    print(f"search complete: rows={row_id}, true_solution_found={true_solution_found}, csv={csv_path}")
    return csv_path


def _read_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _seed_line(row: dict[str, str]) -> str:
    return f"N={row['N']} (p,q,r,s)=({row['p']},{row['q']},{row['r']},{row['s']})"


def _known_seed_section() -> list[str]:
    lines = ["## Known Seed Verification", ""]
    for title, args in (("Seed A defect 17", (52, 45, 24)), ("Seed B defect 730", (867, 416, 780))):
        seed = verify_seed(*args)
        lines.extend([f"### {title}", "```text"])
        lines.extend(certificate_lines(seed))
        lines.extend(["```", ""])
    return lines


def write_reports(limit_n: int, data_dir: Path, reports_dir: Path, csv_path: Path) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    rows = _read_rows(csv_path)
    primitive_rows = [row for row in rows if _bool_value(row["primitive"])]
    true_rows = [row for row in primitive_rows if row["notes"] == "TRUE_SOLUTION"]
    seed_rows = [row for row in primitive_rows if row["notes"] == "THREE_DISTANCE_SEED"]
    live_rows = [row for row in seed_rows if _bool_value(row["mcc_live"])]

    by_defect: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in seed_rows:
        by_defect[int(row["defect"])].append(row)

    summary_path = data_dir / f"defect_summary_{limit_n}.csv"
    summary_fields = ["defect", "count", "min_N", "example_seed", "mcc_live_count", "min_live_N", "min_live_seed"]
    summary_rows: list[dict[str, Any]] = []
    for defect in sorted(by_defect):
        items = by_defect[defect]
        min_item = min(items, key=lambda row: (int(row["N"]), int(row["p"]), int(row["q"])))
        live_items = [row for row in items if _bool_value(row["mcc_live"])]
        min_live = min(live_items, key=lambda row: (int(row["N"]), int(row["p"]), int(row["q"]))) if live_items else None
        summary_rows.append(
            {
                "defect": defect,
                "count": len(items),
                "min_N": min_item["N"],
                "example_seed": _seed_line(min_item),
                "mcc_live_count": len(live_items),
                "min_live_N": min_live["N"] if min_live else "",
                "min_live_seed": _seed_line(min_live) if min_live else "",
            }
        )
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary_rows)

    min_defect_row = min(seed_rows, key=lambda row: (int(row["defect"]), int(row["N"]), int(row["p"]), int(row["q"]))) if seed_rows else None
    min_live_row = min(live_rows, key=lambda row: (int(row["defect"]), int(row["N"]), int(row["p"]), int(row["q"]))) if live_rows else None
    min_n_live_row = min(live_rows, key=lambda row: (int(row["N"]), int(row["defect"]), int(row["p"]), int(row["q"]))) if live_rows else None
    defect_counter = Counter(int(row["defect"]) for row in seed_rows)
    targets = [2, 3, 5, 6, 7, 10, 13, 17, 730]
    seed17 = [row for row in seed_rows if int(row["N"]) == 52 and int(row["p"]) == 45 and int(row["q"]) == 24]
    seed730 = [row for row in seed_rows if int(row["N"]) == 867 and int(row["p"]) == 416 and int(row["q"]) == 780]

    report_path = reports_dir / f"defect_summary_{limit_n}.md"
    lines: list[str] = []
    if true_rows:
        lines.append("FOUND TRUE FOUR-DISTANCE SOLUTION")
        first = true_rows[0]
        lines.extend(["", "```text"])
        lines.extend(certificate_lines(verify_seed(int(first["N"]), int(first["p"]), int(first["q"]))))
        lines.extend(["```", ""])

    lines.extend(
        [
            "# Four Distance K2,2 Seed Scan Report",
            "",
            "## Executive Summary",
            f"- Found true four-distance solution: {'yes' if true_rows else 'no'}",
            f"- Search LIMIT: N <= {limit_n}",
            f"- Primitive oriented three-distance seed count: {len(seed_rows)}",
            f"- Distinct defect count: {len(defect_counter)}",
            f"- Minimum defect: {min_defect_row['defect'] if min_defect_row else 'none'}",
            f"- Minimum defect seed: {_seed_line(min_defect_row) if min_defect_row else 'none'}",
            f"- Minimum live defect: {min_live_row['defect'] if min_live_row else 'none'}",
            f"- Minimum live defect seed: {_seed_line(min_live_row) if min_live_row else 'none'}",
            f"- Minimum N live seed: {_seed_line(min_n_live_row) if min_n_live_row else 'none'}",
            f"- 17 seed status: {'present; live=' + seed17[0]['mcc_live'] if seed17 else 'not present'}",
            f"- 730 seed status: {'present; live=' + seed730[0]['mcc_live'] if seed730 else 'not present'}",
            "",
        ]
    )
    lines.extend(_known_seed_section())
    lines.extend(["## Defect Distribution", ""])
    lines.append("| defect | count | min_N | example seed | mcc_live_count |")
    lines.append("|---:|---:|---:|---|---:|")
    for row in summary_rows[:40]:
        lines.append(f"| {row['defect']} | {row['count']} | {row['min_N']} | {row['example_seed']} | {row['mcc_live_count']} |")
    lines.extend(["", "Target low defects:", ""])
    for target in targets:
        lines.append(f"- defect={target}: {'present, count=' + str(defect_counter[target]) if target in defect_counter else 'absent'}")
    lines.extend(
        [
            "",
            "## McCloskey Gate Analysis",
            "",
            "The gate `v3(x) < 0 or v3(yc) < 0` is a necessary condition for a true four-distance solution in the centered rectangle model.",
            "For three-distance seeds it is only a live/dead computational label, not a proof of existence or non-existence.",
            f"- Seed 17 is {'live' if seed17 and _bool_value(seed17[0]['mcc_live']) else 'dead'} under this label.",
            f"- Seed 730 is {'live' if seed730 and _bool_value(seed730[0]['mcc_live']) else 'dead'} under this label.",
            f"- Live seed count: {len(live_rows)}",
            "",
            "## Slope Closure Analysis",
            "",
            "Known seeds satisfy `A*C = B*D = A+B-1`; their obstruction is exactly `D not in S`.",
            "",
        ]
    )
    for title, args in (("defect 17", (52, 45, 24)), ("defect 730", (867, 416, 780))):
        seed = verify_seed(*args)
        s = seed.slopes
        lines.append(
            f"- {title}: A={fraction_to_str(s.A)}, C={fraction_to_str(s.C)} -> "
            f"B={fraction_to_str(s.B)}, D={fraction_to_str(s.D)}, D_in_S={s.D_in_S}, defect={seed.defect}"
        )
    lines.extend(["", "Best low-defect D candidates from this K2,2 scan are the top rows in the defect table above.", ""])
    lines.extend(
        [
            "## Local 730 Search",
            "",
            "Run `python research/four_distance/local_730_search.py --height H --window-num 1 --window-den 100` for the real-near and 3-adic-compatible candidate tables.",
            "This K2,2 report does not treat a local-search miss as a theorem.",
            "",
            "## Elliptic Prep",
            "",
            "Run `python research/four_distance/elliptic_prep.py --delta 289/260` to generate fixed-delta cleared-denominator curve equations.",
            "Sage availability is optional and skipped without failing.",
            "",
            "## Conclusion",
            "",
        ]
    )
    if true_rows:
        lines.append("A true solution was found above; inspect the exact certificate before making any mathematical claim.")
    else:
        lines.append(f"No true four-distance solution was found up to N <= {limit_n} in this exact integer scan.")
        lines.append("This is computed evidence only; it is not a proof that no solution exists beyond the searched limit.")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote summary={summary_path}")
    print(f"wrote report={report_path}")
    return summary_path, report_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-n", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    parser.add_argument("--primitive-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=1000)
    args = parser.parse_args()

    csv_path = search_k22(
        limit_n=args.limit_n,
        output_dir=args.output_dir,
        primitive_only=args.primitive_only,
        resume=args.resume,
        checkpoint_every=args.checkpoint_every,
    )
    write_reports(args.limit_n, args.output_dir, args.reports_dir, csv_path)


if __name__ == "__main__":
    main()
