#!/usr/bin/env python3
"""Prepare fixed-delta algebraic curve equations for later Sage work."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def _parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def _curve_lines(delta: Fraction) -> list[str]:
    try:
        import sympy as sp
    except Exception as exc:  # pragma: no cover - depends on environment
        return [f"sympy unavailable: {exc}"]

    u = sp.symbols("u")
    d = sp.Rational(delta.numerator, delta.denominator)
    A = 2 * u / (1 - u**2)
    expressions = {
        "C": d - 1 / A,
        "B": A * (d - 1),
        "D": (A * d - 1) / (A * (d - 1)),
    }
    lines = [f"## delta = {delta}", ""]
    lines.append("A = 2u/(1-u^2)")
    lines.append("")
    for name, expr in expressions.items():
        reduced = sp.together(expr)
        num, den = sp.fraction(reduced)
        curve = sp.factor(num**2 + den**2)
        den_sq = sp.factor(den**2)
        lines.extend(
            [
                f"### {name} in S",
                "",
                f"{name}(u) = ({sp.factor(num)}) / ({sp.factor(den)})",
                "",
                "Cleared denominator condition:",
                "",
                "```text",
                f"W_{name}^2 = {curve}",
                f"denominator_square = {den_sq}",
                "```",
                "",
            ]
        )
    return lines


def _sage_status() -> str:
    sage = shutil.which("sage")
    if not sage:
        return "Sage not found; genus/rank attempts skipped."
    try:
        result = subprocess.run([sage, "--version"], capture_output=True, text=True, timeout=20)
        return f"Sage available: {result.stdout.strip() or result.stderr.strip()}"
    except Exception as exc:  # pragma: no cover - environment dependent
        return f"Sage invocation failed; skipped: {exc}"


def write_elliptic_report(deltas: list[Fraction], reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    label = "_".join(f"{d.numerator}-{d.denominator}" for d in deltas)
    path = reports_dir / f"elliptic_prep_{label}.md"
    lines = [
        "# Elliptic Prep",
        "",
        "This file only prepares exact cleared-denominator curve equations.",
        "It does not assert rank, rational point completeness, or non-existence.",
        "",
        f"## Sage Status",
        "",
        _sage_status(),
        "",
    ]
    for delta in deltas:
        lines.extend(_curve_lines(delta))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {path}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delta", action="append", help="Fraction such as 289/260. Can be repeated.")
    parser.add_argument("--reports-dir", type=Path, default=Path("research/four_distance/reports"))
    args = parser.parse_args()
    if args.delta:
        deltas = [_parse_fraction(text) for text in args.delta]
    else:
        deltas = [Fraction(13, 6), Fraction(289, 260), Fraction(2), Fraction(3), Fraction(1, 2), Fraction(3, 2), Fraction(4, 3), Fraction(5, 4)]
    write_elliptic_report(deltas, args.reports_dir)


if __name__ == "__main__":
    main()
