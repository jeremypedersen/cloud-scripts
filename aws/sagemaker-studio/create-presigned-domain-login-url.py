#
# Jeremy Pedersen (and ChatGPT)
# Updated: ?
#
import boto3

user = input('Enter username: ').strip()

# Initialize the SageMaker client
sagemaker = boto3.client('sagemaker')

# Create a presigned URL for the domain
response = sagemaker.create_presigned_domain_url(
            DomainId='d-fsc7wfywxh9b',
                UserProfileName=user
                )

# Get the presigned URL from the response
presigned_url = response['AuthorizedUrl']

print(presigned_url)

