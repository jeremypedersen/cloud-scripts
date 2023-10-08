# S3 Scripts

Scripts to manage S3 buckets and the objects they contain.

## `sign-all-objects-in-bucket.py`

Goes through every single object in a bucket, generating 12-hour signed URLs for each object found. It saves results into a CSV file. The bucket name and CSV file name are specified using command line arguments.

## `delete-all-objects-in-bucket.py`

Deletes all the objects in a bucket, including old versions (for versioned buckets) and any fragments leftover from multi-part uploads. The bucket name is specified using a command line argument. 


