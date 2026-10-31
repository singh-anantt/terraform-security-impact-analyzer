
import json
import re
from pathlib import Path


def extract_actions(file_path):
    text = Path(file_path).read_text()

    # Find the Action list in this initial controlled example.
    match = re.search(r'Action\s*=\s*\[(.*?)\]', text, re.DOTALL)
    if not match:
        return set()

    return set(re.findall(r'"([^"]+)"', match.group(1)))


old_file = "fixtures/v1/main.tf"
new_file = "fixtures/v2/main.tf"

old_actions = extract_actions(old_file)
new_actions = extract_actions(new_file)

added = new_actions - old_actions
removed = old_actions - new_actions

print("=== Terraform IAM Upgrade Comparison ===")
print("Old actions:", sorted(old_actions))
print("New actions:", sorted(new_actions))
print("Added actions:", sorted(added))
print("Removed actions:", sorted(removed))
