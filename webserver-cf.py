from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2

template = Template()

#Security Group
sec_grp = ec2.SecurityGroup("LampSg")
sec_grp.GroupDescription = "LAMP SecurityGroup with Permission for Port 80 & 22"
sec_grp.SecurityGroupIngress = [
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp = "0.0.0.0/0"),
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "80", ToPort = "80", CidrIp = "0.0.0.0/0")
]
template.add_resource(sec_grp)

#SSH Key Pair
key_pair = template.add_parameter(Parameter(
		"KeyName",
		Description = "SSH Key Pair that is used to access the instance",
		Type = "String"
	))

#AMI ID & Instance Type
instance = ec2.Instance("WebServer")
instance.ImageId = "ami-0998bf58313ab53da"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sec_grp)]
instance.KeyName = Ref(key_pair)
#Commands to be executed in the Instance after creation
user_data = Base64(Join('\n',
	[
		"#!/bin/bash",
		"sudo yum -y install httpd",
		"sudo echo '<html><head><title>Welcome</title></head><body><h1>Welcome to EC2 WebServer Test Page</h1><body></html>' > /var/www/html/test.html",
		"sudo service httpd start",
		"sudo chkconfig httpd on"
	]
	))
instance.UserData = user_data
template.add_resource(instance)

template.add_output(Output(
	"InstanceAccess",
	Description = "Get the Command to access the instance using SSH",
	Value = Join("", ["ssh -i ShiviKey.pem ec2-user@", GetAtt(instance, "PublicIp")])
	))

template.add_output(Output(
	"WebUrl",
	Description = "Get the Web URL of the instance",
	Value = Join("", ["http://", GetAtt(instance, "PublicDnsName")])
	))

#Check: 
print(template.to_json())