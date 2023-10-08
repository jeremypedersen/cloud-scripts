#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
#
# Creates a signed URL for a single Jupyter Notebook instance
import boto3
import argparse

#############
# Functions #
#############

def make_notebook_link(region, instance_name):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    try:
        response = sagemaker.create_presigned_notebook_instance_url(NotebookInstanceName=instance_name)
        url = response['AuthorizedUrl']
        print(url)
    except:
        print(f'Unable to generate URL for {instance_name}')

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description='A script to generate a signed URL for a single Jupyter Notebook instance')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-n', '--notebook', type=str, required=True, help='The name of the SageMaker notebook instance to stop (ex: my-notebook-instance)')

# Parse the command line arguments
args = parser.parse_args()

# Print out the link by itself (making it easy to copy-paste or push into a file)
make_notebook_link(args.region, args.notebook)
