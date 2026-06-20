import boto3
import datetime

# =========================
# AWS CLIENTS
# =========================
ec2 = boto3.client("ec2")
cloudwatch = boto3.client("cloudwatch")
rds = boto3.client("rds")
s3 = boto3.client("s3")
ses = boto3.client("ses")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("CostOptimizationFindings")

TODAY = str(datetime.date.today())

# =========================
# EC2 SCAN (ENRICHED)
# =========================
def scan_ec2():

    findings = []

    response = ec2.describe_instances()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:

            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]
            launch_time = instance["LaunchTime"]

            age_days = (datetime.datetime.now(datetime.timezone.utc) - launch_time).days

            if state == "stopped" and age_days > 7:

                findings.append({
                    "resource_id": instance_id,
                    "resource_type": "EC2",
                    "region": ec2.meta.region_name,
                    "finding": f"Stopped for {age_days} days",
                    "severity": "HIGH" if age_days > 30 else "MEDIUM",
                    "estimated_cost": "12"
                })

    return findings

# =========================
# EBS SCAN (COST AWARE)
# =========================
def scan_ebs():

    findings = []

    response = ec2.describe_volumes()

    for volume in response["Volumes"]:

        volume_id = volume["VolumeId"]
        size = volume["Size"]

        if len(volume["Attachments"]) == 0:

            cost = round(size * 0.10, 2)

            findings.append({
                "resource_id": volume_id,
                "resource_type": "EBS",
                "region": ec2.meta.region_name,
                "finding": "Unattached volume",
                "severity": "HIGH" if size > 100 else "MEDIUM",
                "estimated_cost": str(cost)
            })

    return findings

# =========================
# RDS SCAN (CLOUDWATCH POWERED)
# =========================
def scan_rds():

    findings = []

    response = rds.describe_db_instances()

    for db in response["DBInstances"]:

        db_id = db["DBInstanceIdentifier"]

        metrics = cloudwatch.get_metric_statistics(
            Namespace="AWS/RDS",
            MetricName="CPUUtilization",
            Dimensions=[
                {"Name": "DBInstanceIdentifier", "Value": db_id}
            ],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=7),
            EndTime=datetime.datetime.utcnow(),
            Period=86400,
            Statistics=["Average"]
        )

        datapoints = metrics.get("Datapoints", [])

        avg_cpu = (
            sum([d["Average"] for d in datapoints]) / len(datapoints)
            if datapoints else 0
        )

        if avg_cpu < 5:

            findings.append({
                "resource_id": db_id,
                "resource_type": "RDS",
                "region": "global",
                "finding": f"Low CPU usage ({avg_cpu:.2f}%)",
                "severity": "HIGH",
                "estimated_cost": "25"
            })

    return findings

# =========================
# S3 SCAN (AGE BASED)
# =========================
def scan_s3():

    findings = []

    response = s3.list_buckets()

    for bucket in response["Buckets"]:

        bucket_name = bucket["Name"]
        creation_date = bucket["CreationDate"]

        age_days = (datetime.datetime.now(datetime.timezone.utc) - creation_date).days

        if age_days > 90:

            findings.append({
                "resource_id": bucket_name,
                "resource_type": "S3",
                "region": "global",
                "finding": f"Old bucket ({age_days} days)",
                "severity": "LOW",
                "estimated_cost": "2"
            })

    return findings

# =========================
# REPORT GENERATION
# =========================
def generate_report(findings):

    report = "AWS COST OPTIMIZATION REPORT\n"
    report += "====================================\n\n"

    total = 0

    for item in findings:

        report += (
            f"[{item['severity']}] "
            f"{item['resource_type']} | "
            f"{item['resource_id']} | "
            f"{item['finding']} | "
            f"${item['estimated_cost']}\n"
        )

        total += float(item["estimated_cost"])

    report += f"\nTOTAL ESTIMATED WASTE: ${total:.2f}"

    return report

# =========================
# EMAIL SENDER
# =========================
def send_email(report):

    ses.send_email(
        Source="muelsir301@gmail.com",
        Destination={
            "ToAddresses": ["muelsir301@gmail.com"]
        },
        Message={
            "Subject": {
                "Data": "AWS Cost Optimization Report"
            },
            "Body": {
                "Text": {
                    "Data": report
                }
            }
        }
    )

# =========================
# LAMBDA HANDLER
# =========================
def lambda_handler(event, context):

    findings = []

    findings.extend(scan_ec2())
    findings.extend(scan_ebs())
    findings.extend(scan_rds())
    findings.extend(scan_s3())

    # store in DynamoDB
    for item in findings:
        item["scan_date"] = TODAY
        table.put_item(Item=item)

    report = generate_report(findings)

    send_email(report)

    return {
        "statusCode": 200,
        "body": report
    }


