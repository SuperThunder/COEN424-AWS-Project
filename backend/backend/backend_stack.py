from aws_cdk import (
    aws_lambda as lambda_,
    aws_s3 as s3,
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
        # TODO COGNITO AUTH FROM THE FRONT END
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


        # OpenSearch (Elasticsearch) instance for the geodata
        # this is apparently just a dev-level cluster (no scaling)
        # hopefully t3.small.search + 10GB matches up with the free tier
        opensearch_domain = opensearch.Domain(self, 'OpenSearchDomain', version=opensearch.EngineVersion.OPENSEARCH_1_0,
                                              capacity=opensearch.CapacityConfig(data_nodes=1, data_node_instance_type='t3.small.search'),
                                              ebs=opensearch.EbsOptions(volume_size=10))
        # Grant read permission to the GET lambda, read-write to the POST lambda
        # todo: may need to specify a particular path in the domain
        opensearch_domain.grant_read_write(lambda_network_submit)
        opensearch_domain.grant_read(lambda_network_search)





