import json
import requests
import boto3
import os
from requests_aws4auth import AWS4Auth

# handler for GET with a (lat,lon) coordinate and radius

# Look up the coordinate in Elastic, get the UUIDs, then look those up in Dynamo
# Then return the results back

dynamodb = boto3.resource('dynamodb')
wifinetwork_table_name = os.environ['WIFINETWORK_TABLE_NAME']
wifinetwork_table = dynamodb.Table(wifinetwork_table_name)

# https://docs.aws.amazon.com/opensearch-service/latest/developerguide/search-example.html
opensearch_url = os.environ['OPENSEARCH_URL']
opensearch_http_secret = json.loads(os.environ['OPENSEARCH_USER_SECRET'])
opensearch_http_auth = (opensearch_http_secret['username'], opensearch_http_secret['password'])

host = 'https://' + opensearch_url + '/'
index_url = host + os.environ['OPENSEARCH_WIFI_NETWORK_INDEX'] + '/'
search_url = index_url + '_search'


# Parameters that must be in request
required_params = ['uuid','like','dislike']

def lambda_handler(event, context):
    print('Request headers:', event['headers'])
    print('Request params:', event['queryStringParameters'])
    print('Search URL: ', search_url)

    # response template
    response = {
        'statusCode': 400,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': '',
        'isBase64Encoded': False
    }

    if(event['queryStringParameters'] is None):
        response['body'] = 'Error: params missing'.format(p=required_params)
        print('Error: params missing')
        return response

    req_params = event['queryStringParameters']

    # Required parameters
    for param in required_params:
        if param not in req_params.keys():
            response['body'] = 'Error: {p} param missing'.format(p=param)
            return response

    dynamo_key = req_params['uuid']
    if req_params['like'] == 'true':
        ddres = wifinetwork_table.update_item(
            Key=dynamo_key,
            UpdateExpression="SET upvote = upvote + :inc",

            ExpressionAttributeValues={
                ':inc': 1
            },
            ReturnValues="UPDATED_NEW"
        )
    elif req_params['dislike'] == 'true':
        ddres = wifinetwork_table.update_item(
            Key=dynamo_key,
            UpdateExpression="SET downvote = downvote + :inc",

            ExpressionAttributeValues={
                ':inc': -1
            },
            ReturnValues="UPDATED_NEW"
        )

    return response
