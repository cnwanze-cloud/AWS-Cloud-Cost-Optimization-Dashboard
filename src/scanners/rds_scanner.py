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
