import aws_cdk as core
import aws_cdk.assertions as assertions

from my_test_project.my_test_project_stack import MyTestProjectStack

# example tests. To run these tests, uncomment this file along with the example
# resource in my_test_project/my_test_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MyTestProjectStack(app, "my-test-project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
