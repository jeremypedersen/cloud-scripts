# DeepRacer Scripts

Scripts to setup and manage sets of SageMaker Notebook instances. 

The following scripts are included:

-`sagemaker-notebook-cleanup-roles.py`: Clean up user roles created by `sagemaker-notebook-create-multiple.py`.
-`sagemaker-notebook-cleanup-users.py`: Clean up users created by `sagemaker-notebook-create-multiple.py`.
-`sagemaker-notebook-create-multiple.py`: Create multiple SageMaker Notebook instances, each with an associated IAM user and SageMaker execution role. Depending on the specified command line arguments, the script can optionally attach a lifecycle configuration to the instance, or grant limited S3 permissions (full read plus prefix-limited write on a specified S3 bucket).
-`sagemaker-notebook-delete-all.py`: Delete all SageMaker Notebook instances in the specified region.
-`sagemaker-notebook-delete-one.py`: Delete one named SageMaker Notebook instance in the specified region.
-`sagemaker-notebook-link-one.py`: Create a signed logon link for one SageMaker Notebook instance in the specified region.
-`sagemaker-notebook-links-all.py`: Create signed logon links for all SageMaker Notebook instances in the specified region. 
-`sagemaker-notebook-list-instances.py`: List all SageMaker Notebook instances in a region, and their current status.
-`sagemaker-notebook-start-all.py`: Start all SageMaker Notebook instances in the specified region.
-`sagemaker-notebook-start-one.py`: Start one named SageMaker Notebook instance in the specified region.
-`sagemaker-notebook-stop-all.py`: Stop all SageMaker Notebook instances in the specified region.
-`sagemaker-notebook-stop-one.py`: Stop one named SageMaker Notebook instance in the specified region.

**Getting help**: All the scripts above accept an `-h` command line argument which will print a list of accepted command line parameters and expected values for each. 
