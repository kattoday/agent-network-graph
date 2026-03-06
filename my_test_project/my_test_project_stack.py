from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_neptune_alpha as neptune
)
from constructs import Construct

class MyTestProjectStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC remains the same
        vpc = ec2.Vpc(self, "AgentNetworkVpc", max_azs=2)

        # FIX: Define the cluster with the configuration included
        self.cluster = neptune.DatabaseCluster(self, "AgentGraphCluster",
            vpc=vpc,
            instance_type=neptune.InstanceType.SERVERLESS,
            # This next line is what the error was asking for:
            serverless_scaling_configuration=neptune.ServerlessScalingConfiguration(
                min_capacity=1.0, # Minimum Neptune Capacity Units (NCUs)
                max_capacity=2.5
            ),
            iam_authentication=True
        )

        self.cluster.connections.allow_default_port_from_any_ipv4("InternalAccess")


from aws_cdk import aws_lambda as _lambda

# ... (inside your Stack class)

# 4. The Lambda "Bridge"
ingestor_lambda = _lambda.Function(self, "GraphIngestor",
    runtime=_lambda.Runtime.PYTHON_3_12,
    handler="ingestor.handler", # Look in ingestor.py for a function called 'handler'
    code=_lambda.Code.from_asset("lambda"), # Upload the whole 'lambda' folder
    vpc=vpc, # Put the Lambda INSIDE your VPC
    environment={
        "NEPTUNE_ENDPOINT": self.cluster.cluster_endpoint.hostname
    }
)

# 5. Give the Lambda permission to talk to the Database
self.cluster.grant_connect(ingestor_lambda)

