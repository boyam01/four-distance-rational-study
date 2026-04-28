#!/usr/bin/env python3
"""Draw an exactly verified seed or solution in the unit square."""

from __future__ import annotations

import argparse
import os
import sys
from fractions import Fraction
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.slope_tools import certificate_lines, fraction_to_str, verify_seed
else:
    from .slope_tools import certificate_lines, fraction_to_str, verify_seed


def _distance_label(square_value: int, root: int | None, N: int, fallback: str) -> str:
    if root is not None:
        return f"{root}/{N}"
    return f"{fallback}/{N}"


def plot_seed(N: int, p: int, q: int, output_dir: Path) -> Path:
    seed = verify_seed(N, p, q)
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(f"matplotlib is required for plotting: {exc}") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"seed_N{N}_p{p}_q{q}.png"

    x = Fraction(p, N)
    y = Fraction(q, N)
    xf = float(x)
    yf = float(y)
    corners = [
        ((0.0, 0.0), "(0,0)", _distance_label(seed.pq_sq, seed.h_pq, N, "")),
        ((1.0, 0.0), "(1,0)", _distance_label(seed.rq_sq, seed.h_rq, N, "")),
        ((0.0, 1.0), "(0,1)", _distance_label(seed.ps_sq, seed.h_ps, N, "")),
        ((1.0, 1.0), "(1,1)", _distance_label(seed.rs_sq, seed.h_rs, N, seed.fourth_factor)),
    ]

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="#222222", linewidth=1.6)
    ax.scatter([xf], [yf], s=90, color="#c23b22", zorder=5)
    ax.text(xf + 0.018, yf + 0.018, f"P=({fraction_to_str(x)}, {fraction_to_str(y)})", fontsize=10)

    for (cx, cy), name, label in corners:
        ax.scatter([cx], [cy], s=40, color="#1f4e79", zorder=4)
        ax.plot([xf, cx], [yf, cy], linestyle="--", linewidth=1.0, color="#5b6b7a")
        mx = (xf + cx) / 2
        my = (yf + cy) / 2
        ax.text(mx, my, label, fontsize=9, bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "#cccccc"})
        ax.text(cx + (0.015 if cx == 0 else -0.11), cy + (0.018 if cy == 0 else -0.045), name, fontsize=10)

    title = "TRUE FOUR-DISTANCE SOLUTION" if seed.true_solution else f"Three-distance seed, defect={seed.defect}"
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.08, 1.08)
    ax.grid(True, linewidth=0.4, alpha=0.35)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)

    print("\n".join(certificate_lines(seed)))
    print(f"wrote {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--N", type=int, required=True)
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--q", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("research/four_distance/reports"))
    args = parser.parse_args()
    plot_seed(args.N, args.p, args.q, args.output_dir)


if __name__ == "__main__":
    main()
