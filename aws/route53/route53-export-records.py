import boto3
import argparse
from botocore.exceptions import ClientError

# Initialize a Route53 client
client = boto3.client('route53')

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

def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Export all records from an AWS Route53 hosted zone.")
    
    # Add the hosted_zone_id argument
    parser.add_argument("hosted_zone_id", help="The Hosted Zone ID of the AWS Route53 records you want to export.")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Call the function to export the records
    exported_records = export_route53_records(args.hosted_zone_id)
    
    # Process or store the exported_records as needed, for example:
    # print(exported_records)

if __name__ == "__main__":
    main()
