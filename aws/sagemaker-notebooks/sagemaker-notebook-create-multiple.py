#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-06
#
import boto3

#############
# Constants #
#############
role_name = SageMaker-NotebookExecutionRole

role_arn = f'arn:aws:iam::{account_id}:role/service-role/SageMaker-NotebookExecutionRole'


# First, we need a function to fetch the current account ID 
# (this will the be account ID) associated with the Access Key or
# token being used by boto3 to authenticate against AWS. 
def get_account_id():
    # Create an STS client
    sts = boto3.client('sts')
    
    # Call the 'get_caller_identity' method which returns details about the IAM user or role whose
    # credentials are used to call the operation
    response = sts.get_caller_identity()
    
    # Extract the account ID from the response
    account_id = response['Account']
    
    return account_id



# Constants
account_id = '115727517926'

# Take user inputs
region = input('Enter region name: ').strip()
num_instances = int(input('Enter number of instances to create: ').strip())
instance_type = input('Enter an instance type (ex: ml.g4dn.2xlarge, ml.g5.2xlarge): ').strip()
namestring = input('Enter a name formatting string, like team\{\}-diffusion (the braces will be replaced by a number): ').strip()

# Initialize the boto3 client
sagemaker = boto3.client('sagemaker', region_name=region)


for i in range(1, num_instances+1):
    instance_name = namestring.format(i)
    print(f'Creating notebook instance: {instance_name}...')
    sagemaker.create_notebook_instance(
        NotebookInstanceName=instance_name,
        InstanceType=instance_type,
        RoleArn=role_arn,
        DirectInternetAccess='Enabled',
        RootAccess='Enabled',
        VolumeSizeInGB=256
    )

print('Done!')