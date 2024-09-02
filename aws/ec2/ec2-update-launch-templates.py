# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-13
#
# Given an AWS region as input, update all the launch templates
# in the region to use the latest version and delete all older versions.
#
import boto3
import argparse

#############
# Functions #
#############

def set_default_to_latest_and_delete_old_versions(region_name):
    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region_name)

    # Get all launch templates in the region
    response = ec2.describe_launch_templates()
    launch_templates = response['LaunchTemplates']

    for lt in launch_templates:
        launch_template_id = lt['LaunchTemplateId']
        latest_version_number = lt['LatestVersionNumber']

        # Set default version to the latest version
        ec2.modify_launch_template(
            LaunchTemplateId=launch_template_id,
            DefaultVersion=str(latest_version_number)
        )

        # Delete all older versions
        for version_number in range(1, latest_version_number):
            try:
                ec2.delete_launch_template_versions(
                    LaunchTemplateId=launch_template_id,
                    Versions=[str(version_number)]
                )
            except ec2.exceptions.ClientError as e:
                # Handle cases where the version might have been deleted previously
                print(f'Error deleting version {version_number} of {launch_template_id}. Error: {str(e)}')

    print(f'Processed {len(launch_templates)} launch template(s) in {region_name}')

##################
# The real stuff #
##################

parser = argparse.ArgumentParser(description='Update AWS launch templates in the given region.')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region name (ex: us-west-1)')
args = parser.parse_args()

set_default_to_latest_and_delete_old_versions(args.region)
