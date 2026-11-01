
from regression_detector import compare_resource_scopes


def make_record(resource):
    return {
        "statements": [
            {
                "effect": "Allow",
                "actions": ["s3:GetObject"],
                "resource": resource,
            }
        ]
    }


def test_resource_scope_expansion():
    old = make_record("arn:aws:s3:::my-bucket/*")
    new = make_record("*")

    changes = compare_resource_scopes(old, new)

    assert len(changes) == 1
    assert changes[0]["change_type"] == "POTENTIAL SCOPE EXPANSION"


def test_resource_scope_restriction():
    old = make_record("*")
    new = make_record("arn:aws:s3:::my-bucket/*")

    changes = compare_resource_scopes(old, new)

    assert len(changes) == 1
    assert changes[0]["change_type"] == "SCOPE RESTRICTION"


def test_unchanged_resource_scope():
    old = make_record("arn:aws:s3:::my-bucket/*")
    new = make_record("arn:aws:s3:::my-bucket/*")

    changes = compare_resource_scopes(old, new)

    assert changes == []


def test_different_actions_are_not_matched():
    old = make_record("arn:aws:s3:::my-bucket/*")
    new = make_record("*")
    new["statements"][0]["actions"] = ["s3:PutObject"]

    changes = compare_resource_scopes(old, new)

    assert changes == []
