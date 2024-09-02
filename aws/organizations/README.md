# AWS Organizations scripts

Scripts to manage AWS organizations. The focus is on cleaning expensive resources that might still be "hanging out" in the accounts within an Organization. **Don't run this on a production AWS Org**, this is mostly for cleanup in test environments. Scripts include:

- `org-delete-ec2-instances.py`: Delete all EC2 instances in a given region for all accounts in the Org
- `org-delete-iam-users.py`: Delete all IAM users for all accounts in the Org
- `org-delete-notebooks.py`: Delete all SageMaker Notebook Instances in a given region for all accounts in the Org
- `org-delete-sagemaker-apps.py`: Delete all SageMaker Domain Apps in a given region for all accounts in the Org
- `org-delete-sagemaker-endpoints.py`: Delete all SageMaker Inference Endpoints in a given region for all accounts in the Org
- `org-generate-nuke-commands.py`: Generate commands to run the [aws nuke script](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/automate-deletion-of-aws-resources-by-using-aws-nuke.html) against each account in the Org
- `org-set-alias.py`: Set an alis for the Org (the aws-nuke script needs this to work correctly)
- `org-stop-ec2-instances.py`: Stop all EC2 instances in a given region for all accounts in the Org
- `org-stop-notebooks.py`: Stop all Jupyter Notebook Instances in a given region for all accounts in the Org

