#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-06
#
# Stops a single, named SageMaker Notebook in a given region
import boto3
import argparse

#############
# Functions #
#############

def stop_sagemaker_notebook(region, instance_name):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    # Stop the specified notebook instance
    print(f'Stopping {instance_name} in region {region}...')
    try:
        sagemaker.stop_notebook_instance(NotebookInstanceName=instance_name)
    except:
        print(f'Unable to stop instance {instance_name}')

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description="A script to stop a single SageMaker notebook instance")
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-n', '--notebook', type=str, required=True, help='The name of the SageMaker notebook instance to stop (ex: my-notebook-instance)')

# Parse the command line arguments
args = parser.parse_args()

# Stop the instance
print(f'Stopping instance {args.notebook} in region {args.region}...')
stop_sagemaker_notebook(args.region, args.notebook)
print('Done!')

