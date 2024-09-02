#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
#
# Generates signed URLs for one or more SageMaker Notebooks in a region, matching a pattern
#
# NOTE: Pattern matching is case-insensitive 
#
import boto3
import csv
import argparse

#############
# Functions #
#############

def make_notebook_links(region, file_name, pattern):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    # Open a new CSV file for writing
    file = open(file_name, 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(['name', 'URL'])

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
            if instance['NotebookInstanceStatus'] == 'InService' and pattern.lower() in instance_name.lower():
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

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description='A script to generate signed URLs for all SageMaker Notebooks in a given region')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-o', '--output', type=str, required=True, help='The name of the CSV file to write the URLs to (ex: links.csv)')
parser.add_argument('-p', '--pattern', type=str, required=True, help='The pattern to match for notebook names (ex: "my-notebook-")')

# Parse the command line arguments
args = parser.parse_args()

print('Generating notebook link(s)...')
make_notebook_links(args.region, args.output, args.pattern)
print('Done!')