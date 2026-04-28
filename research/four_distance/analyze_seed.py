#!/usr/bin/env python3
"""Analyze a single oriented seed exactly."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, os.fspath(Path(__file__).resolve().parents[2]))
    from research.four_distance.slope_tools import certificate_lines, verify_seed
else:
    from .slope_tools import certificate_lines, verify_seed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--N", type=int, required=True)
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--q", type=int, required=True)
    args = parser.parse_args()
    seed = verify_seed(args.N, args.p, args.q)
    print("\n".join(certificate_lines(seed)))


if __name__ == "__main__":
    main()
