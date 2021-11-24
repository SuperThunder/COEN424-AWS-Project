import json
import os
import requests
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
wifiuser_table_name = os.environ['WIFIUSER_TABLE_NAME']
wifiuser_table = dynamodb.Table(wifiuser_table_name)

dynamodb = boto3.resource('dynamodb')
wifinetwork_table_name = os.environ['WIFINETWORK_TABLE_NAME']
wifinetwork_table = dynamodb.Table(wifinetwork_table_name)

def lambda_handler(event, context):
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

    if(event['path'] is None):
        response['body'] = 'Error: params empty'
        print('Error: params is empty')
        return response
    
    if 'users' in event['path']:
        req_type = event['path'].replace('/users/','').split('/')
        if len(req_type) <2:
            userid = req_type[0]
        elif len(req_type) <4:
            netid = req_type[2]
    if 'networks' in event['path']:
        req_type = event['path'].replace('/networks/','').split('/')
        if len(req_type) <2:
            netid = req_type[0]
    
    method = event['httpMethod']
    if method == 'GET':
        # 1) GET /users/{user_id+}/markers                              -> full list of user's markers   
        
        if 'markers' in req_type and 'users' in event['path']:
            # Required parameters
            if '@' in userid:
                email = userid
                # DynamoDB Username key
                dynamo_key = {
                    'pk': f'email#{email}'
                }                
                # If we got results, get them from DynamoDB by using the UUID that links Dynamo and OpenSearch values
                dynamo_response = wifiuser_table.query(
                projectionExpression = "markers",
                KeyConditionExpression=Key(f'email#{email}').eq(email)
                )
            elif '@' not in userid:
                # DynamoDB Username key
                username = userid
                dynamo_key = {
                    'pk': f'username#{username}'
                }
                # If we got results, get them from DynamoDB by using the UUID that links Dynamo and OpenSearch values
                dynamo_response = wifiuser_table.query(
                projectionExpression = "markers",
                KeyConditionExpression=Key(f'username#{username}').eq(username)
                )
            else: 
                print('Error: params are missing: ')
            
            response['body'] = json(dynamo_response)
            print(response)

            return response
        
        # 3) GET /users/{user_id+}                                   -> full info of specific user, except favorites and markers
        elif 'users' in event['path']:
            # Required parameters
            if '@' in userid:
                email = userid
                # DynamoDB Username key
                dynamo_key = {
                    'pk': f'email#{email}'
                }                
            elif '@' not in userid:
                # DynamoDB Username key
                username = userid
                dynamo_key = {
                    'pk': f'username#{username}'
                }
            else: 
                print('Error: params are missing: ')
                
            # If we got results, get them from DynamoDB by using the UUID that links Dynamo and OpenSearch values
            dynamo_response = wifiuser_table.get_item(key={dynamo_key})
            response['body'] = json(dynamo_response)
            print(response)

            return response
            
        # 6) GET  /networks/{marker_id+}                        -> GET full info of a specific marker
        
    # UPDATE (PUT) /networks/{marker_id+}            -> UPDATE the data of the speicific marker
    elif method == 'PUT' and 'networks' in event['path']:
        # If we got results, get them from DynamoDB by using the UUID that links Dynamo and OpenSearch values
        # dynamo_response = wifinetwork_table.update_item(
        #     Key={
        #         'uuid':netid
        #         },
        #     UpdateExpression=f"set ",

        #     ExpressionAttributeValues={
                
        #     },
        #     ReturnValues="UPDATED_NEW"
        # )
        # response['body'] = json(dynamo_response)
        # print(response)

        print('whoops')
        response['body'] = 'whoops'
        return response
    
    # 5) GET and DELETE /users/{user_id+}/markers/marker_id         -> GET full info of the specific marker / DELETE the specific marker from the system entirely
    elif method == 'DELETE' and 'users' in event['path']:
        try:
            if '@' in userid:
                email = userid
                # DynamoDB Username key
                dynamo_key = {
                    'pk': f'email#{email}'
                }                
            elif '@' not in userid:
                # DynamoDB Username key
                username = userid
                dynamo_key = {
                    'pk': f'username#{username}'
                }
            else: 
                print('Error: params are missing: ')
            # response template
            dynamo_response = wifinetwork_table.delete_item(key={dynamo_key})
            response['body'] = json(dynamo_response)
            print(response)
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
        return response
    elif method == 'DELETE' and 'networks' in event['path']:
        try:
            # response template
            dynamo_response = wifinetwork_table.delete_item(
                Key={
                    'uuid':netid
                    }
            )
            response['body'] = json(dynamo_response)
            print(response)
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
        return response
    else:
        print('Request type not supported')

    return {
        'statusCode': 200,
        'body': json.dumps('Request Method:'+event['httpMethod']+',  Request Path: '+event['path'])
    }
