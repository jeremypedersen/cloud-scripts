# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-11
#
# Snapshot all EC2 instances in a specified region, so long as they are stopped
# 
# WARNING: As written, the script is designed to produce AMIs only for x86-64 instances
#
import boto3
import argparse
from datetime import datetime

#############
# Functions #
#############

def get_instance_name(instance):
    tags_dict = {tag['Key']: tag['Value'] for tag in instance.tags}
    return tags_dict.get('Name', 'untagged')

def take_snapshot(region_name):
    # Create EC2 resource and client
    ec2_resource = boto3.resource('ec2', region_name=region_name)
    ec2_client = boto3.client('ec2', region_name=region_name)

    # Get all stopped instances in the region
    instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])

    # Get current date and time
    current_datetime = datetime.now().strftime('%Y-%m-%d-%H-%M')

    for instance in instances:
        for volume in instance.volumes.all():
            # Create snapshot
            name = get_instance_name(instance)
            snapshot_name = f"{current_datetime}-{name}"
            snapshot = ec2_client.create_snapshot(VolumeId=volume.id, Description=f'Snapshot for {instance.id}', TagSpecifications=[{'ResourceType': 'snapshot', 'Tags': [{'Key': 'Name', 'Value': snapshot_name}]}])

            print(f"Snapshot created with ID {snapshot['SnapshotId']} for volume {volume.id} attached to instance {instance.id}.")

##################
# The real stuff #
##################

# Use argparse to 
parser = argparse.ArgumentParser(description="Take a snapshot of all disks attached to all stopped EC2 instances in the region.")
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region (ex: us-east-1)')
args = parser.parse_args()

take_snapshot(args.region)
print('Done!')