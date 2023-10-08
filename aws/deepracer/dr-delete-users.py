# 
# Author: Jeremy Pedersen
# Updated: 2023-10-08
#
# Delete the DeepRacer IAM users created by
# the dr-delete-users.py script
#
# NOTE: This script will delete all IAM users and groups using the 
# patterns supplied as command line arguments (or the default patterns
# included in the code below, if no command line arguments are supplied)
#
import boto3
import time
import argparse

#############
# Functions #
#############

def delete_users(user_prefix, group_name):

    # Initialize the IAM client
    iam = boto3.client('iam')

    policy_arns = [
        'arn:aws:iam::aws:policy/AWSDeepRacerDefaultMultiUserAccess',
        'arn:aws:iam::aws:policy/IAMUserChangePassword'
    ]

    #
    # Helper functions
    #
    def delete_user_login_profile(username):
        try:
            iam.delete_login_profile(UserName=username)
            print(f'Deleted login profile for user: {username}')
        except:
            print(f'Was not able to delete logon profile for user {username}')
            print('Continuing on...')

    def delete_user(username):
        try:
            iam.delete_user(UserName=username)
            print(f'Deleted user: {username}')
        except:
            print(f'Was not able to delete user {username}')
            print('Continuing on...')

    def remove_user_from_group(username, group_name):
        try:
            iam.remove_user_from_group(UserName=username, GroupName=group_name)
            print(f'User {username} removed from group {group_name}')
        except:
            print(f'Unable to remove user {username} from group {group_name}')
            print('Continuing anyway...')

    #
    # Remove users
    #
    try:
        # Fetch list of all IAM users
        users = iam.list_users()['Users']

        # Filter list for users starting with 'DeepRacer'
        deepracer_users = [user['UserName'] for user in users if user['UserName'].startswith(user_prefix)]
    except:
        print('Unable to fetch user list')
        print('This is a fatal error, exiting now. Check your AWS credentials.')
        exit(-1)

    # For each user, delete the user's login profile and then delete the user
    for username in deepracer_users:
        remove_user_from_group(username, group_name)
        delete_user_login_profile(username)    
        delete_user(username)

    # Detach policies from group
    for policy_arn in policy_arns:
        try:
            iam.detach_group_policy(
                GroupName=group_name,
                PolicyArn=policy_arn
            )
            print(f'Policy {policy_arn} removed from group {group_name} successfully.')
        except:
            print(f'Unable to remove policy {policy_arn} from group {group_name}, continuing on...')

    # Wait for policies to detach
    print('Waiting for policies to detach...')
    time.sleep(2)

    # Delete group
    try:
        iam.delete_group(GroupName=group_name)
        print(f'Deleted group: {group_name}')
    except:
        print(f'Unable to delete the group {group_name}, you may need to delete it by hand (or it may already be deleted).')

parser = argparse.ArgumentParser(description='A to delete the DeepRacer users (and the group) created by dr-create-users.py')
parser.add_argument('-u', '--user-prefix', type=str, required=False, help='The prefix to use for the user names (ex: deepracer-)')
parser.add_argument('-g', '--group-name', type=str, required=False, help='The name of the IAM group to create (ex: DeepRacerUsers)')

# Parse the command line arguments
args = parser.parse_args()

# Default values
user_prefix = 'deepracer'
group_name = 'DeepRacerUsers'

# Override defaults with command line arguments
if args.user_prefix:
    user_prefix = args.user_prefix
if args.group_name:
    group_name = args.group_name

delete_users(user_prefix, group_name)
print('Done!')
