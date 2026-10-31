
import json
from pathlib import Path
import hcl2


def inspect_file(file_path):
    with open(file_path, "r") as file:
        data = hcl2.load(file)

    print(f"\n=== {file_path} ===")
    print(json.dumps(data, indent=2, default=str))


inspect_file("fixtures/v1/main.tf")
inspect_file("fixtures/v2/main.tf")
