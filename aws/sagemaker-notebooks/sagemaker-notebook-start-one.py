#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-24
# 
# Starts a single, named SageMaker Notebook in a given region
import boto3

def start_sagemaker_notebook(region, instance_name):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    # Start the specified notebook instance
    print(f'Starting {instance_name} in region {region}...')
    try:
        sagemaker.start_notebook_instance(NotebookInstanceName=instance_name)
    except:
        print(f'Unable to start instance {instance_name}')

# Get input from the user
region = input('Enter the AWS region: ').strip()
instance_name = input('Enter the SageMaker notebook instance name: ').strip()

start_sagemaker_notebook(region, instance_name)

print('Done!')