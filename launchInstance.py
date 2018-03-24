import boto3
Import sys



####### LAUNCH INSTANCE #######
ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
    ImageId='ami-3bfab942',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro')
print instance[0].id
############################


####### KILL INSTANCE USING FILE INPUT #######
ec2 = boto3.resource('ec2')
for instance_id in sys.argv[1:]:
    instance = ec2.Instance(i-00caec6ad08505c07)
    response = instance.terminate()
    print response
 ############################


####### KILL INSTANCE HARDCODED IN FILE #######
ec2 = boto3.resource('ec2')
instance = ec2.Instance('i-00caec6ad08505c07')
response = instance.terminate()
############################
