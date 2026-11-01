












# Security-Impact Analysis of Terraform Module Upgrades

A software-only static analysis prototype that compares Terraform configurations before and after module upgrades to identify selected security-sensitive IAM changes before deployment.

## 1. Problem Statement

Terraform module upgrades can introduce unintended IAM permission expansion, trust relationship changes, and potentially risky authorization changes. These changes may be difficult to identify through ordinary configuration review.

## 2. Project Objective

Develop a static analysis tool that compares old and new Terraform configurations and highlights potentially security-relevant changes before deployment.

## 3. Implemented Features

- Detect added and removed IAM actions.
- Compare IAM trust relationships between Terraform versions.
- Identify selected resource-level permission changes.
- Detect potential IAM resource-scope expansion and restriction.
- Aggregate selected IAM actions across attached policies.
- Identify selected managed-policy version modification risks.
- Detect selected changes in synthetic attack-path graph scenarios.
- Identify redundant IAM policy detachment where an action remains available through another attached policy.
- Generate repeatable evaluation reports.

## 4. Project Workflow

1. Load old and new Terraform configuration directories.
2. Extract supported IAM actions and trust relationships.
3. Compare permission and trust changes.
4. Analyze selected resource scopes.
5. Aggregate supported actions across attached policies.
6. Identify potentially security-sensitive changes.
7. Report findings with available evidence.
8. Evaluate implemented functionality using controlled scenarios.

## 5. Requirements

- Python 3.9 or later
- python-hcl2
- pytest
- Checkov for the separately conducted baseline comparison

## 6. Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 7. Running the Project

Run the main analyzer:

```bash
python src/upgrade_analyzer.py
```

Run the permission evaluation:

```bash
PYTHONPATH=src python src/run_permission_evaluation.py
```

Compare two Terraform configurations:

```bash
python src/upgrade_analyzer.py --old fixtures/v1 --new fixtures/v2
```

## 8. Running Tests

Run the automated test suite:

```bash
PYTHONPATH=src python -m pytest -v
```

## 9. Evaluation and Results

The current evaluation uses 13 controlled scenarios (E01–E13).

| Evaluation measure | Result |
|---|---:|
| Scenarios evaluated | 13/13 |
| Evaluation checks passed | 21 |
| Evaluation checks failed | 0 |
| Automated pytest tests passed | 24/24 |
| Automated pytest tests failed | 0 |

### Scenarios Covered

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

### E13 Observation

The evaluation detected the removal of policy_a from app_role. The s3:GetObject action remained available through policy_b, so the aggregate role action set remained unchanged.

### Evaluation Output

The reproducible evaluation output is saved at:

`results/evaluation_E01_E13.txt`

The written evaluation summary is saved at:

`results/evaluation_summary.md`

These results demonstrate successful checks on the implemented controlled scenarios. Overall accuracy, precision, recall, and F1-score have not been calculated for the current evaluation.

## 10. Comparison with Checkov

Checkov version 3.3.30 was used as a baseline static-analysis tool in the earlier comparison.

The proposed prototype focuses on comparing old and upgraded Terraform configurations. Its analysis includes selected IAM action changes, trust relationship changes, resource-scope changes, and role-level candidate risks.

The comparison concerns differences in analysis workflow and scope. It does not establish that the proposed prototype is superior to Checkov.

## 11. Limitations

- Supports only the implemented Terraform and IAM patterns.
- The current IAM parser handles a limited fixture format and is not a complete Terraform or IAM policy evaluator.
- Role-level aggregation uses an action-set proxy and does not establish actual AWS effective permissions.
- Resource conditions, explicit deny precedence, permission boundaries, and session policies are not fully evaluated.
- E05 and E06 use synthetic graph fixtures, not Terraform-derived graphs.
- The managed-policy version risk detector uses heuristic rules.
- The prototype does not verify permissions against a live AWS account.
- The evaluation uses a limited set of controlled scenarios.
- Findings are static-analysis candidates and do not prove exploitability.