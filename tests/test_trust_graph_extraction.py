from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trust_graph import extract_trust_edges, compare_trust_edges


def test_terraform_trust_upgrade_detects_added_and_removed_edges():
    old_edges = extract_trust_edges(ROOT / "fixtures" / "v1" / "roles.tf")
    new_edges = extract_trust_edges(ROOT / "fixtures" / "v2" / "roles.tf")

    changes = compare_trust_edges(old_edges, new_edges)

    assert ("arn:aws:iam::111122223333:role/admin-role", "role:app-role") in changes["added"]
    assert ("arn:aws:iam::111122223333:user/developer", "role:app-role") in changes["removed"]
