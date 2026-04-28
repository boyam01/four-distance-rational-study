from argparse import Namespace
from pathlib import Path

from research.four_distance.delta_scan_lite import load_source_candidates, run_scan, select_deltas


def test_delta_scan_selects_default_deltas():
    candidates = load_source_candidates([Path("research/four_distance/data/fiber_secant_candidates.csv")])
    selected = select_deltas(candidates, max_deltas=6)
    assert [str(item) for item in selected] == [
        "13/6",
        "289/260",
        "867/416",
        "289/29",
        "332/255",
        "249/130",
    ]


def test_delta_scan_dry_run_one_delta(tmp_path):
    args = Namespace(
        delta=None,
        max_deltas=1,
        max_multiple=50,
        combo_bound=10,
        sieve_primes=1000,
        timeout=10,
        dry_run=True,
        source_candidates=Path("research/four_distance/data/fiber_secant_candidates.csv"),
        reverse_one_sided=Path("research/four_distance/data/reverse_nearmiss_one_sided_H1000.csv"),
        data_dir=tmp_path / "data",
        reports_dir=tmp_path / "reports",
    )
    summary, report = run_scan(args)
    assert summary.exists()
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "Delta Scan Lite Report" in text
    assert "dry_run" in text


def test_delta_scan_no_float_or_math_sqrt_exact_tests():
    source = Path("research/four_distance/delta_scan_lite.py").read_text(encoding="utf-8")
    assert "math.sqrt" not in source
    assert "float(" not in source
