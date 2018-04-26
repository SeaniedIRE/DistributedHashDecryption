import sys
import boto3
import botocore
import os
import paramiko
from paramiko import SSHClient
from scp import SCPClient

ec2 = boto3.resource('ec2')

globalSubnet1val=''
globalSubnet2val=''
ec2client = ec2.meta.client
client = boto3.client('ec2')

vpc = ec2.create_vpc(CidrBlock='192.168.0.0/16')
# we can assign a name to vpc, or any resource, by using tag
vpc.create_tags(Tags=[{"Key": "Name", "Value": "TEST|CLOUD"}])
vpc.wait_until_available()
print('Your VPC ID is: ',vpc.id)

ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
ig.create_tags(Tags=[{"Key": "Name", "Value": "IntGWTest"}])
print('Internet Gateway online, ID: ',ig.id)

route_table_public = vpc.create_route_table()
route_table_private = vpc.create_route_table()

routePublic = route_table_public.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=ig.id)
print('Route Tables Built')


  # create public subnet
subnet1 = ec2.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc.id)
subnet1.create_tags(Tags=[{"Key": "Name", "Value": "TESTpublic"}])
print(subnet1.id)
globalSubnet1val = subnet1.id
print('Public Subnet, Setup')

# create private subnet
subnet2 = ec2.create_subnet(CidrBlock='192.168.2.0/24', VpcId=vpc.id)
subnet2.create_tags(Tags=[{"Key": "Name", "Value": "TESTprivate"}])
print(subnet2.id)
globalSubnet2val = subnet2.id
print('Private Subnet, Setup')

# associate the route table with the subnet

route_table_public.associate_with_subnet(SubnetId=subnet1.id)


natGW = client.create_nat_gateway(AllocationId='eipalloc-da82e9e7', SubnetId=subnet2.id)
waiter = client.get_waiter('nat_gateway_available')
waiter.wait(NatGatewayIds=[natGW['NatGateway']['NatGatewayId']])
print('Waiting for gatewat Status: Availible ')


routePublic = route_table_private.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=natGW ['NatGateway']['NatGatewayId'])
print('Route Tables Built 2')

route_table_private.associate_with_subnet(SubnetId=subnet2.id)


# Create sec group
sec_groupPrivate = ec2.create_security_group(
   GroupName='TESTprivateaccess', Description='Security Group for Internal Asets', VpcId=vpc.id)
sec_groupPrivate.authorize_ingress(
    CidrIp='192.168.0.0/16',
        IpProtocol='icmp',
        FromPort=-1,
        ToPort=-1
)
sec_groupPrivate.authorize_ingress(
	CidrIp='192.168.0.0/16',
    	IpProtocol='tcp',
        FromPort=22,
        ToPort=22
)

print('Private Security Group is Securing Things')

sec_groupPublic = ec2.create_security_group(
    GroupName='TESTpublicaccess', Description='Security Group for Exnternally Facing Asets', VpcId=vpc.id)
sec_groupPublic.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='icmp',
    FromPort=-1,
    ToPort=-1
)
sec_groupPublic.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22
)

