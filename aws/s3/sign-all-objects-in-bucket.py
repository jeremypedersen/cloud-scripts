#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-24
#
# Generate signed URLs for all objects in a bucket, with
# a 12 hour expiration time
#
import boto3

def generate_signed_urls(region, bucket_name, csvfile):
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


# Request user input
region = input('Enter the AWS region: ')
bucket_name = input('Enter the S3 bucket name: ')

# Open a .csv file called 'urls'
csvfile = open('urls.csv', 'w')
csvfile.write('Object Name, URL\n')

# Generate signed URLs
print('Generating')
generate_signed_urls(region, bucket_name, csvfile)
print('Done!')