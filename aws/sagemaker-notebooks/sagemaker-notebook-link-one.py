#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-19
#
# Creates a signed URL for a single Jupyter Notebook instance
import boto3

def create_presigned_url(region, instance_name):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    # Create a presigned URL for the specified notebook instance
    print(f'Generating URL for {instance_name} in region {region}...')
    try:
        response = sagemaker.create_presigned_notebook_instance_url(NotebookInstanceName=instance_name)
        print('=' * 30)
        print(response['AuthorizedUrl'])
        print('=' * 30)
    except:
        print(f'Unable to generate URL for {instance_name}')

# Get input from the user
region = input("Enter the AWS region: ").strip()
instance_name = input("Enter the SageMaker notebook instance name: ").strip()

create_presigned_url(region, instance_name)

print('Done!')