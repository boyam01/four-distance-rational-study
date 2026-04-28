import json
from pathlib import Path


def test_artifact_manifest_json_valid_and_paths_exist():
    path = Path("research/four_distance/ARTIFACT_MANIFEST.json")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["artifact"] == "unit-square-four-distance-exact-search"
    assert manifest["current_results"]["delta_289_260"]["true_solution_count"] == 0
    for section in ("scripts", "reports", "tests"):
        for item in manifest[section]:
            assert Path(item).exists(), item


def test_root_and_module_readmes_exist():
    assert Path("README.md").exists()
    assert Path("research/four_distance/README.md").exists()
    assert Path("research/four_distance/REPRODUCIBILITY.md").exists()
