#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-06
#
# Generate signed URLs for all objects in a bucket, with
# a 12 hour expiration time
#
import boto3
import argparse

#############
# Functions #
#############

def generate_signed_urls(region, bucket_name, filename):
    # Open a .csv file called 'urls'
    csvfile = open(filename, 'w')
    csvfile.write('Object Name, URL\n')

    # Initialize the S3 client
    s3 = boto3.client('s3', region_name=region)

    # Iterate over all the objects in the bucket
    objects = s3.list_objects_v2(Bucket=bucket_name)

    # Check if there are any objects
    if objects.get('Contents'):
        for obj in objects['Contents']:
            # Generate the signed URL
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': obj['Key']
                },
                ExpiresIn=43200 # 12 hours in seconds
            )

            # Write object name and signed URL into csvfile
            csvfile.write(f"{obj['Key']},{url}\n")

            #print(url)
    else:
        print(f'No objects found in the bucket {bucket_name}.')

##################
# The real stuff #
##################

# Initialize the argument parser
parser = argparse.ArgumentParser(description="A script to create signed URLs for all objects in an S3 bucket, with a 12 hour expiration time")
parser.add_argument('-r', '--region', type=str, required=True, help='The AWS region to use (ex: us-west-1)')
parser.add_argument('-b', '--bucket', type=str, required=True, help='The name of the S3 bucket (ex: my-s3-bucket)')
parser.add_argument('-o', '--output', type=str, required=True, help='The name of the output .csv file (ex: urls.csv)')

# Parse the command line arguments
args = parser.parse_args()

# Generate signed URLs
print('Generating signed URLs..')
generate_signed_urls(args.region, args.bucket, args.output)
print('Done!')