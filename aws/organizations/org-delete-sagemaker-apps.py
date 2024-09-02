#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-25
#
# Stop all KernelGateways and Apps in a given region for all accounts
# in AWS Organizations
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

# Stop SageMaker apps
def stop_sagemaker_apps(region):

    # Role name for cross account access
    role_name = 'OrganizationAccountAccessRole'

    accounts = get_all_accounts_in_organizations()
    root_account = get_root_account_id()

    for account in accounts:
        account_id = account['Id']
        # Only delete resources from accounts other than the management (root) account
        if account_id != root_account:

            print('=' * 30)
            print(f'Processing account {account_id}')
            
            # Assume the specified role in the current account
            sts_client = boto3.client('sts', region_name=region)
            assumed_role = sts_client.assume_role(
                RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
                RoleSessionName='DeleteAppsSession'
            )

            # Create a SageMaker client using the assumed role's temporary credentials
            sm_client = boto3.client(
                'sagemaker',
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken'],
                region_name=region
            )


            # Build complete domain list
            domains = []
            paginator = sm_client.get_paginator('list_domains')
            for page in paginator.paginate():
                domains.extend(page['Domains'])

            for domain in domains:
                domain_id = domain['DomainId']
                domain_name = domain['DomainName']
                print(f'Processing domain {domain_name} with ID {domain_id}')

                # Build app list
                apps = []
                paginator = sm_client.get_paginator('list_apps')
                for page in paginator.paginate(DomainIdEquals=domain_id):
                    apps.extend(page['Apps'])

                for app in apps:
                    # Pull app data
                    app_name = app['AppName']
                    app_type = app['AppType']
                    domain_id = app['DomainId']

                    try:
                        user_profile = app['UserProfileName']
                    except:
                        user_profile = app['SpaceName']

                    print(f'Deleting App {app_name} from domain {domain_id}')

                    try:
                        sm_client.delete_app(UserProfileName=user_profile, DomainId=domain_id, AppName=app_name, AppType=app_type)
                    except:
                        print(f'Unable to delete app {app_name}, continuing...')

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='Stop all SageMaker domain KernelGateways and Apps in a specified region for all accounts within an AWS Organization.')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region where SageMaker resources should be stopped.')
args = parser.parse_args()

stop_sagemaker_apps(args.region)

print('Done!')