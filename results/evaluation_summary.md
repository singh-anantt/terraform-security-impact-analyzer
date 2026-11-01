# Terraform Upgrade Security Evaluation

## Evaluation Overview

The prototype was evaluated on 13 controlled scenarios (E01–E13).

| Metric | Result |
|---|---:|
| Scenarios evaluated | 13/13 |
| Evaluation checks passed | 21 |
| Evaluation checks failed | 0 |
| Automated pytest tests passed | 24/24 |

## Scenarios Covered

- E01: Harmless variable addition
- E02: Ordinary S3 permission addition
- E03: Policy version modification actions
- E04: Trust relationship change
- E05: New administrative path
- E06: Existing administrative path unchanged
- E07: Permission removal
- E08: Combined permission and trust changes
- E09: Actions split across attached policies
- E10: S3 resource scope expansion
- E11: Harmless IAM policy tag change
- E12: IAM resource scope restriction
- E13: Redundant IAM policy detachment

## E13 Observation

The analyzer detected the removal of policy_a from app_role.
The s3:GetObject action remained available through policy_b.
Therefore, the aggregate role action set remained unchanged.

## Limitations

- E05 and E06 use synthetic graph fixtures, not Terraform-derived graphs.
- The IAM analysis supports a limited Terraform fixture format and is not a complete IAM policy evaluator.
- Aggregate Allow action-set comparison does not establish actual AWS effective permissions.
- Overall accuracy, precision, and recall have not been calculated.
- Passing controlled scenarios does not establish real-world detection performance.

## Conclusion

The evaluation demonstrates that the prototype can identify several
implemented categories of security-sensitive changes across controlled
Terraform upgrade scenarios. Further validation on broader Terraform
configurations and independently labelled datasets is required.
