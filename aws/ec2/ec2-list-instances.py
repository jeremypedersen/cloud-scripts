# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-11
#
# List all EC2 instances and their current status
#
import argparse
import boto3

#############
# Functions #
#############

def list_ec2_instances(region):
    ec2 = boto3.client('ec2', region_name=region)

    response = ec2.describe_instances()

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_name = get_instance_name(instance)
            instance_state = instance['State']['Name']

            print(f"Instance ID: {instance_id}")
            print(f"Instance Name: {instance_name}")
            print(f"Instance Status: {instance_state}\n")

def get_instance_name(instance):
    for tag in instance['Tags']:
        if tag['Key'] == 'Name':
            return tag['Value']
    return 'N/A'

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='List EC2 instances in an AWS region')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region name (ex: us-east-1)')
args = parser.parse_args()

list_ec2_instances(args.region)
print('Done!')