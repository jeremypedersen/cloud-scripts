# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-23
#
# Given an AWS region as input, create AMIs from every
# snapshot found in the region
import argparse
import boto3

#############
# Functions #
#############

def create_ami_from_snapshot(region):
    # Initialize a Boto3 EC2 client in the specified region
    ec2 = boto3.client('ec2', region_name=region)

    # Describe all EBS snapshots in the region
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']

    for snapshot in snapshots:
        snapshot_id = snapshot['SnapshotId']
        name_tag = ''
        
        # Check if 'Name' tag exists for the snapshot
        for tag in snapshot.get('Tags', []):
            if tag['Key'] == 'Name':
                name_tag = tag['Value']
                break
        
        # Create an AMI from the snapshot
        try:
            response = ec2.create_image(
                InstanceId='',  # Specify the instance ID associated with the snapshot, if applicable
                Name=name_tag or f'AMI created from snapshot {snapshot_id}',
                Description=f'AMI created from EBS snapshot {snapshot_id}',
                BlockDeviceMappings=[
                    {
                        'DeviceName': '/dev/sda1',  # Specify the desired device name
                        'Ebs': {
                            'SnapshotId': snapshot_id,
                            'VolumeSize': snapshot['VolumeSize'],
                            'DeleteOnTermination': False,  # Change as needed
                        },
                    },
                ],
                DryRun=False  # Set to True to test without actually creating the AMI
            )
        except:
            print(f'Unable to create AMI from snapshot {snapshot_id}, continuing...')
    
        
        print(f"AMI created: {response['ImageId']}")

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description="Create AMIs from EBS snapshots")
parser.add_argument("--region", required=True, help="AWS region")
args = parser.parse_args()

create_ami_from_snapshot(args.region)
