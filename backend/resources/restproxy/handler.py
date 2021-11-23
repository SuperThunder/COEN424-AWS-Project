import json
import os
import requests
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
wifiuser_table_name = os.environ['WIFIUSER_TABLE_NAME']
wifiuser_table = dynamodb.Table(wifiuser_table_name)

required_body_keys = ['username', 'password', 'dateJoined', 'email', 'numWifiAdded']

def lambda_handler(event, context):
    
    # TODO Handle the request based on the httpMethod and the path parameters of the event.
    
    # TODO Methods to handle:
    # 1) GET /users/{user_id+}                                      -> full info of specific user, except favorites and markers
    if GET /users/{user_id+}:
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

    # 3) GET /users/{user_id+}/markers                              -> full list of user's markers
    # 5) GET and DELETE /users/{user_id+}/markers/marker_id         -> GET full info of the specific marker / DELETE the specific marker from the system entirely
    # 6) GET and UPDATE (or POST) /networks/{marker_id+}            -> GET full info of a specific marker / UPDATE the data of the speicific marker

    return {
        'statusCode': 200,
        'body': json.dumps('Request Method:'+event['httpMethod']+',  Request Path: '+event['path'])
    }
