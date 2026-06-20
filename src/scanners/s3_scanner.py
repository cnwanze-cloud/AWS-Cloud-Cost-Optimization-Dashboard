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
