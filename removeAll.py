import sys
import boto3
 
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

    print('#######################################################')
    print('# Hold Onto Your Hat Deletion In Progress........... #')
    print('######################################################')
    # delete any instances
    for subnet in vpc.subnets.all():
        print('Termination In Progress')
        for instance in subnet.instances.all():
            instance.terminate()
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
    vpc_cleanup(argv[1])
 
if __name__ == '__main__':
    main(sys.argv)