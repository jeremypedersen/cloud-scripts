#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-25
#
# Delete all SageMaker 
#
import argparse
import boto3

#############
# Functions #
#############

# Function to get root account ID
def get_root_account_id():
    # Create an STS client
    sts_client = boto3.client('sts')
    
    # Get the caller identity
    response = sts_client.get_caller_identity()
    
    # Extract and return the account ID
    account_id = response['Account']
    
    return account_id

# List all accounts in Org
def get_all_accounts_in_organizations():
    org_client = boto3.client('organizations')
    accounts = []

    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])

    return accounts

def delete_sagemaker_endpoints(region):

    # Role name for cross account access
    role_name = 'OrganizationAccountAccessRole'

    # Create an AWS Organizations client
    orgs_client = boto3.client('organizations', region_name=region)

    accounts = get_all_accounts_in_organizations()
    root_account = get_root_account_id()
    
    for account in accounts:
        account_id = account['Id']

        # Only delete endpoints from Org accounts (not the root account)
        if account_id != root_account:

            print('=' * 30)
            print(f'Processing account {account_id}')

            # Assume a role in the account to delete SageMaker endpoints
            sts_client = boto3.client('sts')
            assumed_role = sts_client.assume_role(
                RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
                RoleSessionName='SageMakerEndpointCleanupSession'
            )

            # Create a SageMaker client using the assumed role
            sagemaker_client = boto3.client(
                'sagemaker',
                region_name=region,
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken']
            )

            # Build full list of endpoints
            endpoints = []
            paginator = sagemaker_client.get_paginator('list_endpoints')
            for page in paginator.paginate():
                endpoints.extend(page['Endpoints'])

            for endpoint in endpoints:
                endpoint_name = endpoint['EndpointName']
                print(f'Deleting SageMaker endpoint {endpoint_name} in account {account_id}')
                try:
                    sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
                    print(f'Deleted SageMaker endpoint {endpoint_name}')
                except:
                    print(f'Unable to delete endpoint {endpoint_name}, continuing...')

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='Delete SageMaker endpoints from all accounts in an AWS Organization.')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region where the SageMaker endpoints should be deleted.')
args = parser.parse_args()

delete_sagemaker_endpoints(args.region)


