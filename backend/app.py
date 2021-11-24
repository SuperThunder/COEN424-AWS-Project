#!/usr/bin/env python3

from aws_cdk import core
import os

from backend.backend_stack import BackendStack
from cicd.cicd_stack import CicdStack


app = core.App()

# The backend
BackendStack(app, "backend",
             env=core.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
                                    stack_name="backend-Project424Backend")

# The CICD pipeline
CicdStack(app, "cicd")

app.synth()
