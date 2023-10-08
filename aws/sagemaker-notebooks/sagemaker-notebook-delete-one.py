#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
#
# Deletes a single, named SageMaker Notebook
import boto3
import argparse

#############
# Functions #
#############

def delete_sagemaker_notebook(region, instance_name):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    # Delete the specified notebook instance
    try:
        sagemaker.delete_notebook_instance(NotebookInstanceName=instance_name)
    except:
        print(f'Unable to delete instance {instance_name}')

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description='A script to delete a single SageMaker Notebook instance')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-n', '--notebook', type=str, required=True, help='The name of the SageMaker notebook instance to stop (ex: my-notebook-instance)')

# Parse the command line arguments
args = parser.parse_args()

print (f'Deleting {args.notebook} in region {args.region}...')
delete_sagemaker_notebook(args.region, args.notebook)
print('Done!')