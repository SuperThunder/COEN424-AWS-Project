import json
import requests
import boto3
import os
from requests_aws4auth import AWS4Auth

# handler for GET with a (lat,lon) coordinate and radius

# Look up the coordinate in Elastic, get the UUIDs, then look those up in Dynamo
# Then return the results back

dynamodb = boto3.resource('dynamodb')
wifiuser_table_name = os.environ['WIFIUSER_TABLE_NAME']
wifiuser_table = dynamodb.Table(wifiuser_table_name)

# Parameters that must be in request
required_params = ['username', 'email']

def lambda_handler(event, context):
    
    # TODO Return either all the users or process other parameters to return only few users
    #      very brief information like the username / userID in the system so we can reach his data,
    #      full and specific user info should be fetched using the proxy path as the user ID should be the first segment
    
    print('Request headers:', event['headers'])
    print('Request params:', event['queryStringParameters'])

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
        print('Error: params is empty')
        return response

    req_params = event['queryStringParameters']

    # Required parameters
    if 'email' not in req_params.keys() and 'username' not in req_params.keys() :
        response['body'] = 'Error: {p} param missing'
        print('Error: params is missing: ')
        return response
    elif 'username' in req_params.keys():
        # DynamoDB Username key
        username = req_params['username']
        dynamo_key = {
            'pk': f'username#{username}'
        }
    elif 'email' in req_params.keys():
        email = req_params['email']
        # DynamoDB Username key
        dynamo_key = {
            'pk': f'email#{email}'
        }
            
    # If we got results, get them from DynamoDB by using the UUID that links Dynamo and OpenSearch values
    dynamo_response = wifiuser_table.get_item(key={dynamo_key})
    response['body'] = json(dynamo_response)
    print(response)

    return response
