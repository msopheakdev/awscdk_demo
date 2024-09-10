from aws_cdk import (
    App,
    Stack,
    aws_ec2 as ec2,
    Environment,
    Tags
)

class Ec2InstanceStack(Stack):

    def __init__(self, scope: App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the VPC and Subnet IDs
        vpc_id = "vpc-02e5fc702984b6cbd"
        subnet_id = "subnet-07164b20e01cfc5ea"

        # Import the existing VPC
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)

        # Import the existing Subnet with its availability zone
        subnet = ec2.Subnet.from_subnet_attributes(
            self, 
            "Subnet",
            subnet_id=subnet_id,
            availability_zone="ap-southeast-1a"  # Replace with the correct availability zone
        )

        # Create a Security Group with all inbound and outbound traffic allowed
        security_group = ec2.SecurityGroup(
            self,
            "MySecurityGroup",
            vpc=vpc,
            security_group_name="AllowAllTraffic",
            description="Allow all inbound and outbound traffic",
            allow_all_outbound=True
        )

        # Allow all inbound traffic
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.all_traffic(), "Allow all inbound traffic")
        security_group.add_ingress_rule(ec2.Peer.any_ipv6(), ec2.Port.all_traffic(), "Allow all inbound traffic")

        # Define EC2 instance user data (install nginx and custom content)
        user_data = '''#!/bin/bash
        yum update -y
        amazon-linux-extras install nginx1 -y
        systemctl start nginx
        systemctl enable nginx
        echo "Hello Proseth and AWS Event" > /usr/share/nginx/html/index.html
        '''

        # Create EC2 instance
        ec2_instance = ec2.Instance(
            self, 
            "ProsethEC2Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),  # Amazon Linux 2 image
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=[subnet]),
            key_name="mylinuxkeypair",  # Optional: Replace with your key pair name if needed
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=8,
                        volume_type=ec2.EbsDeviceVolumeType.GP3
                    )
                )
            ],
            user_data=ec2.UserData.custom(user_data),
            security_group=security_group  # Attach the security group to the instance
        )

        # Tag the instance
        Tags.of(ec2_instance).add("Name", "ProsethEC2Instance")

app = App()
Ec2InstanceStack(app, "ProsethEC2Stack", env=Environment(account="025066243530", region="ap-southeast-1"))
app.synth()
