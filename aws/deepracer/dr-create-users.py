# 
# Author: Jeremy Pedersen
# Updated: 2023-10-25
#
# Create multiple DeepRacer IAM users, for use with 
# DeepRacer's multi-user feature, documented here:
# https://docs.aws.amazon.com/deepracer/latest/developerguide/multi-user-mode.html
#
import boto3
import time
import argparse
import csv

#############
# Functions #
#############

def create_users(user_prefix, group_name, num_users, filename):
    sts = boto3.client('sts')
    iam = boto3.client('iam')

    # Initialize the CSV writer
    f = open(filename, 'w')
    writer = csv.writer(f)

    writer.writerow(['Username', 'Password', 'Login Link]'])

    # Determine the IAM user login link for the account (so we can include it
    # in the .csv file)
    try:
        # Fetch account ID
        account_id = sts.get_caller_identity().get('Account')
        
        # Construct the URL
        login_url = f'https://{account_id}.signin.aws.amazon.com/console/'
        print(f'IAM users can log in using: {login_url}')
    except:
        print(f'Could not determine account ID!')
        print('Continuing anyway, but you a will need to determine the IAM user login URL by yourself')
        login_url = 'UNKNOWN'

    # Create IAM User Group 'DeepRacerUsers', and attach policies 
    # to grant DeepRacer service access and IAM 'change password' permissions
    policy_arns = [
        'arn:aws:iam::aws:policy/AWSDeepRacerDefaultMultiUserAccess',
        'arn:aws:iam::aws:policy/IAMUserChangePassword'
    ]

    try:
        # Create the group
        response = iam.create_group(GroupName=group_name)
        if response and 'Group' in response:
            print(f'Group {group_name} created successfully.')
    except:
        print(f'Unable to create group {group_name}, skipping and hoping it is already there!')

    # Wait before attaching policies
    print('Waiting a few seconds before adding policies...')
    time.sleep(2)   

    for policy_arn in policy_arns:
        try:
            # Attach the policy to the group
            iam.attach_group_policy(
                GroupName=group_name,
                PolicyArn=policy_arn
            )
            print(f'Policy {policy_arn} attached to group {group_name} successfully.')
        except:
            print(f'Unable to attach policy {policy_arn} to group {group_name}, continuing on...')

    # Create users
    for i in range(1, num_users+1):
        username = f'{user_prefix}-{i}'
        password = f'{username}-{i}$' # Assign a random password (user will change on first login)
        print(f'Creating user {username}')

        # Create user
        try:
            iam.create_user(UserName=username)
        except:
            print(f'Cloud not create user: {username}')
            print('Skipping, moving on to next user')

        # Grant console access
        try:
            iam.create_login_profile(
                UserName=username, Password=password, PasswordResetRequired=True)
        except:
            print(f'Could not create login profile for {username}')
            print(f'Continuing anyway...')

        # Grant DeepRacer permissions (assigned to group)
        try:
            iam.add_user_to_group(
                UserName=username,
                GroupName=group_name
            )
        except:
            print(f'Could not add user {username} to group')
            print(f'Continuing anyway...')

        writer.writerow([username, password, login_url])

    # Close the .csv file
    f.close()

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='A script to create DeepRacer IAM users and attach the permissions required to access the DeepRacer console')
parser.add_argument('-u', '--user-prefix', type=str, required=False, help='The prefix to use for the user names (ex: deepracer)')
parser.add_argument('-g', '--group-name', type=str, required=False, help='The name of the IAM group to create (ex: DeepRacerUsers)')
parser.add_argument('-n', '--num-users', type=int, required=False, help='The number of users to create (ex: 10)')
parser.add_argument('-o', '--output-file', type=str, required=False, help='The name of the .csv file to store the usernames and passwords')

# Parse the command line arguments
args = parser.parse_args()

# Default values
user_prefix = 'deepracer'
group_name = 'DeepRacerUsers'
num_users = 1
filename = 'users.csv'

# Override defaults with command line arguments
if args.user_prefix:
    user_prefix = args.user_prefix
if args.group_name:
    group_name = args.group_name
if args.num_users:
    num_users = args.num_users
if args.output_file:
    filename = args.output_file

# Create IAM Users
create_users(user_prefix, group_name, num_users, filename)

# Create a log to keep track of the group and user prefix values, which we may
# need later when deleting users
with open(filename.split('.')[0] + '.log', 'w') as f:
    f.write(f'User prefix: {user_prefix}\n')
    f.write(f'Group name: {group_name}\n')

print('Done!')