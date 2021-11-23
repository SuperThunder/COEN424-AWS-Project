#!/usr/bin/env python3

from aws_cdk import core

from backend.backend_stack import BackendStack
from cicd.cicd_stack import CicdStack


app = core.App()

# The backend
BackendStack(app, "backend")

# The CICD pipeline
CicdStack(app, "CicdStack")

app.synth()
