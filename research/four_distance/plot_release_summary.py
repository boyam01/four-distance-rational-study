#!/usr/bin/env python3
"""Generate release-summary plots for the four-distance artifact."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _int_cell(row: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(row.get(key, "") or default)
    except Exception:
        return default


def plot_defect_hist(data_dir: Path, plots_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = _read_csv(data_dir / "defect_summary_1000000.csv")[:15]
    labels = [row["defect"] for row in rows]
    counts = [_int_cell(row, "count") for row in rows]
    live_counts = [_int_cell(row, "mcc_live_count") for row in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = list(range(len(labels)))
    ax.bar(x, counts, label="all primitive oriented seeds", color="#4c78a8")
    ax.bar(x, live_counts, label="McCloskey-live", color="#f58518", alpha=0.8)
    ax.set_title("Top Defects in K2,2 Seed Scan (N <= 1,000,000)")
    ax.set_xlabel("squarefree defect")
    ax.set_ylabel("seed count")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(plots_dir / "defect_hist.png", dpi=180)
    plt.close(fig)


def plot_intersection(data_dir: Path, plots_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    point_rows = _read_csv(data_dir / "sage_fiber_points.csv")
    sets: dict[str, set[str]] = {"B": set(), "C": set(), "D": set()}
    for row in point_rows:
        if row.get("delta") != "289/260":
            continue
        fiber = row.get("fiber", "")
        if fiber in sets:
            sets[fiber].add(row.get("u", ""))
    counts = {
        "|U_B|": len(sets["B"]),
        "|U_C|": len(sets["C"]),
        "|U_D|": len(sets["D"]),
        "B∩C": len(sets["B"] & sets["C"]),
        "B∩D": len(sets["B"] & sets["D"]),
        "C∩D": len(sets["C"] & sets["D"]),
        "B∩C∩D": len(sets["B"] & sets["C"] & sets["D"]),
    }

    fig, ax = plt.subplots(figsize=(9, 5))
    labels = list(counts)
    values = [counts[label] for label in labels]
    colors = ["#54a24b", "#54a24b", "#54a24b", "#e45756", "#e45756", "#e45756", "#b279a2"]
    ax.bar(labels, values, color=colors)
    ax.set_title("Delta 289/260 Fiber u-set Intersections")
    ax.set_ylabel("exact u count")
    ax.set_yscale("symlog", linthresh=3)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(plots_dir / "intersection.png", dpi=180)
    plt.close(fig)


def plot_delta_scan(data_dir: Path, plots_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = _read_csv(data_dir / "delta_scan_lite_summary.csv")
    labels = [row["delta"] for row in rows]
    max_pair = [
        max(_int_cell(row, "UB_UC_size"), _int_cell(row, "UB_UD_size"), _int_cell(row, "UC_UD_size"))
        for row in rows
    ]
    triple = [_int_cell(row, "triple_size") for row in rows]

    fig, ax = plt.subplots(figsize=(11, 5))
    x = list(range(len(labels)))
    ax.bar(x, max_pair, label="max pairwise intersection", color="#72b7b2")
    ax.bar(x, triple, label="triple intersection", color="#e45756")
    ax.set_title("Lightweight Delta Scan Intersection Comparison")
    ax.set_xlabel("delta")
    ax.set_ylabel("intersection count")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(plots_dir / "delta_scan.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("research/four_distance/data"))
    parser.add_argument("--plots-dir", type=Path, default=Path("research/four_distance/plots"))
    args = parser.parse_args()
    args.plots_dir.mkdir(parents=True, exist_ok=True)
    plot_defect_hist(args.data_dir, args.plots_dir)
    plot_intersection(args.data_dir, args.plots_dir)
    plot_delta_scan(args.data_dir, args.plots_dir)
    print(f"wrote plots to {args.plots_dir}")


if __name__ == "__main__":
    main()
