
def compare_actions(old_actions, new_actions):
    return {
        "added": new_actions - old_actions,
        "removed": old_actions - new_actions,
    }


def test_permission_added():
    result = compare_actions(
        {"s3:GetObject"},
        {"s3:GetObject", "iam:CreatePolicyVersion"},
    )
    assert result["added"] == {"iam:CreatePolicyVersion"}
    assert result["removed"] == set()


def test_permission_removed():
    result = compare_actions(
        {"s3:GetObject", "s3:PutObject"},
        {"s3:GetObject"},
    )
    assert result["added"] == set()
    assert result["removed"] == {"s3:PutObject"}


def test_harmless_change():
    result = compare_actions(
        {"s3:GetObject"},
        {"s3:GetObject"},
    )
    assert result["added"] == set()
    assert result["removed"] == set()


if __name__ == "__main__":
    test_permission_added()
    test_permission_removed()
    test_harmless_change()
    print("PASS: All 3 regression cases.")
