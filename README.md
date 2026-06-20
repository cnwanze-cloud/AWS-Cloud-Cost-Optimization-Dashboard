# ☁️ Cloud Cost Optimization Dashboard

Automated AWS cost-governance system that scans your account daily, flags unused or idle resources, estimates wasted spend, and emails a report — fully serverless, fully scheduled, zero manual effort.

![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20EventBridge%20%7C%20DynamoDB%20%7C%20SES-orange?logo=amazon-aws)
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Architecture](https://img.shields.io/badge/Architecture-Serverless-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Overview

Cloud environments often accumulate unused or underutilized resources that silently increase operational costs. This project solves that problem by building an automated cost optimization engine using AWS serverless services.
The system performs daily scans across AWS resources, identifies waste, estimates financial impact, and sends structured reports to stakeholders.

---

## 🏗️ Architecture
<img width="2400" height="1600" alt="architecture" src="https://github.com/user-attachments/assets/abe0b4fa-3fe4-418d-a179-24d60bec9f5f" />


```
 EventBridge Scheduler (rate: 1 day)
            │
            ▼
        AWS Lambda
            │
   ┌────────┼────────┬─────────┬───────────────┐
   ▼        ▼        ▼         ▼               ▼
  EC2      EBS      RDS       S3         Cost Explorer
   │        │        │         │               │
   └────────┴────────┴─────────┴───────────────┘
                      │
                      ▼
                  DynamoDB
            (CostOptimizationFindings)
                      │
                      ▼
               Generate Report
                      │
                      ▼
                Amazon SES
              (Email Delivery)
```

**Flow:** EventBridge triggers Lambda on a daily schedule → Lambda scans EC2, EBS, RDS, and S3 for waste signals and queries Cost Explorer for spend data → findings are persisted in DynamoDB → a report is generated and emailed via SES.

---

## ✨ Features

| Resource | What It Detects |
|---|---|
| **EC2** | Stopped instances, idle running instances |
| **EBS** | Unattached ("available") volumes still incurring storage cost |
| **RDS** | Stopped or extremely low-utilization databases |
| **S3** | Buckets with no recent activity or minimal storage (cleanup candidates) |
| **Cost Explorer** | Monthly spend breakdown to estimate real dollar impact |

Every finding is timestamped and stored in DynamoDB, then rolled up into a daily report delivered automatically by email.

---

## 🧰 Tech Stack

- **Compute:** AWS Lambda (Python 3.14)
- **Scheduling:** Amazon EventBridge
- **Storage:** Amazon DynamoDB
- **Notifications:** Amazon SES
- **Cost Data:** AWS Cost Explorer API
- **SDK:** Boto3
- **IAM:** Least-privilege custom execution role

---

## 📁 Project Structure

```
cloud-cost-optimizer/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── template.yaml                 # (optional) SAM/CloudFormation IaC template
│
├── src/
│   └── lambda_function/
│       ├── __init__.py
│       ├── handler.py            # Lambda entry point (lambda_handler)
│       ├── scanners/
│       │   ├── __init__.py
│       │   ├── ec2_scanner.py
│       │   ├── ebs_scanner.py
│       │   ├── rds_scanner.py
│       │   └── s3_scanner.py
│       ├── cost_explorer.py      # Cost Explorer API queries
│       ├── findings_store.py     # DynamoDB read/write logic
│       ├── report_builder.py     # Report generation (text/HTML/CSV)
│       └── notifier.py           # SES email sending
│
├── tests/
│   ├── __init__.py
│   ├── test_ec2_scanner.py
│   ├── test_ebs_scanner.py
│   ├── test_rds_scanner.py
│   ├── test_s3_scanner.py
│   ├── test_report_builder.py
│   └── fixtures/
│       └── sample_findings.json
│
├── policies/
│   └── lambda-policy.json        # Custom IAM policy (least privilege)
│
├── infra/                        # Infrastructure-as-code (if not using template.yaml)
│   ├── dynamodb_table.tf
│   ├── eventbridge_rule.tf
│   ├── iam_role.tf
│   └── lambda.tf
│
├── docs/
│   ├── architecture.png
│   ├── sample-report.md
│   └── screenshots/
│       └── ses-email-example.png
│
└── .github/
    └── workflows/
        └── deploy.yml            # CI/CD: lint, test, package, deploy on push
```

---

## ⚙️ How It Works

1. **EventBridge** triggers the Lambda function once per day (`rate(1 day)`).
2. **Lambda** scans each AWS service for waste signals:
   - `ec2.describe_instances()` → stopped instances
   - `ec2.describe_volumes()` → unattached volumes
   - `rds.describe_db_instances()` → stopped databases
   - `s3.list_buckets()` → inactive/low-usage buckets
3. **Cost Explorer** (`ce.get_cost_and_usage()`) pulls real monthly spend to contextualize the findings.
4. **DynamoDB** stores every finding, keyed by `resource_id` (partition key) and `scan_date` (sort key), so historical trends can be tracked over time.
5. **Report generation** compiles the day's findings into a readable summary.
6. **SES** emails the report to a verified address — fully hands-off.

---

## 🚀 Setup & Deployment

### 1. Create the DynamoDB table
| Setting | Value |
|---|---|
| Table name | `CostOptimizationFindings` |
| Partition key | `resource_id` |
| Sort key | `scan_date` |

### 2. Verify an SES identity
SES Console → Verified Identities → Create Identity → Email Address → confirm the verification email.

### 3. Create the Lambda IAM role
Attach `AWSLambdaBasicExecutionRole`, plus a custom policy ([`policies/lambda-policy.json`](./policies/lambda-policy.json)) granting read access to EC2, EBS, RDS, S3, and Cost Explorer, and write access to DynamoDB and SES:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "rds:DescribeDBInstances",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "ce:GetCostAndUsage",
        "dynamodb:PutItem",
        "ses:SendEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4. Deploy the Lambda function
- **Runtime:** Python 3.13
- **Function name:** `cost-optimization-dashboard`
- Upload `lambda_function.py` and attach the IAM role above.

### 5. Schedule it with EventBridge
EventBridge → Create Rule → Schedule: `rate(1 day)` → Target: `cost-optimization-dashboard` Lambda function.

---

## 🧠 Skills Demonstrated

`AWS Lambda` · `Amazon EventBridge` · `Amazon DynamoDB` · `Amazon SES` · `AWS Cost Explorer API` · `Amazon EC2` · `Amazon EBS` · `Amazon RDS` · `Amazon S3` · `Python (Boto3)` · `Serverless Architecture` · `Infrastructure Monitoring` · `Cost Optimization Automation` · `Cloud Governance` · `Reporting Automation`

---

## 📄 License

This project is licensed under the MIT License — feel free to fork, adapt, and build on it.

---

*Built as a hands-on demonstration of automated cloud cost governance using native AWS serverless services.*
