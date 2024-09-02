#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-27
#
# Set a random alias on every account within an AWS organization, except
# for the Org management account
#
import boto3
import random
import string
import csv
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

# Function to generate a random two-word alias
def generate_random_alias(length):
    # Generate two random words (You can customize this logic)
    word = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return f'{word.lower()}'

# List all accounts in Organizations
def get_all_accounts_in_organizations():
    org_client = boto3.client('organizations')
    accounts = []

    # Get all accounts in the organization
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])

    return accounts

# Set aliases on each account
def set_aliases(filename, length):

    # Create a CSV writer so we can save the aliaes to an output file
    f = open(filename, 'w')
    writer = csv.writer(f)
    writer.writerow(['Account', 'Alias'])

    accounts = get_all_accounts_in_organizations()
    root_account = get_root_account_id()

    # Iterate through the accounts and assign random aliases
    for account in accounts:
        account_id = account['Id']
        
        # Skip root account
        if account_id == root_account:
            continue

        # Assume the OrganizationAccountAccessRole
        sts_client = boto3.client('sts')

        assumed_role = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole",
            RoleSessionName="AssumeRoleSession"
        )
        credentials = assumed_role['Credentials']

        # Initialize a client using the assumed credentials
        account_client = boto3.client('iam',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )

        # Determine current alias
        try:
            current_alias = account_client.list_account_aliases()['AccountAliases']
        except:
            current_alias = []
            print(f'Unable to determine current alias for account {account_id}')

        if len(current_alias) > 0:
            try:
                account_client.delete_account_alias(AccountAlias=current_alias[0])
            except:
                print(f'Unable to remove current alias from account {account_id}, continuing...')

        # Generate a random alias at least 10 letters long
        random_alias = generate_random_alias(length)

        # Update the account alias
        print(f"Assigning alias '{random_alias}' to account {account_id}")
        
    #try:
        account_client.create_account_alias(AccountAlias=random_alias)
        writer.writerow([account_id, random_alias])
    #except:
        #print(f"Unable to assign alias '{random_alias}' to account {account_id}, continuing...")

    f.close() # Close output file

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='Script to assign a random alias to each account in an AWS Organization.')
parser.add_argument('-o', '--output', type=str, required=True, help='Output CSV filename, such as aliases.csv')
parser.add_argument('-l', '--length', type=int, required=True, help='Length of random alias to attach to each account (ex: 5, for 5 letters)')

args = parser.parse_args()

set_aliases(args.output, args.length)
print('Done!')