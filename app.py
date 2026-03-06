#!/usr/bin/env python3
import os

import aws_cdk as cdk
from my_test_project.my_test_project_stack import MyTestProjectStack

app = cdk.App()
MyTestProjectStack(app, "MyTestProjectStack", 
                       env=cdk.Environment(account="992878410915", region="us-east-1")
                   )

app.synth()

