# List all snapshots in a given region
# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-09-10
import boto3

def list_ebs_snapshots(region_name):
    # Create an EC2 client object using the specified region
    ec2_client = boto3.client('ec2', region_name=region_name)

    # Retrieve snapshots using describe_snapshots method
    snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])

    # Print the header
    print(f"Listing all EBS snapshots in region {region_name}:")
    print('-' * 60)

    # Iterate through all snapshots and print their details
    for snapshot in snapshots['Snapshots']:
        for key, value in snapshot.items():
            print(f"{key}: {value}")
        print('-' * 60)

# Fetch region name
region = input("Enter AWS region (such as us-west-2): ").strip()
list_ebs_snapshots(region)
