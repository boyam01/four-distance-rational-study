#!/usr/bin/env python3
"""Reverse Love-closure search from A,D in the Pythagorean slope set S."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.slope_tools import (
        certificate_lines,
        fraction_height,
        fraction_to_str,
        generate_pythagorean_adjacency,
        in_S,
        is_square,
        mcc_gate,
        valuation_to_str,
        verify_seed,
    )
else:
    from .slope_tools import (
        certificate_lines,
        fraction_height,
        fraction_to_str,
        generate_pythagorean_adjacency,
        in_S,
        is_square,
        mcc_gate,
        valuation_to_str,
        verify_seed,
    )


A0 = Fraction(15, 8)
B0 = Fraction(87, 416)
C0 = Fraction(451, 780)
D0 = Fraction(451, 87)
RESIDUE_MODULI = (3, 9, 27, 5, 17, 73)


@dataclass(frozen=True)
class ReverseCandidate:
    A: Fraction
    D: Fraction
    B: Fraction
    C: Fraction
    x: Fraction
    y: Fraction
    N: int
    p: int
    q: int
    r: int
    s: int
    v3_x: int | object
    v3_yc: int | object
    mcc_live: bool
    love_relation_ok: bool
    four_distance_ok: bool
    point_in_unit: bool
    notes: str


def generate_S(height: int) -> list[Fraction]:
    """Generate reduced alpha=a/b in S with max(|a|,|b|)<=height."""
    slopes: set[Fraction] = {Fraction(0, 1)}
    adjacency = generate_pythagorean_adjacency(height)
    for a, neighbors in adjacency.items():
        if a > height:
            continue
        for b in neighbors:
            if b > height:
                continue
            value = Fraction(a, b)
            if max(abs(value.numerator), value.denominator) <= height:
                slopes.add(value)
                slopes.add(-value)
    return sorted(slopes)


def rational_square(value: Fraction) -> bool:
    """Return True iff value is a square in Q, using integer square tests."""
    if value < 0:
        return False
    return is_square(value.numerator) and is_square(value.denominator)


def four_distance_squares(x: Fraction, y: Fraction) -> tuple[bool, list[str]]:
    values = [
        ("x^2+y^2", x * x + y * y),
        ("(1-x)^2+y^2", (1 - x) * (1 - x) + y * y),
        ("x^2+(1-y)^2", x * x + (1 - y) * (1 - y)),
        ("(1-x)^2+(1-y)^2", (1 - x) * (1 - x) + (1 - y) * (1 - y)),
    ]
    failures = [name for name, value in values if not rational_square(value)]
    return (not failures, failures)


def nondegenerate(A: Fraction, D: Fraction, B: Fraction | None = None, C: Fraction | None = None) -> bool:
    if A == 0 or D == 1:
        return False
    if B is None or C is None:
        return True
    return B != 0 and C != 0 and A + B != 0


def point_to_integral(x: Fraction, y: Fraction) -> tuple[int, int, int, int, int]:
    N = math.lcm(x.denominator, y.denominator)
    p = x.numerator * (N // x.denominator)
    q = y.numerator * (N // y.denominator)
    return N, p, q, N - p, N - q


def reverse_candidate_from_AD(A: Fraction, D: Fraction) -> ReverseCandidate | None:
    """Build a reverse-closure candidate if it survives exact filters."""
    if not nondegenerate(A, D):
        return None
    B = (A - 1) / (D - 1)
    C = D * (A - 1) / (A * (D - 1))
    if not nondegenerate(A, D, B, C):
        return None
    if not in_S(B) or not in_S(C):
        return None
    x = Fraction(1, 1) / (A + B)
    y = A / (A + B)
    N, p, q, r, s = point_to_integral(x, y)
    gate = mcc_gate(N, p, q) if N > 0 else None
    love_relation_ok = A * C == B * D == A + B - 1
    four_ok, failures = four_distance_squares(x, y)
    point_in_unit = 0 < p < N and 0 < q < N
    if four_ok and point_in_unit:
        notes = "TRUE_SOLUTION"
    elif four_ok:
        notes = "rational_four_distance_outside_unit"
    else:
        notes = "algebraic_but_failed:" + ";".join(failures)
    return ReverseCandidate(
        A=A,
        D=D,
        B=B,
        C=C,
        x=x,
        y=y,
        N=N,
        p=p,
        q=q,
        r=r,
        s=s,
        v3_x=gate.v3_x if gate else "",
        v3_yc=gate.v3_yc if gate else "",
        mcc_live=gate.live if gate else False,
        love_relation_ok=love_relation_ok,
        four_distance_ok=four_ok,
        point_in_unit=point_in_unit,
        notes=notes,
    )


def _fraction_mod(frac: Fraction, modulus: int) -> str:
    numerator = frac.numerator % modulus
    denominator = frac.denominator % modulus
    if math.gcd(frac.denominator, modulus) == 1:
        return str((numerator * pow(denominator, -1, modulus)) % modulus)
    return f"nonunit:{numerator}/{denominator}"


def residue_columns(A: Fraction, D: Fraction) -> dict[str, str]:
    row: dict[str, str] = {}
    for modulus in RESIDUE_MODULI:
        row[f"A_mod_{modulus}"] = _fraction_mod(A, modulus)
        row[f"D_mod_{modulus}"] = _fraction_mod(D, modulus)
    return row


def candidate_row(candidate: ReverseCandidate, modular_residue: bool) -> dict[str, Any]:
    row: dict[str, Any] = {
        "A": fraction_to_str(candidate.A),
        "D": fraction_to_str(candidate.D),
        "B": fraction_to_str(candidate.B),
        "C": fraction_to_str(candidate.C),
        "x": fraction_to_str(candidate.x),
        "y": fraction_to_str(candidate.y),
        "N": candidate.N,
        "p": candidate.p,
        "q": candidate.q,
        "r": candidate.r,
        "s": candidate.s,
        "v3_x": valuation_to_str(candidate.v3_x),
        "v3_yc": valuation_to_str(candidate.v3_yc),
        "mcc_live": candidate.mcc_live,
        "love_relation_ok": candidate.love_relation_ok,
        "four_distance_ok": candidate.four_distance_ok,
        "point_in_unit": candidate.point_in_unit,
        "height": max(
            fraction_height(candidate.A),
            fraction_height(candidate.D),
            fraction_height(candidate.B),
            fraction_height(candidate.C),
        ),
        "distance_to_D0": fraction_to_str(abs(candidate.D - D0)),
        "distance_to_A0": fraction_to_str(abs(candidate.A - A0)),
        "notes": candidate.notes,
    }
    if modular_residue:
        row.update(residue_columns(candidate.A, candidate.D))
    return row


def _fieldnames(modular_residue: bool) -> list[str]:
    fields = [
        "A",
        "D",
        "B",
        "C",
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
    if modular_residue:
        for modulus in RESIDUE_MODULI:
            fields.extend([f"A_mod_{modulus}", f"D_mod_{modulus}"])
    return fields


def _checkpoint_path(output_csv: Path) -> Path:
    return output_csv.with_suffix(".checkpoint.json")


def _write_checkpoint(
    output_csv: Path,
    height: int,
    pairs_checked: int,
    last_i: int,
    last_j: int,
    true_solution_found: bool,
    complete: bool,
) -> None:
    path = _checkpoint_path(output_csv)
    tmp = path.with_suffix(".tmp")
    payload = {
        "complete": complete,
        "height": height,
        "pairs_checked": pairs_checked,
        "last_i": last_i,
        "last_j": last_j,
        "timestamp": int(time.time()),
        "true_solution_found": true_solution_found,
    }
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def _read_checkpoint(output_csv: Path, height: int) -> dict[str, Any] | None:
    path = _checkpoint_path(output_csv)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if int(payload.get("height", -1)) != height:
        raise ValueError("checkpoint height mismatch")
    return payload


def _read_existing_rows(output_csv: Path) -> list[dict[str, str]]:
    if not output_csv.exists():
        return []
    with output_csv.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def reverse_search(
    height: int,
    output_csv: Path,
    guided_730: bool,
    modular_residue: bool,
    resume: bool,
    checkpoint_every: int,
) -> tuple[Path, list[dict[str, str]], dict[str, Any]]:
    slopes = generate_S(height)
    checkpoint = _read_checkpoint(output_csv, height) if resume else None
    if checkpoint and checkpoint.get("complete") is True:
        rows = _read_existing_rows(output_csv)
        stats = {
            "height": height,
            "S_size": len(slopes),
            "pairs_checked": int(checkpoint["pairs_checked"]),
            "candidate_count": len(rows),
            "true_solution_count": sum(1 for row in rows if row["notes"] == "TRUE_SOLUTION"),
            "mcc_live_count": sum(1 for row in rows if row["mcc_live"] == "True"),
            "nondegenerate_candidate_count": len(rows),
        }
        return output_csv, rows, stats

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if resume and output_csv.exists() else "w"
    rows: list[dict[str, Any]] = []
    pairs_checked = int(checkpoint["pairs_checked"]) if checkpoint else 0
    true_solution_found = bool(checkpoint.get("true_solution_found")) if checkpoint else False
    start_i = int(checkpoint["last_i"]) if checkpoint else 0
    start_j = int(checkpoint["last_j"]) + 1 if checkpoint else 0
    if start_j >= len(slopes):
        start_i += 1
        start_j = 0

    with output_csv.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=_fieldnames(modular_residue))
        if mode == "w":
            writer.writeheader()
        for i in range(start_i, len(slopes)):
            A = slopes[i]
            j0 = start_j if i == start_i else 0
            for j in range(j0, len(slopes)):
                D = slopes[j]
                pairs_checked += 1
                candidate = reverse_candidate_from_AD(A, D)
                if candidate is None:
                    if checkpoint_every and pairs_checked % checkpoint_every == 0:
                        _write_checkpoint(output_csv, height, pairs_checked, i, j, true_solution_found, False)
                    continue
                row = candidate_row(candidate, modular_residue)
                writer.writerow(row)
                rows.append(row)
                if candidate.notes == "TRUE_SOLUTION":
                    true_solution_found = True
                    print("FOUND TRUE SOLUTION certificate")
                    print("\n".join(certificate_lines(verify_seed(candidate.N, candidate.p, candidate.q))))
                if checkpoint_every and pairs_checked % checkpoint_every == 0:
                    _write_checkpoint(output_csv, height, pairs_checked, i, j, true_solution_found, False)

    existing = _read_existing_rows(output_csv)
    _write_checkpoint(output_csv, height, pairs_checked, len(slopes) - 1, len(slopes) - 1, true_solution_found, True)
    stats = {
        "height": height,
        "S_size": len(slopes),
        "pairs_checked": pairs_checked,
        "candidate_count": len(existing),
        "true_solution_count": sum(1 for row in existing if row["notes"] == "TRUE_SOLUTION"),
        "mcc_live_count": sum(1 for row in existing if row["mcc_live"] == "True"),
        "nondegenerate_candidate_count": len(existing),
        "guided_730": guided_730,
        "modular_residue": modular_residue,
    }
    return output_csv, existing, stats


def _sort_guided(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        rows,
        key=lambda row: (
            Fraction(row["distance_to_D0"]),
            row["mcc_live"] != "True",
            int(row["height"]),
            Fraction(row["distance_to_A0"]),
        ),
    )


def write_report(height: int, rows: list[dict[str, str]], stats: dict[str, Any], reports_dir: Path, guided_730: bool) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"reverse_closure_H{height}.md"
    true_rows = [row for row in rows if row["notes"] == "TRUE_SOLUTION"]
    live_rows = [row for row in rows if row["mcc_live"] == "True"]
    guided_rows = _sort_guided(rows)[:25]
    lines = [
        "# Reverse Closure Search Report",
        "",
        f"- height: {height}",
        f"- |S|: {stats['S_size']}",
        f"- A,D pairs checked: {stats['pairs_checked']}",
        f"- B,C in S candidates: {stats['candidate_count']}",
        f"- true four-distance solutions found: {stats['true_solution_count']}",
        f"- mcc_live candidate count: {stats['mcc_live_count']}",
        f"- nondegenerate candidates: {stats['nondegenerate_candidate_count']}",
        f"- guided_730 sorting requested: {guided_730}",
        "",
    ]
    if true_rows:
        lines.append("FOUND TRUE SOLUTION")
    else:
        lines.append(f"no true solution found up to this height ({height})")
    lines.extend(
        [
            "",
            "## Closest-to-730 D Candidates",
            "",
            "| A | D | B | C | distance_to_D0 | mcc_live | height | N | p | q | notes |",
            "|---|---|---|---|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in guided_rows:
        lines.append(
            f"| {row['A']} | {row['D']} | {row['B']} | {row['C']} | {row['distance_to_D0']} | "
            f"{row['mcc_live']} | {row['height']} | {row['N']} | {row['p']} | {row['q']} | {row['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This is exact finite computation over generated slopes only. It is not a proof of global non-existence.",
            "Residue columns, when enabled, are diagnostic labels only and are not used as theorems.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    parser.add_argument("--guided-730", action="store_true")
    parser.add_argument("--modular-residue", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=100000)
    args = parser.parse_args()

    output_csv = args.output_dir / f"reverse_closure_H{args.height}.csv"
    csv_path, rows, stats = reverse_search(
        height=args.height,
        output_csv=output_csv,
        guided_730=args.guided_730,
        modular_residue=args.modular_residue,
        resume=args.resume,
        checkpoint_every=args.checkpoint_every,
    )
    print(f"wrote {csv_path}")
    write_report(args.height, rows, stats, args.reports_dir, args.guided_730)


if __name__ == "__main__":
    main()
