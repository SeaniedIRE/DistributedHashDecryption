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

def menu():
    os.system('cls' if os.name == 'nt' else 'clear') 
    selection=True
    while selection:
        print 30 * "-" , "MENU" , 30 * "-"
        print "1. Create"
        print "2. Delete"
        print "3. Quit"
        print 66 * "-"

        selection=raw_input("Enter your choice [1-3]: ") 

        if selection=="1":
            createVPC()
            selection=False
        elif selection=="2":
            vpcid = raw_input('Please type the VPC ID: ') 
            vpc_cleanup(vpcid)
            selection=False
        elif selection=="3":
            sys.exit
        else:
            sys.exit
 
def createVPC():
    ec2client = ec2.meta.client

    #ec2 = boto3.resource('ec2')
    os.system('cls' if os.name == 'nt' else 'clear') 
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
    globalSubnet1val = subnet1.id
    print('Public Subnet, Setup')

    # create private subnet
    subnet2 = ec2.create_subnet(CidrBlock='192.168.2.0/24', VpcId=vpc.id)
    subnet2.create_tags(Tags=[{"Key": "Name", "Value": "private"}])
    print(subnet2.id)
    globalSubnet2val = subnet2.id
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

    sec_groupPrivate.authorize_ingress(
    CidrIp='192.168.0.0/16',
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22
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

    instances = ec2.create_instances(
        ImageId='ami-f90a4880', InstanceType='t2.micro', MaxCount=1, MinCount=1, KeyName="DistributedKey",
        NetworkInterfaces=[{'SubnetId': subnet1.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_groupPublic.group_id]}])

    instances = ec2.create_instances(
        ImageId='ami-f90a4880', InstanceType='t2.micro', MaxCount=2, MinCount=1,
        NetworkInterfaces=[{'SubnetId': subnet2.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': False, 'Groups': [sec_groupPrivate.group_id]}])

    print('')
    print('Instances Building(Go Grab a Coffee): ')
    instances[0].wait_until_running()
    print('Instances Building: Done')
    print('')

    print('Waiting for Instance Status(This could take a while): ')
    waiter = ec2client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instances[0].id])
    print('Waiting for Instance Status: OK ')

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
            if instance.public_ip_address is not None:
                print instance.public_ip_address
                print('########################################')
                print('')
                cert = paramiko.RSAKey.from_private_key_file("/Users/sean/.aws/DistributedKey.pem")
                sshcon = paramiko.SSHClient()

                sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                print('..........Establishing SSH Connection to', instance.public_ip_address)

                sshcon.connect( hostname = instance.public_ip_address, username = "ubuntu", pkey = cert,)
                print "connected!!!"

                print 30 * "-" , "Basic Update of OS" , 30 * "-"
                #stdin, stdout, stderr = sshcon.exec_command('sudo apt-get -y update ** sudo apt-get -y upgrade && sudo apt-get install -y build-essential libssl-dev && sudo apt-get install -y libgmp3-dev p7zip-full && sudo apt-get install -y build-essential libssl-dev && sudo apt-get install -y libgmp3-dev p7zip-full && sudo apt-get install -y build-essential libssl-dev && sudo apt-get install -y libgmp3-dev p7zip-full')
               # print stdout.read()
                print 30 * "-" , "Dependencies Install" , 30 * "-"
               # stdin, stdout, stderr = sshcon.exec_command('sudo apt-get install -y yasm libgmp-dev libpcap-dev libnss3-dev libkrb5-dev pkg-config nvidia-cuda-toolkit nvidia-opencl-dev libopenmpi-dev openmpi-bin')
                #print stdout.read()
                print 30 * "-" , "Cloning Latest JtR Git Repo" , 30 * "-"
                #stdin, stdout, stderr = sshcon.exec_command('git clone git://github.com/magnumripper/JohnTheRipper -b bleeding-jumbo john')
                #print stdout.read()
                print 30 * "-" , "Make Install in Progress" , 30 * "-"
               # stdin, stdout, stderr = sshcon.exec_command('cd ~/john/src && sudo ./configure && sudo make -s clean && sudo make -sj4')
                #print stdout.read()
               # stdin, stdout, stderr = sshcon.exec_command('../run/john --test=0')
               # print stdout.read()
                print 30 * "-" , "Copying Private Key for Nodes" , 30 * "-"
                scp = SCPClient(sshcon.get_transport())
                scp.put("/Users/sean/.aws/InternalAssetsDistributedKey.pem")
                stdin, stdout, stderr = sshcon.exec_command('chmod 400 InternalAssetsDistributedKey.pem')
                print 30 * "-" , "Copying List of Private IP's" , 30 * "-"
                scp.put("PrivateIps.txt")

                for subnet in vpc.subnets.all():
                    if subnet.id == globalSubnet2val:
                        for instance in subnet.instances.all():
                            print(instance.private_ip_address)
                stdin, stdout, stderr = sshcon.exec_command('sudo reboot')


                sshcon.close()

    print "Package Install Complete, YAY!!!" 


def vpc_cleanup(vpcid):
    """Remove VPC from AWS 
    Set your region/access-key/secret-key from env variables or boto config.
 
    :param vpcid: id of vpc to delete
    """
    if not vpcid:
        return
    print('Removing VPC ({}) from AWS'.format(vpcid))
    ec2 = boto3.resource('ec2')
    ec2client = ec2.meta.client
    vpc = ec2.Vpc(vpcid)

    os.system('cls' if os.name == 'nt' else 'clear') 
    print('#######################################################')
    print('# Hold Onto Your Hat Deletion In Progress........... #')
    print('######################################################')
    # delete any instances
    for subnet in vpc.subnets.all():
        print('Termination In Progress')
        for instance in subnet.instances.all():
            #instance.terminate()
            print('Please Wait')
            instance.wait_until_terminated()
    print('Instances Gone')


    # detach and delete all gateways associated with the vpc
    for gw in vpc.internet_gateways.all():
        vpc.detach_internet_gateway(InternetGatewayId=gw.id)
        gw.delete()
    print("Internet Gateway Gone")

    rtl = vpc.route_tables.all()
    count = sum(1 for _ in rtl)
    while count > 1:

     #delete all route table associations
        for rt in rtl:
            for rta in rt.associations:
                if not rta.main:
                    print("Deleting route table associations")
                    rta.delete()

            for r in rt.routes:
                try:
                    x = r.delete()
                   #  print(x)
                except:
                    pass
            try:
                rt.delete()
            except:
                pass
                 
        rtl = vpc.route_tables.all()
        count = sum(1 for _ in rtl)

    print('Route Tables Gone')

    # delete our endpoints
    for ep in ec2client.describe_vpc_endpoints(Filters=[{
            'Name': 'vpc-id',
            'Values': [ vpcid ]
        }])['VpcEndpoints']:
        ec2client.delete_vpc_endpoints(VpcEndpointIds=[ep['VpcEndpointId']])
    print('Endpoints Gone')

    # delete our security groups
    for sg in vpc.security_groups.all():
        if sg.group_name != 'default':
            sg.delete()
    print('Security Groups Gone')

    # delete any vpc peering connections
    for vpcpeer in ec2client.describe_vpc_peering_connections(Filters=[{
            'Name': 'requester-vpc-info.vpc-id',
            'Values': [ vpcid ]
        }] )['VpcPeeringConnections']:
        ec2.VpcPeeringConnection(vpcpeer['VpcPeeringConnectionId']).delete()
    print('VPC Connections Gone')

    # delete non-default network acls
    for netacl in vpc.network_acls.all():
        if not netacl.is_default:
            netacl.delete()

    # delete network interfaces
    for subnet in vpc.subnets.all():
        for interface in subnet.network_interfaces.all():
            interface.delete()
        subnet.delete()
    print('Network Interfaces Gone')

    # finally, delete the vpc
    ec2client.delete_vpc(VpcId=vpcid)
    print('##############################')
    print('#### My Work Here Is Done ####')
    print('##############################')
 
def main(argv=None):
        menu()
        #vpc_cleanup(argv[1])
 
if __name__ == '__main__':
    main(sys.argv)
