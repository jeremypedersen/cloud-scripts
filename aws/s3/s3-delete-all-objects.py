#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-06
#
# Delete all objects (and versions, and multipart upload fragments)
# from a bucket
#
import boto3
import argparse

#############
# Functions #
#############

def delete_all_objects(bucket_name):
    s3_client = boto3.client('s3')

    # Delete all object versions and delete markers
    object_versions = s3_client.list_object_versions(Bucket=bucket_name)
    
    to_delete = []
    
    if 'Versions' in object_versions:
        to_delete.extend(
            [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in object_versions['Versions']]
        )
        
    if 'DeleteMarkers' in object_versions:
        to_delete.extend(
            [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in object_versions['DeleteMarkers']]
        )
    
    if to_delete:
        s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': to_delete})

    # Delete all multipart uploads
    multipart_uploads = s3_client.list_multipart_uploads(Bucket=bucket_name)
    if 'Uploads' in multipart_uploads:
        for upload in multipart_uploads['Uploads']:
            s3_client.abort_multipart_upload(
                Bucket=bucket_name,
                Key=upload['Key'],
                UploadId=upload['UploadId']
            )

    print(f'Deleted all objects and versions from bucket {bucket_name}.')

##################
# The real stuff #
##################

# Region name and bucket name should be included as command line 
# arguments, parsed with argparse

# Initialize the argument parser
parser = argparse.ArgumentParser(description="A script to delete all S3 objects from a bucket")
parser.add_argument('-b', '--bucket', type=str, required=True, help='The name of the S3 bucket (ex: my-s3-bucket)')

# Parse the command line arguments
args = parser.parse_args()

print('Deleting all objects...')
delete_all_objects(args.bucket)
print('Done!')