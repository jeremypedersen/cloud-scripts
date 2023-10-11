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

def take_snapshot_and_register_ami(region_name):
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
            snapshot_name = f"{current_datetime}-{instance.tags['Name']}"
            snapshot = ec2_client.create_snapshot(VolumeId=volume.id, Description=f'Snapshot for {instance.id}', TagSpecifications=[{'ResourceType': 'snapshot', 'Tags': [{'Key': 'Name', 'Value': snapshot_name}]}])

            print(f"Snapshot created with ID {snapshot['SnapshotId']} for volume {volume.id} attached to instance {instance.id}.")

            # If the volume is a root device, register it as an AMI
            if volume.id == instance.root_device_name:
                ami_name = f"{current_datetime}-{instance.tags['Name']}"
                ami_description = f"AMI based on {snapshot_name}"
                ami = ec2_client.register_image(Name=ami_name, Description=ami_description, Architecture='x86_64', RootDeviceName=instance.root_device_name, BlockDeviceMappings=[{'DeviceName': instance.root_device_name, 'Ebs': {'SnapshotId': snapshot['SnapshotId']}}])

                print(f"AMI created with ID {ami['ImageId']} based on snapshot {snapshot['SnapshotId']}.")

##################
# The real stuff #
##################

# Use argparse to 
parser = argparse.ArgumentParser(description="Take a snapshot of all disks attached to all stopped EC2 instances in the region and register the snapshot as an AMI if it's a system disk.")
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region (ex: us-east-1)')
args = parser.parse_args()

take_snapshot_and_register_ami(args.region)
print('Done!')