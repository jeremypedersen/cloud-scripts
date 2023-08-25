#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-24
#
# Deletes a single, named SageMaker Notebook
import boto3

def delete_sagemaker_notebook(region, instance_name):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    # Delete the specified notebook instance
    print(f'Deleting {instance_name} in region {region}...')
    try:
        sagemaker.delete_notebook_instance(NotebookInstanceName=instance_name)
    except:
        print(f'Unable to delete instance {instance_name}')

# Get input from the user
region = input('Enter the AWS region: ').strip()
instance_name = input('Enter the SageMaker notebook instance name: ').strip()

delete_sagemaker_notebook(region, instance_name)

print('Done!')