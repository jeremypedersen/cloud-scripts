# S3 Scripts

Scripts to manage S3 buckets and the objects they contain.

## `sign-all-objects-in-bucket.py`

Goes through every single object in a bucket, generating 12-hour signed URLs for each object found. It saves results into a CSV file. 