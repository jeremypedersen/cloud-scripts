#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2024-02-04
# Purpose: delete all KernelGateways in a given region (cleanup)
#
import boto3
import argparse

####################
# Helper functions #
####################

def delete_all_kernelgateways(region_name):
    # Initialize SageMaker client for the specified region
    sagemaker = boto3.client('sagemaker', region_name=region_name)

    # Paginator for listing SageMaker applications
    paginator = sagemaker.get_paginator('list_apps')

    # Iterate through all SageMaker applications in the region
    for page in paginator.paginate():
        for app in page['Apps']:
            if app['AppType'] == 'KernelGateway':

                # Gather app info
                domain_name = app['DomainId']
                try:
                    user_name = app['UserProfileName']
                except:
                    user_name = app['SpaceName']
                app_type = app['AppType']
                app_name = app['AppName']

                print('=' * 30)
                print('Deleting KernelGateway...')
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

##################
# The real stuff #
##################

# Use argparse to get the region name from the command line
parser = argparse.ArgumentParser(description='Delete all Kernel Gateways (Apps) in a given region')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region name (ex: us-east-1)')

args = parser.parse_args()

# Ask the user to input a region
delete_all_kernelgateways(args.region)
