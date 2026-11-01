
from resource_action_extractor import extract_resource_actions


def resource_map(directory):
    result = {}

    for record in extract_resource_actions(directory):
        key = (
            record["resource_type"],
            record["resource_label"],
        )

        actions = set()

        for statement in record.get("statements", []):
            if statement.get("effect") == "Allow":
                actions.update(statement.get("actions", []))

        result[key] = {
            **record,
            "actions": actions,
        }

    return result


def compare_resource_scopes(old_record, new_record):
    changes = []

    if not old_record or not new_record:
        return changes

    old_statements = old_record.get("statements", [])
    new_statements = new_record.get("statements", [])

    for old_statement in old_statements:
        for new_statement in new_statements:
            if old_statement.get("effect") != new_statement.get("effect"):
                continue

            if set(old_statement.get("actions", [])) != set(new_statement.get("actions", [])):
                continue

            old_resource = old_statement.get("resource")
            new_resource = new_statement.get("resource")

            if old_resource == new_resource:
                continue

            if new_resource == "*" and old_resource != "*":
                change_type = "POTENTIAL SCOPE EXPANSION"
            elif old_resource == "*" and new_resource != "*":
                change_type = "SCOPE RESTRICTION"
            else:
                change_type = "RESOURCE SCOPE CHANGED"

            changes.append({
                "actions": sorted(new_statement.get("actions", [])),
                "old_resource": old_resource,
                "new_resource": new_resource,
                "change_type": change_type,
            })

    return changes


def main():
    old = resource_map("fixtures/v1")
    new = resource_map("fixtures/v2")

    print("=== RESOURCE-LEVEL IAM REGRESSION REPORT ===")

    all_resources = sorted(set(old) | set(new))

    for key in all_resources:
        old_record = old.get(key)
        new_record = new.get(key)

        old_actions = old_record["actions"] if old_record else set()
        new_actions = new_record["actions"] if new_record else set()

        added = sorted(new_actions - old_actions)
        removed = sorted(old_actions - new_actions)

        if added or removed:
            resource_type, label = key
            print(f"\nResource: {resource_type}.{label}")

            if added:
                print("  Added actions:", added)
                print("  Evidence file:", new_record["file"])

            if removed:
                print("  Removed actions:", removed)

    print("\nNote: New permissions are potential security changes,")
    print("not proof of an exploitable privilege-escalation path.")


if __name__ == "__main__":
    main()

