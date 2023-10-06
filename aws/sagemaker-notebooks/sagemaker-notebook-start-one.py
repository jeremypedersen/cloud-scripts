#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-06
# 
# Starts a single, named SageMaker Notebook in a given region
import boto3
import argparse

#############
# Functions #
#############

def start_sagemaker_notebook(region, instance_name):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    # Start the specified notebook instance
    try:
        sagemaker.start_notebook_instance(NotebookInstanceName=instance_name)
    except:
        print(f'Unable to start instance {instance_name}')

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description='A script to start a single SageMaker notebook instance in a given region')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-n', '--notebook', type=str, required=True, help='The name of the SageMaker notebook instance to stop (ex: my-notebook-instance)')

# Parse the command line arguments
args = parser.parse_args()

print(f'Starting {args.notebook} in region {args.region}')
start_sagemaker_notebook(args.region, args.notebook)
print('Done!')