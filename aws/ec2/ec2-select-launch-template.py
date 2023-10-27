import argparse
import boto3

def list_launch_templates(region):
    try:
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_launch_templates()
        return response['LaunchTemplates']
    except Exception as e:
        print(f"Error listing launch templates: {str(e)}")
        return []

def select_launch_template(templates):
    if not templates:
        print("No launch templates found in the specified region.")
        return None

    print("Select a launch template:")
    for index, template in enumerate(templates, start=1):
        print(f"{index}. {template['LaunchTemplateName']}")

    while True:
        try:
            choice = int(input("Enter the number of the desired launch template: "))
            if 1 <= choice <= len(templates):
                return templates[choice - 1]['LaunchTemplateName']
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def create_ec2_instance(region, launch_template_name):
    try:
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.run_instances(
            LaunchTemplateName=launch_template_name,
            MinCount=1,
            MaxCount=1
        )
        instance_id = response['Instances'][0]['InstanceId']
        print(f"EC2 instance {instance_id} is launching.")
    except Exception as e:
        print(f"Error creating EC2 instance: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Create an EC2 instance from a selected launch template")
    parser.add_argument("-r", "--region", required=True, help="AWS region for EC2 instance creation")
    args = parser.parse_args()

    region = args.region
    launch_templates = list_launch_templates(region)
    launch_template_name = select_launch_template(launch_templates)

    if launch_template_name:
        create_ec2_instance(region, launch_template_name)

if __name__ == "__main__":
    main()
