import boto3
import sys

ec2 = boto3.resource('ec2')

print('########################################')
print('############# Now Building #############')
print('########################################')


vpc = ec2.create_vpc(CidrBlock='192.168.0.0/16')
# we can assign a name to vpc, or any resource, by using tag
vpc.create_tags(Tags=[{"Key": "Name", "Value": "JtR-Cloud"}])
vpc.wait_until_available()
print('Your VPC ID is: ',vpc.id)

# create then attach internet gateway
ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
ig.create_tags(Tags=[{"Key": "Name", "Value": "IntGW"}])
print('Internet Gateway online, ID: ',ig.id)

# create a route table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=ig.id)
print('Route Tables Built')

# create public subnet
subnet1 = ec2.create_subnet(CidrBlock='192.168.1.0/24', VpcId=vpc.id)
subnet1.create_tags(Tags=[{"Key": "Name", "Value": "public"}])
print(subnet1.id)
S1 = subnet1.id
print('Public Subnet, Setup')

# create private subnet
subnet2 = ec2.create_subnet(CidrBlock='192.168.2.0/24', VpcId=vpc.id)
subnet2.create_tags(Tags=[{"Key": "Name", "Value": "private"}])
print(subnet2.id)
S2 - subnet2.id
print('Private Subnet, Setup')

# associate the route table with the subnet

route_table.associate_with_subnet(SubnetId=subnet1.id)
route_table.associate_with_subnet(SubnetId=subnet2.id)
print('Associated Subnets With Route Table')

# Create sec group
sec_groupPrivate = ec2.create_security_group(
    GroupName='privateaccess', Description='Security Group for Internal Asets', VpcId=vpc.id)
sec_groupPrivate.authorize_ingress(
    CidrIp='192.168.0.0/16',
    IpProtocol='icmp',
    FromPort=-1,
    ToPort=-1
)
print('Private Security Group is Securing Things')

sec_groupPublic = ec2.create_security_group(
    GroupName='publicaccess', Description='Security Group for Exnternally Facing Asets', VpcId=vpc.id)
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
print('Public Security Group is Securing Things Too! Only SSH and ICMP Traffic is Permitted')

print('Instances Are Being Built, This Could Take a Minute')
instances = ec2.create_instances(
    ImageId='ami-3bfab942', InstanceType='t2.micro', MaxCount=1, MinCount=1, KeyName="DistributedKey",
    NetworkInterfaces=[{'SubnetId': subnet1.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_groupPublic.group_id]}])

instances = ec2.create_instances(
    ImageId='ami-3bfab942', InstanceType='t2.micro', MaxCount=2, MinCount=1,
    NetworkInterfaces=[{'SubnetId': subnet2.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': False, 'Groups': [sec_groupPrivate.group_id]}])


instances[0].wait_until_running()

print(instances[0].id)

print('')

print('########################################')

print('Your Private Internal IP Addresses Are(192.168.1.* is The Controller Node): ')
text_file = open("PrivateIps.txt", "w")
for subnet in vpc.subnets.all():
    for instance in subnet.instances.all():
        print instance.private_ip_address
        text_file.write(instance.private_ip_address)
        text_file.write("\n")
text_file.close()

print('########################################')

print('')

print('Your Public IP Address is: ')
for subnet in vpc.subnets.all():
    for instance in subnet.instances.all():
        print instance.public_ip_address
print('########################################')






