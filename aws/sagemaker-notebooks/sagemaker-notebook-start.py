#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
#
# Starts one or more stopped SageMaker Notebooks in a given region, matching a pattern
#
# NOTE: Pattern matching is case-insensitive 
#
import boto3
import argparse

#############
# Functions #
#############

def start_notebooks(region, pattern):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    # Initialize the NextToken value
    next_token = None

    while True:
        # If NextToken is not None, include it in the request
        if next_token:
            notebook_instances = sagemaker.list_notebook_instances(NextToken=next_token)
        else:
            notebook_instances = sagemaker.list_notebook_instances()

        # Iterate over each instance
        for instance in notebook_instances['NotebookInstances']:
            instance_name = instance['NotebookInstanceName']

            # Only start the notebook instance if it is in the Stopped state
            if instance['NotebookInstanceStatus'] == 'Stopped' and pattern.lower() in instance_name.lower():
                print(f'Starting {instance_name}...')
                try:
                    sagemaker.start_notebook_instance(NotebookInstanceName=instance_name)
                except:
                    print(f'Unable to start instance {instance_name}...')
        
        # If the response includes a NextToken, assign it to the variable for the next loop iteration
        if 'NextToken' in notebook_instances:
            next_token = notebook_instances['NextToken']
        else:
            # If there is no NextToken in the response, we've reached the end of the list
            break

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description='A script to start all SageMaker Notebooks in a given region')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-p', '--pattern', type=str, required=True, help='The pattern to match for notebook names (ex: "my-notebook-")')

# Parse the command line arguments
args = parser.parse_args()

print('Starting notebook(s)...')
start_notebooks(args.region, args.pattern)
print('Done!')