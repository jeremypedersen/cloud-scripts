#
# Author: Jeremy Pedersen
# Date: 2023-08-23
#
# This script performs "complete cleanup" of all the SageMaker domains
# in a given region. This includes:
#
# 1. Deleting all apps
# 2. Deleting all spaces
# 3. Deleting all user profiles
# 4. Deleting any left-behind resources (EFS shared filesystems)
#
# Note that it does NOT delete Execution Roles, because it is assumed that you might want to
# preserve the list of attached policies so you can re-create the permissions associated with 
# each domain in the future

# NOTE: You may have to run the script more than once, as domains will fail to
# delete properly if user profiles are still being deleted (which takes some time)
import boto3, time

# Helpers
def delete_all_apps(sagemaker):

    # Paginator for listing SageMaker applications
    paginator = sagemaker.get_paginator('list_apps')

    # Iterate through all SageMaker applications in the region, deleting
    # them as we go (skip apps which cannot be deleted because they are in the "deleting"
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
                print(f"Error deleting KernelGateway {app_name}: {e}")

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
                print(f"Deleting user profile: {user_profile_name} from domain: {domain_id}")
                sagemaker.delete_user_profile(DomainId=domain_id, UserProfileName=user_profile_name)
            except Exception as e:
                print(f"Error deleting user profile {user_profile_name} from domain {domain_id}. Error: {str(e)}")

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
                print(f"Deleting space: {space_name} from domain: {domain_id}")
                sagemaker.delete_space(DomainId=domain_id, SpaceName=space_name)
            except Exception as e:
                print(f"Error deleting space {space_name} from domain {domain_id}. Error: {str(e)}")

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
            print(f"Deleting domain: {domain_id} ...")
            
            # Delete the domain
            try:
                sagemaker.delete_domain(DomainId=domain_id)
                print(f"Domain {domain_id} deleted successfully.")
            except Exception as e:
                print(f"Failed to delete domain {domain_id}. Error: {e}")

    print("Finished deleting all SageMaker domains in the region.")

#
# Ok, let's clean up!
# 

# Get user input for the region
region_name = input("Please input the AWS region name (e.g., us-east-1): ")
sagemaker_client = boto3.client('sagemaker', region_name=region_name)

# First, delete apps
delete_all_apps(sagemaker_client)

# Wait for apps to delete
print("Pausing for 1 minute while apps delete...")
time.sleep(60)

# Then, delete all user profiles
delete_all_user_profiles(sagemaker_client)

# We also need to clean up any Spaces
delete_all_spaces(sagemaker_client)

# Pause before deleting domains, because it takes some time for apps, profiles, and spaces to delete
print("Pausing for 1 minute while spaces delete...")
time.sleep(60)

# Finally, delete all domains
delete_all_domains(sagemaker_client)

# We're done!
print("Done!")