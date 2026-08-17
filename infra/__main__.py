import pulumi
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
