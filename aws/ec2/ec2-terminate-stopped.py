# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-10
#
# Given an AWS region as input, terminate all the stopped
# instances in the region which match a pattern. If no pattern
# is given, simply terminate all stopped instances.
#
import boto3
import argparse

def terminate_stopped_ec2_instances(region):
    # Create EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    # Fetch all instances in the 'stopped' state
    response = ec2.describe_instances(
        Filters=[{
            'Name': 'instance-state-name',
            'Values': ['stopped']
        }]
    )

    instances_to_terminate = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances_to_terminate.append(instance['InstanceId'])

    if not instances_to_terminate:
        print(f'No stopped instances to terminate in the region: {region}')
        return

    # Terminate instances
    print(f"Terminating stopped instances: {', '.join(instances_to_terminate)}")
    ec2.terminate_instances(InstanceIds=instances_to_terminate)
    print('Stopped instances terminated successfully!')

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='Terminate all stopped EC2 instances in a specified region.')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region name (ex: us-west-2)')

args = parser.parse_args()
terminate_stopped_ec2_instances(args.region)
print('Done!')