#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-24
#
# This script deletes all the (SageMaker created) EFS filesystems in a region. 
# We need to do this because deleting a SageMaker domain does not automatically 
# delete associated EFS filesystems.
#
# NOTE: We try to be careful by only deleting filesystems tagged with 'ManagedByAmazonSageMakerResource'
import boto3, time

def delete_mount_targets(efs_client, fs_id):
    mount_targets = efs_client.describe_mount_targets(FileSystemId=fs_id)['MountTargets']
    
    for mt in mount_targets:
        mt_id = mt['MountTargetId']
        print(f'Deleting mount target with ID: {mt_id}...')
        efs_client.delete_mount_target(MountTargetId=mt_id)

def delete_efs_filesystems(region):
    # Initialize the EFS client
    efs_client = boto3.client('efs', region_name=region)
    
    # List all file systems
    filesystems = efs_client.describe_file_systems()['FileSystems']
    
    # If no file systems exist, print a message and exit
    if not filesystems:
        print('No EFS filesystems found in region', region)
        return
    
    # Loop through each file system and delete if it has the required tag
    for fs in filesystems:
        fs_id = fs['FileSystemId']
        
        # Fetch the tags for the file system
        tags = efs_client.describe_tags(FileSystemId=fs_id)['Tags']
        
        # Check if the desired tag is present
        has_tag = any(tag['Key'] == 'ManagedByAmazonSageMakerResource' for tag in tags)
        
        if has_tag:
            # First, delete associated mount targets
            delete_mount_targets(efs_client, fs_id)

            # Wait for a few seconds
            print('Waiting for mount targets to be deleted...')
            time.sleep(15)

            # Then, delete the file system
            print(f'Deleting EFS filesystem with ID: {fs_id}...')
            try:
                efs_client.delete_file_system(FileSystemId=fs_id)
                print(f'Deleted EFS filesystem with ID: {fs_id}')
            except Exception as e:
                print(f'Failed to delete EFS filesystem with ID: {fs_id}. Reason: {e}')

region = input('Please input the AWS region (e.g. us-east-1): ')
delete_efs_filesystems(region)
