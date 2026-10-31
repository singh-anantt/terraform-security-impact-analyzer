 do not prove exploitability.# Security-Impact Analysis of Terraform Module Upgrades

 ## 1. Problem Statement

 Terraform module upgrades can introduce unintended IAM permission expansion, trust relationship changes, and potential privilege-escalation risks. These changes may be difficult to identify through a normal configuration review.

 ## 2. Project Objective

 Develop a software-only static analysis tool that compares Terraform configurations before and after an upgrade and highlights potentially security-relevant changes before deployment.

 ## 3. Implemented Features

 - Detect added and removed IAM actions.
 - Compare IAM trust relationships between Terraform versions.
 - Report resource-level permission changes with evidence files.
 - Aggregate selected IAM actions across attached policies.
 - Detect heuristic managed-policy version risks.
 - Compare candidate policy-version findings between configurations.
 - Evaluate selected attack-path scenarios using synthetic graph fixtures.
 - Run repeatable evaluation scenarios and automated tests.

 ## 4. Project Workflow

 1. Read old and new Terraform configuration directories.
 2. Extract supported IAM actions and trust relationships.
 3. Compare configuration changes.
 4. Aggregate supported IAM actions across attached policies.
 5. Identify potential security-sensitive changes.
 6. Generate candidate findings with supporting evidence.
 7. Evaluate implemented checks against controlled scenarios.

 ## 5. Requirements

 - Python 3.9 or later
 - Checkov
 - python-hcl2
 - pytest

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
 python src/run_permission_evaluation.py
 ```

 Compare two Terraform configurations:

 ```bash
 python src/upgrade_analyzer.py --old fixtures/v1 --new fixtures/v2
 ```

 ## 8. Running Tests

 Run the automated test suite:

 ```bash
 python -m pytest -v
 ```

 Run preliminary risk metrics:

 ```bash
 python src/risk_metrics.py
 ```

 ## 9. Evaluation and Results

 The prototype was evaluated using controlled Terraform fixture scenarios.

 ### Functional Testing

 - Total automated tests: 20
 - Passed tests: 20
 - Failed tests: 0

 Tested scenarios include permission addition, permission removal, trust relationship changes, harmless configuration changes, split-policy permission aggregation, and selected attack-path scenarios.

 The permission evaluation script also passed 9 out of 9 controlled scenarios.

 ### Preliminary Risk Metrics

 Results from five controlled fixture pairs:

 | Metric | Result |
 |---|---:|
 | True Positives | 2 |
 | False Positives | 0 |
 | False Negatives | 0 |
 | True Negatives | 3 |
 | Accuracy | 100% |
 | Precision | 100% |
 | Recall | 100% |
 | F1-score | 100% |

 These results are preliminary and based on a small controlled fixture set. They do not represent real-world cloud security performance.

 ## 10. Comparison with Checkov

 Checkov version 3.3.30 was used as a baseline static-analysis tool.

 In the tested configurations, Checkov identified several IAM security misconfigurations, including wildcard resource permissions and privilege-escalation-related policy concerns.

 The proposed tool focuses on comparing old and upgraded Terraform configurations. It identifies added or removed IAM actions, trust relationship changes, and selected role-level candidate risks.

 The experiments demonstrate differences in analysis workflow and are not evidence that the proposed tool is superior to Checkov.

 ## 11. Limitations

 - Supports only implemented Terraform and IAM patterns.
 - Uses heuristic rules for managed-policy version risk detection.
 - Does not verify permissions against a live AWS account.
 - Some attack-path graph scenarios use synthetic fixtures.
 - Evaluation uses a limited set of controlled scenarios.
 - Findings are static-analysis candidates and do not prove exploitability.