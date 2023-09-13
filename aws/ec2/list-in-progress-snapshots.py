# List all in-progress snapshots in a given region
# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-09-13
import boto3

def list_in_progress_snapshots(region):
    ec2 = boto3.client('ec2', region_name=region)
    
    # Get all snapshots in the region
    response = ec2.describe_snapshots(OwnerIds=['self'])
    snapshots = response['Snapshots']

    # Filter snapshots that are not yet complete
    in_progress_snapshots = [snap for snap in snapshots if snap['Progress'] != '100%']

    # Print in-progress snapshot details
    for snap in in_progress_snapshots:
        print(f"Snapshot ID: {snap['SnapshotId']}, Progress: {snap['Progress']}")

region = input("Please enter the AWS region (e.g., us-west-2): ").strip()
list_in_progress_snapshots(region)
