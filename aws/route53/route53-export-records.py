import boto3
from botocore.exceptions import ClientError

# Initialize a Route53 client
client = boto3.client('route53')

# Specify your hosted zone ID
hosted_zone_id = 'YOUR_HOSTED_ZONE_ID'

def export_route53_records(hosted_zone_id):
    try:
        # Initialize pagination
        paginator = client.get_paginator('list_resource_record_sets')

        # Create a PageIterator from the paginator
        page_iterator = paginator.paginate(HostedZoneId=hosted_zone_id)

        all_record_sets = []

        for page in page_iterator:
            # Retrieve each record set and append to the list
            for record_set in page['ResourceRecordSets']:
                print(record_set)  # or process the record_set as needed
                all_record_sets.append(record_set)

        return all_record_sets

    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

# Call the function to export the records
exported_records = export_route53_records(hosted_zone_id)

# Process or store the exported_records as needed, for example:
# print(exported_records)
