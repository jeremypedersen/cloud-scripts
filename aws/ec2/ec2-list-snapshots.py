# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-11
#
# List all snapshots in a given region
#
import boto3
import argparse

#############
# Functions #
#############

def list_ebs_snapshots(region_name):
    # Create an EC2 client object using the specified region
    ec2_client = boto3.client('ec2', region_name=region_name)

    # Retrieve snapshots using describe_snapshots method
    snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])

    # Print the header
    print(f"Listing all EBS snapshots in region {region_name}:")

    for snap in snapshots['Snapshots']:
        print('-' * 60)
        print(f"Snapshot ID: {snap['SnapshotId']}\nProgress: {snap['Progress']}\nStatus: {snap['State']}")
        
##################
# The real stuff #
##################

# Use argparse to get the region name from the command line
parser = argparse.ArgumentParser(description='A script to list all snapshots in a specified region')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region name (ex: us-east-1)')

args = parser.parse_args()

list_ebs_snapshots(args.region)
print('-' * 60)
print('Done!')