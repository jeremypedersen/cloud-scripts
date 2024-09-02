#
# Jeremy Pedersen (and ChatGPT)
# Updated: 2024-02-04
#
# This script performs 'complete cleanup' of all SageMaker domains
# in a given region. This includes:
#
# 1. Deleting all apps
# 2. Deleting all spaces
# 3. Deleting all user profiles
#
# NOTE: You may need to run the script several times before it succeeds. It can
# take a long time delete some resources (apps, spaces, user profiles), and some 
# resources will not allow themselves to be deleted until their dependent resources
# are successfully deleted. 
#
import boto3
import argparse

####################
# Helper functions #
####################

def delete_all_apps(sagemaker):

    # Paginator for listing SageMaker applications
    paginator = sagemaker.get_paginator('list_apps')

    # Iterate through all SageMaker applications in the region, deleting
    # them as we go (skip apps which cannot be deleted because they are in the 'deleting'
    # state or have already been deleted)
    for page in paginator.paginate():
        for app in page['Apps']:

            # Gather app info
            domain_name = app['DomainId']
            try:
                user_name = app['UserProfileName']
            except:
                user_name = app['SpaceName']
            app_type = app['AppType']
            app_name = app['AppName']

            print('=' * 30)
            print('Deleting App...')
            print(f'Domain: {domain_name}')
            print(f'User / Space Name: {user_name}')
            print(f'App Type: {app_type}')
            print(f'App Name: {app_name}')

            # Deleting the KernelGateway instance
            try:
                sagemaker.delete_app(
                    DomainId=domain_name, 
                    UserProfileName=user_name, 
                    AppType=app_type, 
                    AppName=app_name
                )
            except Exception as e:
                print(f'Error deleting KernelGateway {app_name}: {e}')

def delete_all_user_profiles(sagemaker):
    # Paginator for listing SageMaker applications
    paginator = sagemaker.get_paginator('list_user_profiles')

    # Iterate through all SageMaker profiles in the region, 
    # deleting them as we go
    for page in paginator.paginate():
        for profile in page['UserProfiles']:
            user_profile_name = profile['UserProfileName']
            domain_id = profile['DomainId']

            try:
                print(f'Deleting user profile: {user_profile_name} from domain: {domain_id}')
                sagemaker.delete_user_profile(DomainId=domain_id, UserProfileName=user_profile_name)
            except Exception as e:
                print(f'Error deleting user profile {user_profile_name} from domain {domain_id}. Error: {str(e)}')

# Delete all SageMaker Spaces in a region
def delete_all_spaces(sagemaker):
    # Paginator for listing SageMaker spaces
    paginator = sagemaker.get_paginator('list_spaces')

    # Iterate through all SageMaker spaces in the region, 
    # deleting them as we go
    for page in paginator.paginate():
        for space in page['Spaces']:
            space_name = space['SpaceName']
            domain_id = space['DomainId']

            try:
                print(f'Deleting space: {space_name} from domain: {domain_id}')
                sagemaker.delete_space(DomainId=domain_id, SpaceName=space_name)
            except Exception as e:
                print(f'Error deleting space {space_name} from domain {domain_id}. Error: {str(e)}')

# Delete all SageMaker domains in a region
def delete_all_domains(sagemaker):

    # Create a paginator for the list_domains operation
    paginator = sagemaker.get_paginator('list_domains')

    # Use the paginator to retrieve all pages of SageMaker domains
    for page in paginator.paginate():
        domains = page['Domains']

        # Loop through each domain in the current page and delete it
        for domain in domains:
            # Get the domain ID
            domain_id = domain['DomainId']
            print('=' * 30)
            print(f'Deleting domain: {domain_id} ...')
            
            # Delete the domain
            try:
                sagemaker.delete_domain(DomainId=domain_id)
                print(f'Domain {domain_id} deleted successfully.')
            except Exception as e:
                print(f'Failed to delete domain {domain_id}. Error: {e}')

##################
# The real stuff #
##################

# Use argparse to get the region name from the command line
parser = argparse.ArgumentParser(description='Delete all SageMaker Domains in a given region')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region name (ex: us-east-1)')

args = parser.parse_args()

sagemaker_client = boto3.client('sagemaker', region_name=args.region)

# First, delete apps
delete_all_apps(sagemaker_client)

# Then, delete all user profiles
delete_all_user_profiles(sagemaker_client)

# We also need to clean up any Spaces
delete_all_spaces(sagemaker_client)

# Finally, delete all domains
delete_all_domains(sagemaker_client)

# We're done!
print('=' * 30)
print('Done! Pay attention to the errors and warnings above (if any). You will probably need to run this script more than once.')