import json

from aws_cdk import (
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway,
    aws_secretsmanager as secretsmanager,
    core as cdk
)

import os
import sys

from resources import config


class BackendStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # best way to get the basic auth credentials to the lambda function is probably through role to secrets manager:
        # https://aws.amazon.com/blogs/security/how-to-securely-provide-database-credentials-to-lambda-functions-by-using-aws-secrets-manager/
        # but for now we pass it directly
        opensearch_master_user_secret = secretsmanager.Secret.from_secret_complete_arn(self, 'os-master-user-secret',
                                                                                       secret_complete_arn=config.OPENSEARCH_MASTER_USER_SECRET_ARN)
        opensearch_master_user_credentials = opensearch_master_user_secret.secret_value

        # Dynamo table for wifi network submissions
        # On demand (pay per request), ID (UUID of submission) as hash key
        networks_table = dynamodb.Table(self, 'NetworkDynamoDB', billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                                        partition_key=dynamodb.Attribute(name='uuid', type=dynamodb.AttributeType.STRING)
                                        )

        # Dynamo table for wifi Users
        # On demand (pay per request), ID (UUID of submission) as hash key
        user_table = dynamodb.Table(self, 'UsersDynamoDB', billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                                        partition_key=dynamodb.Attribute(name='pk', type=dynamodb.AttributeType.STRING)
                                        )


        # Layer including requests library for lambda
        wifinetwork_lambda_layer = lambda_.LayerVersion(self, "protobuf-layer",
                                                        compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
                                                        code=lambda_.Code.from_asset(os.path.join('resources',
                                                                                                  'wifinetwork-layer-python.zip')))

        # Reference the Cognito user pool used to authorize logged in users
        #auth_networks = apigateway.CognitoUserPoolsAuthorizer(self, "networksAPIAuthorizer",
        #                                                      cognito_user_pools=[cognito.UserPool.from_user_pool_arn(self, id=config.USER_POOL_ID, user_pool_arn=config.USER_POOL_ARN)])

        # API Gateway for the backend
        api = apigateway.RestApi(self, 'network-search-api-424-project', rest_api_name='424 Project Network Search',
                                 description='Search / Submit WiFi Networks',
                                 default_cors_preflight_options=apigateway.CorsOptions(allow_origins=apigateway.Cors.ALL_ORIGINS, ),
        #                         default_method_options=apigateway.MethodOptions(authorization_type=apigateway.AuthorizationType.COGNITO,
        #                                                                         authorizer=auth_networks)
                                 )
        api_networks = api.root.add_resource('networks')
        api_networks_proxy = api_networks.add_resource('{marker_id+}')

        api_users = api.root.add_resource('users')
        api_users_proxy = api_users.add_resource('{user_specific_path+}')


        # Wifi Network Search Lambda
        lambda_network_search = lambda_.Function(self, "NetworkSearchLambda",
                                                 code=lambda_.Code.from_asset(
                                                     os.path.join('resources', 'networksearch')),
                                                 handler="handler.lambda_handler",
                                                 timeout=cdk.Duration.seconds(45),
                                                 runtime=lambda_.Runtime.PYTHON_3_9,
                                                 environment={'GEO_RADIUS_LIMIT_METRE': config.GEO_RADIUS_LIMIT_METRE,
                                                              'OPENSEARCH_URL': config.OPENSEARCH_URL,
                                                              'OPENSEARCH_WIFI_NETWORK_INDEX': config.OPENSEARCH_WIFI_NETWORK_INDEX,
                                                              'OPENSEARCH_GET_WIFI_NETWORK_LIMIT': config.OPENSEARCH_GET_WIFI_NETWORK_LIMIT,
                                                              'OPENSEARCH_USER_SECRET': opensearch_master_user_credentials.to_string(),
                                                              'WIFINETWORK_TABLE_NAME': networks_table.table_name
                                                              },
                                                 layers=[wifinetwork_lambda_layer]
                                                 )

        # Wifi Users Search Lambda
        lambda_user_search = lambda_.Function(self, "UserSearchLambda",
                                                 code=lambda_.Code.from_asset(
                                                     os.path.join('resources', 'userssearch')),
                                                 handler="handler.lambda_handler",
                                                 timeout=cdk.Duration.seconds(45),
                                                 runtime=lambda_.Runtime.PYTHON_3_9,
                                                 environment={
                                                    'WIFIUSER_TABLE_NAME': user_table.table_name
                                                              }
                                                 )

        
        # Users fetching lambda (not sure if needed, should probably retrieve very brief information about a specified amount of users)
        # TODO need to change ENV variables to allow user search
        lambda_user_submit = lambda_.Function(self, "UserSubmitLambda",
                                                 code=lambda_.Code.from_asset(
                                                     os.path.join('resources', 'usersubmit')),
                                                 handler="handler.lambda_handler",
                                                 timeout=cdk.Duration.seconds(45),
                                                 runtime=lambda_.Runtime.PYTHON_3_9,
                                                 environment={
                                                    'WIFIUSER_TABLE_NAME': user_table.table_name
                                                              }
                                                 )

        # Rest proxy handling lambda (can be split into 2 functions tho doesnt really matters)
        # TODO need to change ENV variables to allow user search and related ops
        lambda_rest_proxy = lambda_.Function(self, "SampleProxyFunction",
                                                 code=lambda_.Code.from_asset(
                                                     os.path.join('resources', 'restproxy')),
                                                 handler="handler.lambda_handler",
                                                 timeout=cdk.Duration.seconds(45),
                                                 runtime=lambda_.Runtime.PYTHON_3_9,
                                                 environment={
                                                    'WIFIUSER_TABLE_NAME': user_table.table_name
                                                              }
                                                 )

        lambda_like_dislike = lambda_.Function(self, "LikeDislike",
                                                 code=lambda_.Code.from_asset(
                                                     os.path.join('resources', 'likedislike')),
                                                 handler="handler.lambda_handler",
                                                 timeout=cdk.Duration.seconds(45),
                                                 runtime=lambda_.Runtime.PYTHON_3_9,
                                                 environment={
                                                    'WIFINETWORK_TABLE_NAME': user_table.table_name
                                                              }
                                                 )
        

        # 'A map of Apache Velocity templates that are applied on the request payload.'
        # ^??????
        network_search_request_template = {"application/json": '{ "statusCode": "200" }'}

        network_search_integration = apigateway.LambdaIntegration(lambda_network_search)
        api_networks.add_method('GET', network_search_integration)

        users_integration = apigateway.LambdaIntegration(lambda_user_search)
        api_users.add_method('GET', users_integration)
        api_users_proxy.add_method('ANY', proxy_integration)  # ANY is created by default when going trough UI, you may or may not care to do the same here.

        proxy_integration = apigateway.LambdaIntegration(lambda_rest_proxy)
        api_networks_proxy.add_method('ANY', proxy_integration)  # ANY is created by default when going trough UI, you may or may not care to do the same here.



        # Wifi Network Submission Lambda
        lambda_network_submit = lambda_.Function(self, "NetworkSubmitLambda",
                                                 code=lambda_.Code.from_asset(
                                                     os.path.join('resources', 'networksubmit')),
                                                 handler="handler.lambda_handler",
                                                 timeout=cdk.Duration.seconds(45),
                                                 runtime=lambda_.Runtime.PYTHON_3_9,
                                                 environment={'GEO_RADIUS_LIMIT_METRE': config.GEO_RADIUS_LIMIT_METRE,
                                                              'OPENSEARCH_URL': config.OPENSEARCH_URL,
                                                              'OPENSEARCH_WIFI_NETWORK_INDEX': config.OPENSEARCH_WIFI_NETWORK_INDEX,
                                                              'OPENSEARCH_USER_SECRET': opensearch_master_user_credentials.to_string(),
                                                              'WIFINETWORK_TABLE_NAME': networks_table.table_name
                                                              },
                                                 layers=[wifinetwork_lambda_layer]
                                                 )

        # 'A map of Apache Velocity templates that are applied on the request payload.'
        # ^??????
        network_submit_request_template = {"application/json": '{ "statusCode": "200" }'}

        network_submit_integration = apigateway.LambdaIntegration(lambda_network_submit)

        api_networks.add_method('POST', network_submit_integration)
        
        
        user_submit_integration = apigateway.LambdaIntegration(lambda_network_submit)

        api_users.add_method('POST', user_submit_integration)


        # Grant DynamoDB read permission to the GET lambda, read-write to the POST lambda
        networks_table.grant_read_data(lambda_network_search)
        networks_table.grant_read_write_data(lambda_rest_proxy) # To update the item (tho may not have a related UI component at all.)
        
        networks_table.grant_read_write_data(lambda_network_submit)

        # Grant OpenSearch read permission to the GET lambda, read-write to the POST lambda
        # Note: this may note actually be doing anything, as OpenSearch is in basic auth mode
        #opensearch_domain.grant_read_write(lambda_network_submit)
        #opensearch_domain.grant_read(lambda_network_search)

        # Grant DynamoDB read permission to the GET lambda, read-write to the POST lambda
        user_table.grant_read_data(lambda_user_search)
        user_table.grant_read_write_data(lambda_rest_proxy) # To update the item (tho may not have a related UI component at all.)
        user_table.grant_read_write_data(lambda_user_submit) 
        user_table.grant_read_write_data(lambda_like_dislike)

        # opensearch related docs:
        # setting permissions in CDK: https://docs.aws.amazon.com/cdk/api/latest/docs/aws-opensearchservice-readme.html#permissions
        # getting started: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/gsgcreate-domain.html
        # fine grained access tutorial: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html
        #
        # opensearch notes/ideas:
        # would probably work if we have a master user (for manually poking around) and IAM permissions (to give to the lambdas)
