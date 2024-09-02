#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
# 
# This script performs all the actions needed to create one or more SageMaker notebook
# instances with:
# 1. Permission to access a shared S3 bucket (read only on the whole bucket, plus write to a specific prefix)
# 2. Permission to send logs to CloudWatch
# 3. Permission to use Amazon Polly
#
# The script will also create a set of IAM users with limited permissions to 
# access the AWS console and stop, start, and generate signed URLs for the 
# SageMaker notebooks.
#
# Use the `-n` or `--number` argument to control the number of instances created
# (1 or more)
#
# IMPORTANT: If you specify a lifecycle policy that depends on access to other services
# (such as S3), you will need to modify the SageMaker notebook execution role code in 
# `create_execution_role()` to grant whatever additional permissions are required
#  for your 'Start notebook' and 'Create notebook' scripts to run successfully
#
import boto3
import argparse
import json
import csv
import random

#############
# Functions #
#############

def get_account_id():
    # Create an STS client
    sts = boto3.client('sts')

    # Call the 'get_caller_identity' function
    response = sts.get_caller_identity()

    # Return the account ID
    return response['Account']

# Fetch role ARN using role name
def get_role_arn(role_name):
    iam = boto3.client('iam')

    try:
        response = iam.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        return role_arn
    except iam.exceptions.NoSuchEntityException:
        print(f'The role {role_name} does not exist.')
        return None

# Fetch IAM policy ARN using policy name
def get_policy_arn(policy_name):
    iam = boto3.client('iam')

    try:
        response = iam.get_policy(PolicyArn=f'arn:aws:iam::aws:policy/{policy_name}')
        policy_arn = response['Policy']['Arn']
        return policy_arn
    except iam.exceptions.NoSuchEntityException:
        print(f'The policy {policy_name} does not exist.')
        return None

def create_execution_role(bucket_name, postfix):
    iam = boto3.client('iam')
    sagemaker = boto3.client('sagemaker')

    # Step 1: Create an IAM role for SageMaker
    role_name = f'SageMakerNotebook-ExecutionRoleBatch-{postfix}'
    assume_role_policy_document = {
        'Version': '2012-10-17',
        'Statement': [{
            'Action': 'sts:AssumeRole',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'sagemaker.amazonaws.com'
            }
        }]
    }
    
    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
            Description='SageMaker Notebook Execution Role'
        )
        role_arn = response['Role']['Arn']
    except:
        print('Unable to create role, attempting to look up role ARN...')
        role_arn = get_role_arn(role_name)

    # Step 2: Attach policies for the required permissions to the IAM role

    # 1. Full permissions for Amazon Polly
    try:
        polly_policy_arn = 'arn:aws:iam::aws:policy/AmazonPollyFullAccess'
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=polly_policy_arn
        )
    except:
        print('Unable to attach permission for Polly, assuming they are already there')

    if bucket_name:
        # 2. Read-only permissions on a shared S3 bucket, plus write permission to 
        # a specific prefix
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Action': [
                        's3:ListBucket',
                        's3:GetObject',
                        's3:HeadObject'
                    ],
                    'Resource': f'arn:aws:s3:::{bucket_name}'
                },
                {
                    'Effect': 'Allow',
                    'Action': [
                        's3:ListBucket',
                        's3:GetObject',
                        's3:HeadObject'
                    ],
                    'Resource': f'arn:aws:s3:::{bucket_name}/*'
                },
                {
                    'Effect': 'Allow',
                    'Action': [
                        's3:GetObject',
                        's3:PutObject',
                        's3:DeleteObject'
                    ],
                    'Resource': f'arn:aws:s3:::{bucket_name}/{postfix}/*'
                }
            ]
        }
        policy_name = f'S3AccessToSharedBucket-{postfix}'

        # Add a note to the output so the user of the script is aware that 
        # the bucket policy exists and knows the proper path
        print(f'Bucket policy created to allow {postfix} to upload objects to s3://{bucket_name}/{postfix}')

        try:
            response = iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(bucket_policy)
            )
            bucket_policy_arn = response['Policy']['Arn']
        except:
            print('Unable to create S3 bucket access policy, attempting to locate ARN...')
            get_policy_arn(policy_name)

        try:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=bucket_policy_arn
            )
        except:
            print('Failed to attach S3 bucket access policy to role, assuming it is already there')

    # 3. Minimum permissions to send logs to CloudWatch
    cloudwatch_log_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Effect': 'Allow',
            'Action': [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents'
            ],
            'Resource': '*'
        }]
    }

    cloudwatch_policy_name = f'SageMakerLogsToCloudWatch-{postfix}'
    try:
        response = iam.create_policy(
            PolicyName=cloudwatch_policy_name,
            PolicyDocument=json.dumps(cloudwatch_log_policy)
        )
        cloudwatch_policy_arn = response['Policy']['Arn']
    except:
        print('Failed to locate CloudWatch access policy, trying to locate ARN...')
        get_policy_arn(cloudwatch_policy_name)

    try:
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=cloudwatch_policy_arn
        )
    except:
        print('Failed to attach CloudWatch access policy to role, assuming it is already there')

    return role_arn

def create_iam_users(region, num_users, namestring, filename):
    iam = boto3.client('iam')

     # Open a new CSV file for writing user credentials
    file = open(filename, 'w', newline='')
    writer = csv.writer(file)
    writer.writerow(['Username', 'Password', 'Logon URL'])

    # Step 1, create the IAM user
    for i in range(1, num_users+1):
        # Format username
        postfix = namestring.format(i)
        user_name = f'{postfix}-notebook-user'

        try:
            response = iam.create_user(UserName=user_name)
            print(f'User {user_name} created successfully!')
        except:
            print(f'User {user_name} already exists!')

        # Generate logon profile
        password = f'{user_name}-{str(random.randint(10000,90999))}$'

        try:
            iam.create_login_profile(UserName=user_name, Password=password)
        except:
            print(f'Unable to create logon profile for {user_name}, continuing anyway')

        # Generate logon URL
        account_id = get_account_id()
        login_url = f'https://{account_id}.signin.aws.amazon.com/console' 
        writer.writerow([user_name, password, login_url])

        # Step 2: Attach the inline policy
        policy_document = {
                    'Version': '2012-10-17',
                    'Statement': [
                        {
                            'Effect': 'Allow',
                            'Action': [
                                'sagemaker:DescribeNotebookInstance',
                                'sagemaker:StartNotebookInstance',
                                'sagemaker:StopNotebookInstance',
                                'sagemaker:CreatePresignedNotebookInstanceUrl',
                                'sagemaker:ListTags'
                            ],
                            'Resource': f'arn:aws:sagemaker:{region}:*:notebook-instance/{postfix}'
                        },
                        {
                            'Effect': 'Allow',
                            'Action': [
                                'sagemaker:ListNotebookInstances',
                                'sagemaker:ListCodeRepositories',
                            ],
                            'Resource': '*'
                        }
                    ]
                }

        try:
            iam.put_user_policy(
                UserName=user_name,
                PolicyName=f'SageMakerNotebookPolicy-{user_name}',
                PolicyDocument=json.dumps(policy_document)
            )
            print(f'Inline policy attached to user {user_name} successfully!')
        except:
            print(f'Error attaching inline policy to user {user_name}. Perhaps it is already attached?')

    # Close the CSV file
    file.close()

def create_notebook_instances(region, bucket_name, num_instances, instance_type, namestring, disksize, lifecycle):
    # Initialize the boto3 client
    sagemaker = boto3.client('sagemaker', region_name=region)

    for i in range(1, num_instances+1):
        instance_name = namestring.format(i)
        print(f'Creating notebook instance: {instance_name}...')

        # Create execution role for Notebook instance
        role_arn = create_execution_role(bucket_name, instance_name)

        # Attaching lifecycle configurations is optional, so we need to make two separate calls depending on
        # whether or not a lifecycle configuration was specified
        try:
            if lifecycle:
                sagemaker.create_notebook_instance(
                    NotebookInstanceName=instance_name,
                    InstanceType=instance_type,
                    RoleArn=role_arn,
                    DirectInternetAccess='Enabled',
                    RootAccess='Enabled',
                    VolumeSizeInGB=disksize,
                    LifecycleConfigName=lifecycle  # Added this line to attach the lifecycle policy
                )
            else:
                sagemaker.create_notebook_instance(
                    NotebookInstanceName=instance_name,
                    InstanceType=instance_type,
                    RoleArn=role_arn,
                    DirectInternetAccess='Enabled',
                    RootAccess='Enabled',
                    VolumeSizeInGB=disksize
                )
        except:
            print(f'Unable to create instance {instance_name}, perhaps it already exists?')

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description='A script to create multiple SageMaker Notebooks in a given region')
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-n', '--number', type=int, required=True, help='The number of SageMaker notebooks to create')
parser.add_argument('-t', '--type', type=str, required=True, help='The instance type to use (ex: ml.g4dn.2xlarge, ml.g5.2xlarge)')
parser.add_argument('-s', '--namestring', type=str, required=True, help='The name formatting string to use (ex: team\{\}-diffusion, where the braces will be replaced by a number)', default='team{}')
parser.add_argument('-o', '--output', type=str, required=True, help='The output file to write IAM user credentials to (ex: iam-credentials.csv)')
parser.add_argument('-b', '--bucket', type=str, required=False, help='Name of a shared S3 bucket, used for hosting content needed by all notebooks (ex: shared-models-2023)')
parser.add_argument('-d', '--disksize', type=int, required=False, help='The size of the root volume in GB (ex: 256)', default=256)
parser.add_argument('-l', '--lifecycle', type=str, required=False, help='The lifecycle configuration to use for the notebooks (ex: lifecycle-2023)')

# Parse the command line arguments
args = parser.parse_args()

# Next, create the IAM users and output to CSV file (at present, the script
# creates a single IAM user for each SageMaker notebook instance)
create_iam_users(args.region, args.number, args.namestring, args.output)

# Finally, create the instances
create_notebook_instances(args.region, args.bucket, args.number, args.type, args.namestring, args.disksize, args.lifecycle)

print('Done!')