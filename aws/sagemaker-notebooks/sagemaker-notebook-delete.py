#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
#
# Deletes one or more SageMaker notebook instances which match a pattern
#
# NOTE: Pattern matching is case-insensitive!
#
import boto3
import argparse

#############
# Functions #
#############

def delete_notebooks(region, pattern):
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
            
            if pattern.lower() in instance_name.lower():
                # Delete each notebook instance
                print(f'Deleting {instance_name}...')
                try:
                    sagemaker.delete_notebook_instance(NotebookInstanceName=instance_name)
                except:
                    print(f'Unable to delete instance {instance_name}')
        
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
parser = argparse.ArgumentParser(description='A script to delete all SageMaker Notebooks in a given region')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-p', '--pattern', type=str, required=True, help='The pattern to match for notebook names (ex: "my-notebook-")')

# Parse the command line arguments
args = parser.parse_args()

print('Deleting notebook(s)...')
delete_notebooks(args.region, args.pattern)
print('Done!')