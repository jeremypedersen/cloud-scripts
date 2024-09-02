# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-11
#
# Stop all the EC2 instances in a specified AWS region.
#
import boto3
import argparse

#############
# Functions #
#############

def stop_all_ec2_instances(region):
    # Initialize a session using Amazon EC2
    session = boto3.session.Session(region_name=region)
    ec2_resource = session.resource('ec2')

    # List all running instances
    instances = ec2_resource.instances.filter(
        Filters=[{
            'Name': 'instance-state-name',
            'Values': ['running']
        }]
    )

    # Stop the instances
    for instance in instances:
        print(f"Stopping instance {instance.id} in region {region}...")
        instance.stop()

##################
# The real stuff #
##################

# Parse the command-line arguments
parser = argparse.ArgumentParser(description='Stop all EC2 instances in a specified AWS region.')
parser.add_argument('-r', '--region', type=str, required=True, help="AWS region name (ex: us-west-2)")
args = parser.parse_args()

# Stop all instances in the given region
stop_all_ec2_instances(args.region)
print('Done!')