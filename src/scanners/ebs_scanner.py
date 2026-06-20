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
