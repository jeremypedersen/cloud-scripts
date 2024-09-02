# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-11
#
# Start all the EC2 instances in a region
#
import boto3
import argparse

#############
# Functions #
#############

def start_all_ec2_instances(region_name):
    # Initialize a session using Amazon EC2
    session = boto3.session.Session(region_name=region_name)
    ec2 = session.resource('ec2')

    # Filter the instances which are in 'stopped' state
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
    )

    # Create a list to hold the instance IDs
    instance_ids = [instance.id for instance in instances]

    # Start the instances
    if instance_ids:
        print(f"Starting instances: {', '.join(instance_ids)} in region {region_name}")
        ec2.instances.filter(InstanceIds=instance_ids).start()
    else:
        print(f"No stopped instances in region {region_name} to start.")

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='Start all EC2 instances in a specified region.')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region where the EC2 instances are located.')

args = parser.parse_args()

# Call the function to start the instances
start_all_ec2_instances(args.region)
print('Done!')