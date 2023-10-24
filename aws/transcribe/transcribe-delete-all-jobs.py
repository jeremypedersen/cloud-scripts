# 
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-24
#
# Terminate all (completed) transcribe jobs in a given region. 
#
import boto3
import argparse

def delete_all_transcribe_jobs(region):
    # Create a Transcribe client for the specified region
    transcribe = boto3.client('transcribe', region_name=region)

    # Loop through the job list until no more jobs are found
    while True:

        # List all Transcribe jobs
        response = transcribe.list_transcription_jobs()

        # Check if there are any jobs to delete
        if 'TranscriptionJobSummaries' not in response:
            print('No Transcribe jobs found in the specified region.')
            break

        # Check if the list is empty
        if len(response['TranscriptionJobSummaries']) == 0:
            print('Job list is empty, exiting.')
            break

        # Delete each Transcribe job
        for job in response['TranscriptionJobSummaries']:
            job_name = job['TranscriptionJobName']
            print(f"Deleting Transcribe job: {job_name}")
            transcribe.delete_transcription_job(TranscriptionJobName=job_name)

parser = argparse.ArgumentParser(description="Delete all Transcribe jobs in a specified region.")
parser.add_argument("-r", "--region", required=True, type=str, help="AWS region where Transcribe jobs should be deleted")
args = parser.parse_args()

delete_all_transcribe_jobs(args.region)
