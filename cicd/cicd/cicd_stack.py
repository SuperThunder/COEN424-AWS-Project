from aws_cdk import (
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_secretsmanager as secretsmanager,
    pipelines as pipelines,
    core as cdk
)

import os
import sys

sys.path.append('..')
from backend.backend import backend_stack

# Stage that includes that backend stack
class BackendStageStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = backend_stack.BackendStack(self, 'Project424Backend')


# Deploy the CICD pipeline for the backend
class CicdStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        pipeline_synth_shellstep = pipelines.ShellStep('Synth', input=['cdk synth'])
        pipeline = pipelines.CodePipeline(self, 'pipeline', synth=)

