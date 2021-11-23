from aws_cdk import (
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_secretsmanager as secretsmanager,
    pipelines as pipelines,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipelineactions,
    core as cdk
)

import os
import sys

sys.path.append('..')
from backend import backend_stack

# Stage that includes that backend stack
class BackendStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = backend_stack.BackendStack(self, 'Project424Backend')
        #service = BackendStack(self, 'Project424Backend')



# Deploy the CICD pipeline for the backend
class CicdStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        #pipeline_synth_shellstep = pipelines.ShellStep('Synth', input=['cdk synth'])
        #pipeline = pipelines.CodePipeline(self, 'pipeline', synth=)

        sourceartifact = codepipeline.Artifact()
        cdkoutputartifact = codepipeline.Artifact()

        # Note: CdkPipeline is deprecated
        # The new way to do this would be with CodePipeline
        cdkpipeline = pipelines.CdkPipeline(self, 'CDKPipeline', pipeline_name='Project424BackendCDKPipeline',
                cloud_assembly_artifact=cdkoutputartifact,
                source_action=codepipelineactions.GitHubSourceAction(
                    action_name='GitHub',
                    output=sourceartifact,
                    oauth_token=cdk.SecretValue.secrets_manager('GITHUB_TOKEN'),
                    owner='SuperThunder',
                    repo='COEN424-AWS-Project',
                    branch='backend',
                    trigger=codepipelineactions.GitHubTrigger.POLL
                ),
                synth_action=pipelines.SimpleSynthAction(
                    source_artifact=sourceartifact,
                    cloud_assembly_artifact=cdkoutputartifact,
                    install_command='cd backend; pwd; ls -lh; npm install -g aws-cdk && pip install -r requirements.txt',
                    synth_command='cdk synth'
                )
        )

        backend_stage = BackendStage(self, 'backend')

        backend_pipeline_stage = cdkpipeline.add_application_stage(backend_stage)


# References:
# https://github.com/aws-samples/cdk-pipelines-demo/blob/python/pipelines_webinar/pipeline_stack.py
# https://docs.aws.amazon.com/cdk/api/latest/docs/pipelines-readme.html
# https://binx.io/blog/2020/09/02/implementing-aws-cdk-cicd-with-cdk-pipelines/