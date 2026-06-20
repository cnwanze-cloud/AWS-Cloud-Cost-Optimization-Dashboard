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
