#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-25
#
# Stop all EC2 instances in a specified region, for all accounts 
# in the AWS Organization
#
import boto3
import argparse

#############
# Functions #
#############

def get_root_account_id():
    # Create an STS client
    sts_client = boto3.client('sts')
    
    # Get the caller identity
    response = sts_client.get_caller_identity()
    
    # Extract and return the account ID
    account_id = response['Account']
    
    return account_id

def get_all_accounts_in_organizations():
    org_client = boto3.client('organizations')
    accounts = []

    # Get all accounts in the organization
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])

    return accounts

def stop_all_ec2_instances(region):

    # Role name for cross account access
    role_name = 'OrganizationAccountAccessRole'

    # Get the organization management account ID
    root_account = get_root_account_id()

    # Get all AWS accounts in the organization
    accounts = get_all_accounts_in_organizations()

    # Iterate through each account
    for account in accounts:
        account_id = account['Id']
        
        if account_id != root_account:

            print('=' * 30)
            print(f'Processing account {account_id}')

            # Assume a role in the account to stop EC2 instances
            sts_client = boto3.client('sts')
            assumed_role = sts_client.assume_role(
                RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
                RoleSessionName='EC2StopInstancesSession'
            )

            # Create a SageMaker client using the assumed role
            ec2_client = boto3.client(
                'ec2',
                region_name=region,
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken']
            )

            # Build full instance list
            instances = []
            paginator = ec2_client.get_paginator('describe_instances')
            for page in paginator.paginate():
                for res in page['Reservations']:
                    instances.extend(res['Instances'])

            for instance in instances:
                instance_id = instance['InstanceId']
                print(f'Stopping EC2 instance {instance_id} in account {account_id}...')
                try:
                    ec2_client.stop_instances(InstanceIds=[instance_id])
                    print(f'EC2 instance {instance_id} in account {account_id} stopped.')
                except:
                    print(f'EC2 instance {instance_id} could not be stopped, continuing...')

parser = argparse.ArgumentParser(description='Shutdown all EC2 instances in every AWS Organizations account in a specific AWS region.')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region where EC2 instances should be shut down.')
args = parser.parse_args()

stop_all_ec2_instances(args.region)
print('Done!')

