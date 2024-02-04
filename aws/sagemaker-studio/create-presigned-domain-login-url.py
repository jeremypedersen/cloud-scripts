#
# Jeremy Pedersen (and ChatGPT)
# Updated: 2024-02-04
#
# Generate a signed URL for a given user and domain
import boto3
import argparse

####################
# Helper functions #
####################

sagemaker = boto3.client('sagemaker')

get_url(username, domain_id):

    # Initialize the SageMaker client
    

    # Create a presigned URL for the domain
    response = sagemaker.create_presigned_domain_url(
                DomainId=domain_id,
                    UserProfileName=username
                    )

    # Get the presigned URL from the response
    presigned_url = response['AuthorizedUrl']

    return presigned_url

##################
# The real stuff #
##################

# Use argparse to get the region name from the command line
parser = argparse.ArgumentParser(description='Generate a signed URL for a given user in a SageMaker domain')
parser.add_argument('-u', '--user', type=str, required=True, help='AWS region name (ex: us-east-1)')
parser.add_argument('-d', '--domain'type=str, required=True, help='Domain ID')

url = get_url(args.user, args.domain)

print(f"Sign in with:\n{presigned_url}")
