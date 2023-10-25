#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-25
#
# Delete all IAM users from every account in an AWS Organization
#
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

# List all IAM users
def get_all_users(iam_client): 
    paginator = iam_client.get_paginator('list_users')
    users = []

    for page in paginator.paginate():
        users.extend(page['Users'])

    return users

# List all accounts in Org
def get_all_accounts_in_organizations():
    org_client = boto3.client('organizations')
    accounts = []

    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])

    return accounts

def delete_all_iam_users():

    # Role name for cross-account access
    role_name = 'OrganizationAccountAccessRole'

    accounts = get_all_accounts_in_organizations()
    root_account = get_root_account_id()

    # Delete all IAM users from all accounts
    for account in accounts['Accounts']:
        account_id = account['Id']
        
        if account_id != root_account:

            print('=' * 30)
            print(f'Processing account {account_id}')

            # Initialize the STS client to assume the role
            sts_client = boto3.client('sts')
            assume_role_response = sts_client.assume_role(
                RoleArn=f'arn:aws:iam::{account_id}:role/{role_name}',
                RoleSessionName='DeleteIAMUsersSession'
            )
            
            # Create a session for the target account
            target_session = boto3.Session(
                aws_access_key_id=assume_role_response['Credentials']['AccessKeyId'],
                aws_secret_access_key=assume_role_response['Credentials']['SecretAccessKey'],
                aws_session_token=assume_role_response['Credentials']['SessionToken']
            )
            
            # Initialize the IAM client for the target account
            iam_client = target_session.client('iam')
            
            users = get_all_users(iam_client)
            
            # Delete all IAM users in the target account
            for user in users['Users']:
                user_name = user['UserName']
                print(f'Deleting IAM user {user_name} in account {account_id}')
                iam_client.delete_user(UserName=user_name)
            
            print(f'IAM users deleted in account {account_id}')

##################
# The real stuff #
##################

delete_all_iam_users()
print('Done!')
