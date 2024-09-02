#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-11
#
# List all AMIs (and linked snapshots) in a given region
# 
import boto3
import argparse

#############
# Functions #
#############

def list_amis_and_snapshots(region):
    ec2 = boto3.resource('ec2', region_name=region)

    # Fetch all AMIs owned by the user
    my_amis = list(ec2.images.filter(Owners=['self']))

    # Print AMI details and their associated snapshot details
    for ami in my_amis:
        print('-' * 60)
        print(f"AMI ID: {ami.id}\nAMI Name: {ami.name if ami.name else 'N/A'}")
        for block_device in ami.block_device_mappings:
            if 'Ebs' in block_device:
                snapshot_id = block_device['Ebs']['SnapshotId']
                print(f"EBS Volume: {block_device['DeviceName']}\nSnapshot ID: {snapshot_id}")

##################
# The real stuff #
##################

# Use argparse to get the region name from the command line
parser = argparse.ArgumentParser(description='A script to list all custom AMIs in a specified region')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region name (ex: us-east-1)')

args = parser.parse_args()

list_amis_and_snapshots(args.region)
print('-' * 60)
print('Done!')
