#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-19
#
import boto3

# Constants
role_arn = 'arn:aws:iam::115727517926:role/service-role/SageMaker-NotebookExecutionRole'

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