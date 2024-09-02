#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-11
#
# List all VPCs in a specified region (along with their subnets, 
# route tables, security groups, and NAT gateways)
#
import boto3
import argparse

#############
# Functions #
#############

def list_vpcs(region):
    ec2 = boto3.resource('ec2', region_name=region)
    
    for vpc in ec2.vpcs.all():
        print(f'VPC ID: {vpc.id}')

        # Get the VPC name if available
        tags = {tag['Key']: tag['Value'] for tag in vpc.tags or []}
        name = tags.get('Name', '')
        print(f'VPC Name: {name}')
        
        # List Subnets
        print('Subnets:')
        for subnet in vpc.subnets.all():
            print(f"  - {subnet.id}")
        
        # List Route Tables
        print('Route Tables:')
        for rt in vpc.route_tables.all():
            print(f"  - {rt.id}")

        # List Security Groups
        print('Security Groups:')
        for sg in vpc.security_groups.all():
            print(f"  - {sg.id} ({sg.group_name})")
        
        # List NAT Gateways
        print('NAT Gateways:')
        nat_gateways = boto3.client('ec2', region_name=region).describe_nat_gateways(Filters=[{'Name':'vpc-id', 'Values':[vpc.id]}])
        for nat in nat_gateways['NatGateways']:
            print(f"  - {nat['NatGatewayId']}")
        
        print("="*40)

##################
# The real stuff #
##################

# Parse command line arguments
parser = argparse.ArgumentParser(description='List all VPCs in an AWS region.')
parser.add_argument('-r', '--region', type=str, required=True, help='AWS region')
args = parser.parse_args()

list_vpcs(args.region)
