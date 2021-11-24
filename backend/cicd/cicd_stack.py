from aws_cdk import (
    aws_iam as iam,
    aws_apigateway as apigateway,
    aws_secretsmanager as secretsmanager,
    pipelines as pipelines,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipelineactions,
    aws_codebuild as codebuild,
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

        service = backend_stack.BackendStack(self, 'Project424Backend', stack_name="backend-Project424Backend")
        #service = BackendStack(self, 'Project424Backend')



# Deploy the CICD pipeline for the backend
class CicdStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        #pipeline_synth_shellstep = pipelines.ShellStep('Synth', input=['cdk synth'])
        #pipeline = pipelines.CodePipeline(self, 'pipeline', synth=)

        sourceartifact = codepipeline.Artifact()
        #cdkoutputartifact = codepipeline.Artifact()

        # source_action = codepipelineactions.GitHubSourceAction(
        #     action_name='GitHub',
        #     output=sourceartifact,
        #     oauth_token=cdk.SecretValue.secrets_manager('GITHUB_TOKEN'),
        #     owner='SuperThunder',
        #     repo='COEN424-AWS-Project',
        #     branch='backend',
        # )
        #
        # source_stage = codepipeline.StageProps(stage_name="Source", actions=[source_action])
        # build_stage = codepipeline.StageProps(stage_name="Build", actions=[codepipelineactions.CodeBuildAction(
        #                     action_name="Build",
        #                     # Configure your project here
        #                     project=codebuild.PipelineProject(self, "BackendPipelineCodebuild"),
        #                     input=sourceartifact)]
        # )

        # github_source = pipelines.CodePipelineSource.git_hub(repo_string="SuperThunder/COEN424-AWS-Project",
        #                                                          branch="backend",
        #                                                          authentication=cdk.SecretValue.secrets_manager('GITHUB_TOKEN')
        #                                                      )

        # A CodeStar connection to github has to be created first
        # https://docs.aws.amazon.com/dtconsole/latest/userguide/connections-create-github.html
        github_source = pipelines.CodePipelineSource.connection(repo_string='SuperThunder/COEN424-AWS-Project', branch='backend',
                                                                connection_arn='arn:aws:codestar-connections:us-east-1:391508643370:connection/2520f736-ef67-479d-bea7-78cbffb6fa16')

        cdkpipeline = pipelines.CodePipeline(self, 'CDKPipeline', pipeline_name='Project424BackendCDKPipeline',
                self_mutation=False,
                synth=pipelines.ShellStep(
                    id="Synth",
                    input=github_source,
                    commands=['cd backend', 'npm install -g aws-cdk', 'pip install -r requirements.txt', 'cdk synth'],
                    primary_output_directory='backend'
                ),
                # Save $1/month by not having artifacts encrypted, however give up cross account deployments
                cross_account_keys=False,


        )

        backend_stage = BackendStage(self, 'backend')

        backend_pipeline_stage = cdkpipeline.add_stage(backend_stage)


# References:
# https://github.com/aws-samples/cdk-pipelines-demo/blob/python/pipelines_webinar/pipeline_stack.py
# https://docs.aws.amazon.com/cdk/api/latest/docs/pipelines-readme.html
# https://binx.io/blog/2020/09/02/implementing-aws-cdk-cicd-with-cdk-pipelines/