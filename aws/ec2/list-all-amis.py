# List all AMIs (and linked snapshots) in a given region
# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-09-13
import boto3

def list_amis_and_snapshots(region):
    ec2 = boto3.resource('ec2', region_name=region)

    # Fetch all AMIs owned by the user
    my_amis = list(ec2.images.filter(Owners=['self']))

    # Print AMI details and their associated snapshot details
    for ami in my_amis:
        print(f"AMI ID: {ami.id}, AMI Name: {ami.name if ami.name else 'N/A'}")
        for block_device in ami.block_device_mappings:
            if 'Ebs' in block_device:
                snapshot_id = block_device['Ebs']['SnapshotId']
                print(f"\tEBS Volume: {block_device['DeviceName']}, Snapshot ID: {snapshot_id}")

region = input("Please enter an AWS region (e.g., us-west-2): ").strip()
list_amis_and_snapshots(region)
