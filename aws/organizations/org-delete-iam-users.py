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

def delete_iam_user(user_name, iam_client):
    # List and delete access keys
    access_keys = iam_client.list_access_keys(UserName=user_name)
    for key in access_keys['AccessKeyMetadata']:
        access_key_id = key['AccessKeyId']
        iam_client.delete_access_key(UserName=user_name, AccessKeyId=access_key_id)

    # Delete attached policies
    attached_policies = iam_client.list_attached_user_policies(UserName=user_name)
    for policy_arn in attached_policies['AttachedPolicies']:
        iam_client.detach_user_policy(UserName=user_name, PolicyArn=policy_arn['PolicyArn'])
    
    # Delete inline policies
    inline_policies = iam_client.list_user_policies(UserName=user_name)
    for policy_name in inline_policies['PolicyNames']:
        iam_client.delete_user_policy(UserName=user_name, PolicyName=policy_name)

    # Delete login profile if it exists
    try:
        iam_client.delete_login_profile(UserName=user_name)
    except iam_client.exceptions.NoSuchEntityException:
        pass  # Login profile doesn't exist, so no need to delete it
    
    # Delete the user
    iam_client.delete_user(UserName=user_name)

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
    for account in accounts:
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
            
            iam_client =  boto3.client(
                'iam',
                aws_access_key_id=assume_role_response['Credentials']['AccessKeyId'],
                aws_secret_access_key=assume_role_response['Credentials']['SecretAccessKey'],
                aws_session_token=assume_role_response['Credentials']['SessionToken']
            )
            
            users = get_all_users(iam_client)
            
            # Delete all IAM users in the target account
            for user in users:
                user_name = user['UserName']
                print(f'Deleting user {user_name}')
                delete_iam_user(user_name, iam_client)

##################
# The real stuff #
##################

delete_all_iam_users()
print('Done!')
