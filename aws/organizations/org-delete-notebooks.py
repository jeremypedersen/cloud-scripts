#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-25
#
# Delete all SageMaker Notebook accounts in the specified region, across all
# accounts in the Organization
#
import boto3
import argparse

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

# List all SageMaker notebooks
def get_all_notebooks(sagemaker_client):
    notebooks = []

    paginator = sagemaker_client.get_paginator('list_notebook_instances')
    for page in paginator.paginate():
        notebooks.extend(page['NotebookInstances'])


# Function to stop SageMaker notebook instances in the specified region
def stop_notebooks(region):

    # Role name for cross-account access
    role_name = 'OrganizationAccountAccessRole'

    accounts = get_all_accounts_in_organizations()
    root_account = get_root_account_id()

    # Loop through each account and stop SageMaker notebook instances
    for account in accounts:
        account_id = account['Id']
        if account_id != root_account:

            print('=' * 30)
            print(f'Processing account {account_id}')

            # Assume the specified role in the current account
            sts_client = boto3.client('sts', region_name=region)
            assumed_role = sts_client.assume_role(
                RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
                RoleSessionName='SageMakerNotebookInstanceDeleteSession'
            )

            # Create a SageMaker client using the assumed role's temporary credentials
            sagemaker_client = boto3.client(
                'sagemaker',
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken'],
                region_name=region
            )

            # List all notebooks
            notebook_instances = []
            paginator = sagemaker_client.get_paginator('list_notebook_instances')
            for page in paginator.paginate():
                notebook_instances.extend(page['NotebookInstances'])

            # Stop each SageMaker notebook instance in the specified region
            for instance in notebook_instances:
                instance_name = instance['NotebookInstanceName']
                print(f'Deleting SageMaker notebook instance: {instance_name}')

                # Stop the SageMaker notebook instance
                try:
                    sagemaker_client.delete_notebook_instance(
                        NotebookInstanceName=instance_name
                    )
                except:
                    print(f'Instance {instance_name} could not be deleted, perhaps it is not running?')

            print(f'All SageMaker notebook instances deleted from account {account_id} in region {region}')

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='Stop SageMaker notebook instances in specified AWS region.')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region where SageMaker instances should be stopped.')
args = parser.parse_args()

stop_notebooks(args.region)
print('Done!')