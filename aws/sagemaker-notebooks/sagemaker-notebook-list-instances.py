#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
# 
# This script lists all SageMaker notebook instances in the current region
#
import boto3
import argparse

def list_notebook_instances(region):
    # Create a SageMaker client for the specified region
    sagemaker_client = boto3.client('sagemaker', region_name=region)

    # Initialize empty list to collect notebook instances
    notebook_instances = []

    # Initial call to list_notebook_instances
    response = sagemaker_client.list_notebook_instances()

    while response:
        for instance in response['NotebookInstances']:
            notebook_name = instance['NotebookInstanceName']
            notebook_status = instance['NotebookInstanceStatus']
            notebook_instances.append((notebook_name, notebook_status))

        # Check if there are more instances to retrieve
        next_token = response.get('NextToken')
        if next_token:
            response = sagemaker_client.list_notebook_instances(NextToken=next_token)
        else:
            response = None

    return notebook_instances

parser = argparse.ArgumentParser(description='List all SageMaker Notebook Instances in a given region.')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')

args = parser.parse_args()
instances = list_notebook_instances(args.region)

if instances:
    print('\nNotebook Instances in region {}:'.format(args.region))
    for name, status in instances:
        print(f"- {name}: {status}")
else:
    print('No notebook instances found in region {}.'.format(args.region))
