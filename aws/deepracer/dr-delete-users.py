# 
# Author: Jeremy Pedersen
# Updated: 2023-08-23
#
# Delete the DeepRacer IAM users created by
# the dr-delete-users.py script
#
# NOTE: This script will delete ALL IAM users whose 
# username starts with 'deepracer' so BE CAREFUL
#
# NOTE: It also deletes the 'DeepRacerUsers' group
#
import boto3, time

# Initialize the IAM client
iam = boto3.client('iam')

# Constants
user_prefix = 'deepracer'
group_name = 'DeepRacerUsers'

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
time.sleep(5)

# Delete group
try:
    iam.delete_group(GroupName=group_name)
    print(f'Deleted group: {group_name}')
except:
    print(f'Unable to delete the group {group_name}, you may need to delete it by hand (or it may already be deleted).')

print('Done!')