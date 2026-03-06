from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_neptune_alpha as neptune
)
from constructs import Construct

class MyTestProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create a VPC (Neptune requires a private network)
        vpc = ec2.Vpc(self, "AgentGraphVpc", max_azs=2)

        # 2. Create the Neptune Database Cluster
        cluster = neptune.DatabaseCluster(self, "AgentGraphCluster",
            vpc=vpc,
            instance_type=neptune.InstanceType.T3_MEDIUM,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        )

        # Allow connections to Neptune on port 8182
        cluster.connections.allow_default_port_from_any_ipv4("Open to VPC")

        # 3. Create the Lambda Ingestor (The Bridge)
        ingestor_lambda = _lambda.Function(
            self, 
            "GraphIngestor",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="ingestor.handler",
            code=_lambda.Code.from_asset("lambda"),
            vpc=vpc, # Put the Lambda in the same network as Neptune
            environment={
                "NEPTUNE_ENDPOINT": cluster.cluster_endpoint.socket_address
            }
        )

        # 4. Give the Lambda permission to talk to Neptune
        cluster.grant_connect(ingestor_lambda)

