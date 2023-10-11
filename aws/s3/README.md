# S3 Scripts

Scripts to manage S3 buckets and the objects they contain.

- `sign-all-objects-in-bucket.py`: Creates signed download URLs for all objects in a specified bucket, valid for 12 hours, and saves them in a CSV file. 
- `delete-all-objects-in-bucket.py`: Deletes all objects, object versions, multipart upload fragments from a specified bucket. 
