import json

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_eks as eks

vpc = awsx.ec2.Vpc(
    "lab-vpc",
    cidr_block="10.0.0.0/16",
    number_of_availability_zones=2,
)

cluster = eks.Cluster(
    "lab-cluster",
    vpc_id=vpc.vpc_id,
    public_subnet_ids=vpc.public_subnet_ids,
    private_subnet_ids=vpc.private_subnet_ids,
    skip_default_node_group=True,
)

node_group = eks.NodeGroup(
    "lab-ng",
    cluster=cluster.core,
    instance_type="t3.small",
    desired_capacity=1,
    min_size=1,
    max_size=3,
)

pulumi.export("kubeconfig", cluster.kubeconfig)
pulumi.export("cluster_name", cluster.eks_cluster.name)

# --- Locust load generator (EC2, accessed via SSM — no SSH keys, no open ports) ---

locust_role = aws.iam.Role(
    "locust-ssm-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
)

aws.iam.RolePolicyAttachment(
    "locust-ssm-policy",
    role=locust_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
)

locust_instance_profile = aws.iam.InstanceProfile(
    "locust-instance-profile",
    role=locust_role.name,
)

locust_sg = aws.ec2.SecurityGroup(
    "locust-sg",
    vpc_id=vpc.vpc_id,
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
)

amazon_linux = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[
        {"name": "name", "values": ["al2023-ami-*-x86_64"]},
        {"name": "virtualization-type", "values": ["hvm"]},
    ],
)

locust_user_data = """#!/bin/bash
dnf install -y python3-pip
pip3 install locust
"""

locust_instance = aws.ec2.Instance(
    "locust-box",
    instance_type="t3.small",
    ami=amazon_linux.id,
    subnet_id=vpc.public_subnet_ids[0],
    vpc_security_group_ids=[locust_sg.id],
    iam_instance_profile=locust_instance_profile.name,
    user_data=locust_user_data,
    tags={"Name": "locust-box"},
)

pulumi.export("locust_instance_id", locust_instance.id)
