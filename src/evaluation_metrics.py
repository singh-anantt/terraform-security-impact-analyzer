import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation_dataset.csv"

sys.path.insert(0, str(ROOT / "src"))
from risk_prediction import predict_introduced_policy_risk

REQUIRED_COLUMNS = {
    "scenario_id",
    "scenario_name",
    "change_type",
    "expected_new_risk",
    "expected_permission_change",
    "expected_trust_change",
    "notes",
}


def load_dataset():
    with open(DATASET, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {sorted(missing)}")

        rows = list(reader)

    if not rows:
        raise ValueError("The evaluation dataset is empty.")

    ids = [row["scenario_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate scenario IDs found.")

    for row in rows:
        for column in (
            "expected_new_risk",
            "expected_permission_change",
            "expected_trust_change",
        ):
            if row[column] not in {"TRUE", "FALSE"}:
                raise ValueError(
                    f"Invalid Boolean value in {row['scenario_id']}: "
                    f"{column}={row[column]}"
                )

    return rows


def main():
    rows = load_dataset()

    print(f"Dataset: {DATASET.name}")
    print(f"Scenarios loaded: {len(rows)}")
    print("Dataset structure and labels: PASS")

    e03 = next(
        (row for row in rows if row["scenario_id"] == "E03"),
        None,
    )

    if e03 is None:
        raise ValueError("E03 is missing from the evaluation dataset.")

    old_dir = ROOT / "fixtures" / "risk_v1"
    new_dir = ROOT / "fixtures" / "risk_v2"

    prediction = predict_introduced_policy_risk(old_dir, new_dir)
    expected = e03["expected_new_risk"] == "TRUE"

    print("\n=== E03 Risk Prediction Evaluation ===")
    print("Expected new risk:", expected)
    print("Predicted new risk:", prediction)
    print("E03 result:", "PASS" if prediction == expected else "FAIL")
    print(
        "Scope: one tested policy-risk scenario; "
        "this is not an overall accuracy or F1-score."
    )


if __name__ == "__main__":
    main()
