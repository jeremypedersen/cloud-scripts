#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
# 
# This script is used to help clean up SageMaker notebook execution roles
#
# WARNING: It does this via simple pattern-matching, so be careful about how you use it!
#
import boto3
import argparse

#############
# Functions #
#############

def delete_iam_roles(pattern):
    client = boto3.client('iam')
    
    # Get all roles
    roles = client.list_roles()['Roles']
    
    for role in roles:
        role_name = role['RoleName']

        if pattern.lower() in role_name.lower():
            print(f'Trying to delete role {role_name}...')
            
            # List and detach role policies
            for policy in client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']:

                try:
                    client.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
                except:
                    policy_name = policy['PolicyArn'].split('/')[-1]
                    print('Unable to detach policy {policy_name} from role {role_name}, continuing anyway')

                # Delete the managed policy itself
                try:
                    client.delete_policy(PolicyArn=policy['PolicyArn'])
                    print(f"Deleted policy: {policy['PolicyArn']}")
                except:
                    policy_name = policy['PolicyArn'].split('/')[-1]
                    print(f'Unable to delete policy {policy_name}, continuing anyway')
            
            # Delete inline policies
            for policy_name in client.list_role_policies(RoleName=role_name)['PolicyNames']:
                try:
                    client.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
                    print(f"Deleted inline policy: {policy_name} from role: {role_name}")
                except:
                    print('Unable to delete inline policy {policy_name}, continuing anyway')

            # Delete any associated instance profiles
            for instance_profile in client.list_instance_profiles_for_role(RoleName=role_name)['InstanceProfiles']:
                try:
                    client.remove_role_from_instance_profile(
                        InstanceProfileName=instance_profile['InstanceProfileName'],
                        RoleName=role_name
                    )
                except:
                    print('Unable to remove role {role_name} from instance profile {instance_profile_name}, continuing anyway')
                
                # Delete the instance profile itself (if no longer needed)
                try:
                    client.delete_instance_profile(InstanceProfileName=instance_profile['InstanceProfileName'])
                except:
                    profile_name = instance_profile['InstanceProfileName']
                    print(f'Unable to delete instance profile {profile_name}, continuing anyway')

            # Delete the role itself
            try:
                client.delete_role(RoleName=role_name)
                print(f"Deleted role: {role_name}")
            except:
                print('Unable to delete role e {role_name}, continuing anyway')

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='A script to delete IAM roles (and attached policies) matching a specific pattern')
parser.add_argument('-p', '--pattern', type=str, required=False, help='The SageMaker execution role pattern to match (ex: ExecutionRoleBatch)')

# Parse the command line arguments
args = parser.parse_args()

# Delete the roles matching the pattern    
if args.pattern:
    delete_iam_roles(args.pattern)
else:
    delete_iam_roles('ExecutionRoleBatch')

print('Done!')

