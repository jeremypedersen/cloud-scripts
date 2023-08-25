#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-08-26
#
# Delete all NAT GWs from a given region
#
# This script helps reduce NAT gateway costs, by eliminating any NAT Gateways
# that may have been created while testing or using other services
#
import boto3
import time

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

region = input("Delete all NAT gateways from this region (ex: us-east-1): ").strip()
delete_nat_gateways(region)