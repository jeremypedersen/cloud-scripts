#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-08
#
# Delete all NAT GWs from a given region
#
# This script helps reduce NAT gateway costs, by eliminating any NAT Gateways
# that may have been created while testing or using other services
#
import boto3
import time
import argparse

#############
# Functions #
#############

def delete_nat_gateways(region_name):
    ec2 = boto3.client('ec2', region_name=region_name)

    # List all NAT Gateways
    nat_gateways = ec2.describe_nat_gateways(Filters=[{'Name': 'state', 'Values': ['pending', 'available']}])

    for nat in nat_gateways['NatGateways']:
        # For each NAT Gateway, delete it and release the associated EIP
        nat_gateway_id = nat['NatGatewayId']
        try:
            print(f"Deleting NAT Gateway {nat_gateway_id}")
            ec2.delete_nat_gateway(NatGatewayId=nat_gateway_id)
            
            # Wait for a while before releasing the EIP to ensure the NAT Gateway is deleted
            time.sleep(10)

            for address in nat['NatGatewayAddresses']:
                if 'AllocationId' in address:
                    allocation_id = address['AllocationId']
                    print(f"Releasing EIP with Allocation ID {allocation_id}")
                    ec2.release_address(AllocationId=allocation_id)
        except Exception as e:
            print(f"Failed to delete NAT Gateway {nat_gateway_id} or release its EIP due to {str(e)}")

##################
# The real stuff #
##################

# Use argparse to get the region name from the command line
parser = argparse.ArgumentParser(description='A script to delete all the NAT Gateways in a specified region')
parser.add_argument("-r", "--region", type=str, required=True, help='Region to delete NAT gateways from')

args = parser.parse_args()

delete_nat_gateways(args.region)

print('Done!')