from aws_cdk import (
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_opensearchservice as opensearch,
    aws_apigateway as apigateway,
    core as cdk
)

import os


class BackendStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # API Gateway for the backend
        # TODO COGNITO AUTH FROM THE FRONT END FOR GATEWAYS
        api = apigateway.RestApi(self, 'network-search-api-424-project', rest_api_name='424 Project Network Search',
                                        description='Search for WiFi Networks',
                                        )
        api_networks = api.root.add_resource('networks')

        # Wifi Network Search Lambda
        lambda_network_search = lambda_.Function(self, "NetworkSearchLambda",
                                                 code=lambda_.Code.from_asset(os.path.join('resources', 'networksearch')),
                                                 handler="handler.lambda_handler",
                                                 timeout=cdk.Duration.seconds(45),
                                                 runtime=lambda_.Runtime.PYTHON_3_9,
                                                 environment={}
                                 )

        # 'A map of Apache Velocity templates that are applied on the request payload.'
        # ^??????
        network_search_request_template = {"application/json": '{ "statusCode": "200" }'}

        network_search_integration = apigateway.LambdaIntegration(lambda_network_search, request_templates=network_search_request_template)
        api_networks.add_method('GET', network_search_integration)


        # Wifi Network Submission Lambda
        lambda_network_submit = lambda_.Function(self, "NetworkSubmitLambda",
                                                 code=lambda_.Code.from_asset(os.path.join('resources', 'networksubmit')),
                                                 handler="handler.lambda_handler",
                                                 timeout=cdk.Duration.seconds(45),
                                                 runtime=lambda_.Runtime.PYTHON_3_9,
                                                 environment={}
                                 )



        # 'A map of Apache Velocity templates that are applied on the request payload.'
        # ^??????
        network_submit_request_template = {"application/json": '{ "statusCode": "200" }'}

        network_submit_integration = apigateway.LambdaIntegration(lambda_network_submit, request_templates=network_submit_request_template)

        api_networks.add_method('POST', network_submit_integration)


        # Dynamo table for wifi network submissions
        # On demand (pay per request), ID (UUID of submission) as hash key
        networks_table = dynamodb.Table(self, 'NetworkDynamoDB', billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                                        partition_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING)
                                        )
        # Grant read permission to the GET lambda, read-write to the POST lambda
        networks_table.grant_read_data(lambda_network_search)
        networks_table.grant_read_write_data(lambda_network_submit)


        #
        # OPENSEARCH
        #
        # Used to name the OpenSearch domain
        os_domain_name = 'OpenSearchDomain424Project'
        # Used to name the cognito pool
        app_prefix = 'Project424'


        # Master user for opensearch
        opensearch_master_user = iam.User(self, 'opensearch-master-user', user_name='opensearch-master')

        # Cognito user and identity pool
        opensearch_cognito_userpool = cognito.UserPool(self, app_prefix+'userpool', user_pool_name='opensearch-userpool',
                                                       sign_in_aliases=cognito.SignInAliases(username=True, email=True),
                                                        user_invitation=cognito.UserInvitationConfig(email_subject='424 PROJECT OPENSEARCH COGNITO ACCOUNT',
                                                                                                     email_body='User: {username}. Temp pw: {####}'),
                                                       auto_verify=cognito.AutoVerifiedAttrs(email=True)
                                                       )
        opensearch_cognito_userpool.add_domain('424project-cognito-domain', cognito_domain=cognito.CognitoDomainOptions(domain_prefix=app_prefix))

        opensearch_cognito_identitypool = cognito.CfnIdentityPool(allow_unauthenticated_identities=False, cognito_identity_providers=[])

        opensearch_cognito_admin_principal_conditions = {
                "StringEquals": {"cognito-identity.amazonaws.com:aud": opensearch_cognito_identitypool.ref},
                "ForAnyValue:StringLike": {
                    "cognito-identity.amazonaws.com:amr": "authenticated"
                }
            }

        # Assign the role to a logged in user or not using the 2 conditions
        # https://www.luminis.eu/blog/cloud-en/deploying-a-secure-aws-elasticsearch-cluster-using-cdk/
        opensearch_cognito_admin_role = iam.Role(self, 'cognito_admin_role',
                                                    assumed_by=iam.FederatedPrincipal('cognito-identity.amazonaws.com',
                                                    conditions=opensearch_cognito_admin_principal_conditions,
                                                    assume_role_action="sts:AssumeRoleWithWebIdentity"
                                                    ),
                                                 )

        # Admin role: Full permissions within OS cluster
        opensearch_cognito_service_role = iam.Role(self, 'cognito_service_role', iam.RoleProps(
            assumed_by=iam.ServicePrincipal('424-project-cognito-serviceprincipal',),
                                            managed_policies=[iam.ManagedPolicy.from_managed_policy_name('AmazonESCognitoAccess')])
                                                   )

        # Service role: used to configure Cognito within the Opensearch cluster
        opensearch_lambda_service_role = iam.Role(self, 'cognito_service_role', iam.RoleProps(
            assumed_by=iam.ServicePrincipal('424-project-cognito-serviceprincipal',),
                                            managed_policies=[iam.ManagedPolicy.from_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')])
                                                   )

        # Used by lambda that handles opensearch requests to configure open distro (monitoring) and execute other opensearch requests.
        # Can also be used to insert index templates / data
        cognito_admin_group = cognito.CfnUserPoolGroup(self, 'userpool_admingroup_pool', user_pool_id=opensearch_cognito_userpool.user_pool_id,
                                                       group_name='opensearch_admins',
                                                       role_arn=opensearch_cognito_admin_role.role_arn)

        # OpenSearch (Elasticsearch) instance for the geodata
        # this is apparently just a dev-level cluster (no scaling)
        # hopefully t3.small.search + 10GB matches up with the free tier

        # Identity resources used here:
        # Identity and user pools are referenced to configure the Kibana<->Cognito connection
        # Use the service role that is allowed to configure Opensearch for Cognito
        # Lambda service role to configure fine grained access in opensearch

        # Have to declare the domain arn in advanced since we need to reference it
        opensearch_domain_arn = "arn:aws:es:" + self.region + ":" + self.account + ":domain/" + os_domain_name + "/*"
        opensearch_domain = opensearch.Domain(self, os_domain_name, version=opensearch.EngineVersion.OPENSEARCH_1_0,
                                              capacity=opensearch.CapacityConfig(data_nodes=1, data_node_instance_type='t3.small.search'),
                                              ebs=opensearch.EbsOptions(volume_size=10),
                                              #logging=opensearch.LoggingOptions(app_log_enabled=False, slow_search_log_enabled=False, slow_index_log_enabled=False),
                                              node_to_node_encryption=True,
                                              encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
                                              enforce_https=True,
                                              access_policies=[iam.PolicyStatement(effect=iam.Effect.ALLOW, actions=["es:ESHttp*"], principals=[iam.AnyPrincipal], resources=[opensearch_domain_arn])],
                                              cognito_dashboards_auth=opensearch.CognitoOptions(identity_pool_id=opensearch_cognito_identitypool.ref,
                                                                                                role=opensearch_cognito_service_role, user_pool_id=opensearch_cognito_userpool.user_pool_id),
                                              #fine_grained_access_control=opensearch.AdvancedSecurityOptions(master_user_arn=opensearch_lambda_service_role.role_arn)
                                              fine_grained_access_control=opensearch.AdvancedSecurityOptions(master_user_arn=opensearch_master_user.user_arn),
                                            )
        # Grant read permission to the GET lambda, read-write to the POST lambda
        # todo: may need to specify a particular path in the domain
        opensearch_domain.grant_read_write(lambda_network_submit)
        opensearch_domain.grant_read(lambda_network_search)

        opensearch_distro_config = opensearch

        # opensearch related docs:
        # setting permissions in CDK: https://docs.aws.amazon.com/cdk/api/latest/docs/aws-opensearchservice-readme.html#permissions
        # getting started: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/gsgcreate-domain.html
        # fine grained access tutorial: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html
        #
        # opensearch notes/ideas:
        # would probably work if we have a master user (for manually poking around) and IAM permissions (to give to the lambdas)





