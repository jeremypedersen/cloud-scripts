#
# Author: Jeremy Pedersen (and ChatGPT)
# Updated: 2023-10-11
#
# Delete a specific VPC from a given region
#
import boto3
import argparse

#############
# Functions #
#############

def delete_vpc(region, vpc_id):

    ec2 = boto3.client('ec2', region_name=region)

    print('=' * 30)
    print(f'Deleting VPC {vpc_id}')
    print('=' * 30)
    
    # Delete NAT Gateways and their associated EIPs
    for nat in ec2.describe_nat_gateways(Filters=[{'Name':'vpc-id', 'Values':[vpc_id]}])['NatGateways']:
        try:
            ec2.delete_nat_gateway(NatGatewayId=nat['NatGatewayId'])
        except:
            print(f"unable to delete NAT gateway {nat['NatGatewayId']}")
        # Wait for the NAT Gateway to be deleted
        waiter = ec2.get_waiter('nat_gateway_deleted')
        waiter.wait(NatGatewayIds=[nat['NatGatewayId']])
        
        # Release the EIP associated with the NAT Gateway
        for address in nat.get('NatGatewayAddresses', []):
            if 'AllocationId' in address:
                try:
                    ec2.release_address(AllocationId=address['AllocationId'])
                except:
                    print(f"Unable to release EIP address with ID {address['AllocationId']}, perhaps it has already been deleted?")

    # Detach and delete all gateways associated with the vpc
    for gw in ec2.describe_internet_gateways(Filters=[{'Name':'attachment.vpc-id', 'Values':[vpc_id]}])['InternetGateways']:
        for attachment in gw['Attachments']:
            try:
                ec2.detach_internet_gateway(InternetGatewayId=gw['InternetGatewayId'], VpcId=attachment['VpcId'])
            except:
                print(f"Unable to detach gateway {gw['InternetGatewayId']} from VPC {attachment['VpcId']}, trying to continue anyway...")
        try:
            ec2.delete_internet_gateway(InternetGatewayId=gw['InternetGatewayId'])
        except:
            print(f"Unable to delete Internet Gateway {gw['InternetGatewayId']}, trying to continue anyway...")

    # Delete all route table associations
    for rt in ec2.describe_route_tables(Filters=[{'Name':'vpc-id', 'Values':[vpc_id]}])['RouteTables']:
        for rta in rt.get('Associations', []):
            if not rta.get('Main', False):
                try:
                    ec2.disassociate_route_table(AssociationId=rta['RouteTableAssociationId'])
                except:
                    print(f"Unable to disassociate route table {rta['RouteTableAssociationId']} from VPC {vpc_id}, trying to continue anyway...")
        try:
            ec2.delete_route_table(RouteTableId=rt['RouteTableId'])
        except:
            print(f"Unable to delete route table {rt['RouteTableId']}, trying to continue anyway...")

    # Delete any instances, network interfaces, and subnets
    for subnet in ec2.describe_subnets(Filters=[{'Name':'vpc-id', 'Values':[vpc_id]}])['Subnets']:
        for instance in ec2.describe_instances(Filters=[{'Name':'subnet-id', 'Values':[subnet['SubnetId']]}])['Reservations']:
            for inst in instance['Instances']:
                try:
                    ec2.terminate_instances(InstanceIds=[inst['InstanceId']])
                except:
                    print(f"Unable to terminate EC2 instance {inst['InstanceId']}, trying to continue anyway..")
                print(f"Terminating instance {inst['InstanceId']}")
                waiter = ec2.get_waiter('instance_terminated')
                waiter.wait(InstanceIds=[inst['InstanceId']])
        try:
            ec2.delete_subnet(SubnetId=subnet['SubnetId'])
        except:
            print(f"Unable to delete subnet {subnet['SubnetId']}, trying to continue anyway..")

    # Delete all security group rules and security groups
    for sg in ec2.describe_security_groups(Filters=[{'Name':'vpc-id', 'Values':[vpc_id]}])['SecurityGroups']:

        # Function to create a rule for revoking based on the permission
        def create_revoke_rule(permission):
            rule = {'IpProtocol': permission['IpProtocol']}
            if 'FromPort' in permission and 'ToPort' in permission:
                rule['FromPort'] = permission['FromPort']
                rule['ToPort'] = permission['ToPort']
            if 'IpRanges' in permission:
                rule['IpRanges'] = permission['IpRanges']
            if 'UserIdGroupPairs' in permission:
                rule['UserIdGroupPairs'] = permission['UserIdGroupPairs']
            return rule

        # Delete all inbound rules
        try:
            if 'IpPermissions' in sg and sg['IpPermissions']:
                for permission in sg['IpPermissions']:
                    rule = create_revoke_rule(permission)
                    ec2.revoke_security_group_ingress(GroupId=sg['GroupId'], IpPermissions=[rule])
        except Exception as e:
            print(f"Error deleting inbound rules for security group with ID {sg['GroupId']}: {e}")

        # Delete all outbound rules
        if sg['GroupName'] != 'default':
            try:
                if 'IpPermissionsEgress' in sg and sg['IpPermissionsEgress']:
                    for permission in sg['IpPermissionsEgress']:
                        rule = create_revoke_rule(permission)
                        ec2.revoke_security_group_egress(GroupId=sg['GroupId'], IpPermissions=[rule])
            except Exception as e:
                print(f"Error deleting outbound rules for security group with ID {sg['GroupId']}: {e}")

            # Delete the security group itself
            print(f"Deleting security group {sg['GroupName']}")
            try:
                ec2.delete_security_group(GroupId=sg['GroupId'])
            except Exception as e:
                print(f"Unable to delete security group with ID {sg['GroupId']}, error: {e}")

    # Delete Network ACLs and their rules
    for nacl in ec2.describe_network_acls(Filters=[{'Name':'vpc-id', 'Values':[vpc_id]}])['NetworkAcls']:
        
        # Delete inbound rules
        for entry in nacl['Entries']:

            if not entry['Egress'] and entry['RuleNumber'] != 32767:
                ec2.delete_network_acl_entry(NetworkAclId=nacl['NetworkAclId'], RuleNumber=entry['RuleNumber'], Egress=False)

        # Delete outbound rules
        for entry in nacl['Entries']:

            if entry['Egress'] and entry['RuleNumber'] != 32767:
                ec2.delete_network_acl_entry(NetworkAclId=nacl['NetworkAclId'], RuleNumber=entry['RuleNumber'], Egress=True)
        
        # Don't delete the default network ACL, but the rules should be removed
        if not nacl['IsDefault']:
            ec2.delete_network_acl(NetworkAclId=nacl['NetworkAclId'])

    # Delete all VPC endpoints associated with the VPC
    try:
        endpoints = ec2.describe_vpc_endpoints(Filters=[{'Name':'vpc-id', 'Values':[vpc_id]}])['VpcEndpoints']
        if endpoints:
            endpoint_ids = [endpoint['VpcEndpointId'] for endpoint in endpoints]
            ec2.delete_vpc_endpoints(VpcEndpointIds=endpoint_ids)
    except Exception as e:
        print(f"Error deleting VPC endpoints associated with VPC {vpc_id}: {e}")

    # List all the VPC endpoints for the given VPC
    response = ec2.describe_vpc_endpoints(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    vpc_endpoints = response['VpcEndpoints']
    
    for vpc_endpoint in vpc_endpoints:
        endpoint_id = vpc_endpoint['VpcEndpointId']
        try:
            print(f'Deleting VPC Endpoint {endpoint_id}...')
            ec2_client.delete_vpc_endpoints(VpcEndpointIds=[endpoint_id])
            print(f'VPC Endpoint {endpoint_id} deleted successfully!')
        except Exception as e:
            print(f'Failed to delete VPC Endpoint {endpoint_id}. Reason: {e}')

    # Delete the vpc
    try:
        ec2.delete_vpc(VpcId=vpc_id)
    except Exception as e:
        print(f"Unable to delete VPC {vpc_id}, continuing on...")
        print(f'Error: {e}')

##################
# The real stuff #
##################

# Use argparse to get the region name from the command line
parser = argparse.ArgumentParser(description='A script to delete all the VPCs in a specified region')
parser.add_argument('-r', '--region', type=str, required=True, help='Region to delete NAT gateways from')
parser.add_argument('-v', '--vpc-id', type=str, required=True, help='VPC ID to delete')

args = parser.parse_args()

delete_vpc(args.region, args.vpc_id)

print('Done!')
