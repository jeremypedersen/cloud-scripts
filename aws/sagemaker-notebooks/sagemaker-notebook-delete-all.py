#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-19
#
# Deletes all SageMaker notebook instances in a region
import boto3

# Request region name
region = input('Enter region name: ').strip()

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

print('Done!')