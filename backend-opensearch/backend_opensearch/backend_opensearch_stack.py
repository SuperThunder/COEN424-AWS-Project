from aws_cdk import (
    aws_opensearchservice as opensearch,
    aws_apigateway as apigateway,
    aws_secretsmanager as secretsmanager,
    core as cdk
)
# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class BackendOpensearchStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #
        # OPENSEARCH
        #
        # Used to name the OpenSearch domain
        os_domain_name = 'OpenSearchDomain424Project'
        # Used to name the cognito pool
        app_prefix = 'project424'

        # OpenSearch (Elasticsearch) instance for the geodata
        # dev-level cluster (no scaling)
        # t3.small.search + 10GB matches up with the free tier

        # Have to declare the domain arn in advanced since we need to reference it
        opensearch_domain_arn = "arn:aws:es:" + self.region + ":" + self.account + ":domain/" + os_domain_name + "/*"
        opensearch_domain = opensearch.Domain(self, os_domain_name, version=opensearch.EngineVersion.OPENSEARCH_1_0,
                                              capacity=opensearch.CapacityConfig(data_nodes=1,
                                                                                 data_node_instance_type='t3.small.search'),
                                              ebs=opensearch.EbsOptions(volume_size=10),
                                              # logging=opensearch.LoggingOptions(app_log_enabled=False, slow_search_log_enabled=False, slow_index_log_enabled=False),
                                              node_to_node_encryption=True,
                                              encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
                                              enforce_https=True,
                                              # fine_grained_access_control=opensearch.AdvancedSecurityOptions(master_user_arn=opensearch_master_user.user_arn),
                                              use_unsigned_basic_auth=True,
                                              # access_policies=[iam.PolicyStatement(effect=iam.Effect.ALLOW, actions=["es:ESHttp*"], principals=[iam.AnyPrincipal], resources=[opensearch_domain_arn])],
                                              # cognito_dashboards_auth=opensearch.CognitoOptions(identity_pool_id=opensearch_cognito_identitypool.ref,
                                              #                                                  role=opensearch_cognito_service_role, user_pool_id=opensearch_cognito_userpool.user_pool_id),
                                              # fine_grained_access_control=opensearch.AdvancedSecurityOptions(master_user_arn=opensearch_lambda_service_role.role_arn)

                                              )

        opensearch_url = opensearch_domain.domain_endpoint
        opensearch_url_output = cdk.CfnOutput(self, 'output-opensearch-url', value=opensearch_url)


