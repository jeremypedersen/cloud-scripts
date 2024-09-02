#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
# 
# This script is used to help clean up SageMaker IAM users

# WARNING: It does this via simple pattern-matching, so be careful about how you use it!
#
import boto3
import argparse

#############
# Functions #
#############

def delete_iam_users(pattern):
    client = boto3.client('iam')
    
    # Get all users
    users = client.list_users()['Users']
    
    for user in users:
        username = user['UserName']
        
        if pattern.lower() in username.lower():
            print(f'Trying to delete {username}...')

            # List and delete user policies
            for policy in client.list_attached_user_policies(UserName=username)['AttachedPolicies']:
                try:
                    client.delete_user_policy(UserName=username, PolicyArn=policy['PolicyArn'])
                except:
                    policy_name = policy['PolicyArn'].split('/')[-1]
                    print(f'Unable to detach policy {policy_name} from user {username}, continuing anyway')

            # Delete all inline policies of the user
            inline_policies = client.list_user_policies(UserName=username)['PolicyNames']
            for policy_name in inline_policies:
                try:
                    client.delete_user_policy(UserName=username, PolicyName=policy_name)
                    print(f'Deleted inline policy {policy_name} from user {username}')
                except:
                    print(f'Unable to delete inline policy {policy_name} from user {username}, continuing anyway')

            # List and detach user group memberships (do not delete the group, 
            # its roles, or the policies associated with those roles)
            for group in client.list_groups_for_user(UserName=username)['Groups']:
                try:
                    client.remove_user_from_group(UserName=username, GroupName=group['GroupName'])
                except:
                    group_name = group['GroupName']
                    print(f'Unable to remove user {username} from group {group_name}, continuing anyway')

            # List the roles associated with user and delete policies attached to those roles
            for role in client.list_roles(PathPrefix=f"/{username}/")['Roles']:
                role_name = role['RoleName']

                # List and detach role policies
                for policy in client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']:
                    try:
                        client.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
                    except:
                        policy_name = policy['PolicyArn'].split('/')[-1]
                        print('Unable to detach policy {policy_name} from role {role_name}, continuing anyway')

                # Delete policies attached to each role
                for policy_name in client.list_role_policies(RoleName=role_name)['PolicyNames']:
                    try:
                        client.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
                    except:
                        print('Unable to delete policy {policy_name} from role {role_name}, continuing anyway')

                # Delete the role itself
                try:
                    client.delete_role(RoleName=role_name)
                except:
                    print(f'Unable to delete role {role_name}, continuing anyway')

            # Delete the user's login profile
            try:
                client.delete_login_profile(UserName=username)
            except:
                print(f'Unable to delete login profile from {username}, continuing anyway')

            # Finally, delete the user
            client.delete_user(UserName=username)

            try:
                client.delete_user(UserName=username)
                print(f"Deleted user: {username}")
            except:
                print(f'Unable to delete user {username}, continuing anyway')

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='A script to delete IAM users matching a specific pattern, and their attached policies')
parser.add_argument('-p', '--pattern', type=str, required=False, help='The IAM username prefix to match (ex: notebook-user)')

# Parse the command line arguments
args = parser.parse_args()

# Delete the users matching the pattern
if args.pattern:
    delete_iam_users(args.pattern)
else:
    delete_iam_users('notebook-user')

print('Done!')