#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-19
#
# Generates signed URLs for all SageMaker Notebooks in a region
import boto3
import csv

# Request region name
region = input('Enter region name: ').strip()

# Initialize the boto3 client
sagemaker = boto3.client('sagemaker', region_name=region)

# Open a new CSV file for writing
file = open('sagemaker_urls.csv', 'w', newline='')
writer = csv.writer(file)
writer.writerow(["name", "URL"])

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

        # Only generate a URL if the notebook instance is 'InService'
        if instance['NotebookInstanceStatus'] == 'InService':
            print(f'Generating URL for {instance_name}...')
            try:
                response = sagemaker.create_presigned_notebook_instance_url(
                    NotebookInstanceName=instance_name
                )
                url = response['AuthorizedUrl']
            except:
                url = 'ERROR'
                print(f'Unable to generate URL for instance {instance_name}')

            # Write the instance name and URL to the CSV file
            writer.writerow([instance_name, url])
    
    # If the response includes a NextToken, assign it to the variable for the next loop iteration
    if 'NextToken' in notebook_instances:
        next_token = notebook_instances['NextToken']
    else:
        # If there is no NextToken in the response, we've reached the end of the list
        break

file.close()
print('Done!')