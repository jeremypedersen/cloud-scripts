#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2024-02-04
#
# Export all the Route 53 records in a hosted zone
#
import boto3
import argparse
from botocore.exceptions import ClientError

# Initialize a Route53 client
client = boto3.client('route53')

####################
# Helper functions #
####################

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

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description="A script to export all records from a Route53 Hosted Zone")
parser.add_argument('-z', '--zone-id', type=str, required=True, help='ID of the hosted zone')

# Parse the command line arguments
args = parser.parse_args()

# Call the function to export the records
exported_records = export_route53_records(args.zone_id)

# Write output to file
with open('records.txt', 'w') as f:
    f.write(exported_records)
