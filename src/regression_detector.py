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
