import json
import os
import requests
import boto3
import uuid
from decimal import Decimal

# handler for a POST to submit a user given:
#   Network name (uuID)
#   User ID of poster
#   Password of network (plaintext)
#   Security type (None, WEP, WPA, WPA2, WPA3)
#   lat, lon of network

# We will generate a UUID to uniquely identify the network submission

dynamodb = boto3.resource('dynamodb')
wifiuser_table_name = os.environ['WIFIUSER_TABLE_NAME']
wifiuser_table = dynamodb.Table(wifiuser_table_name)

required_body_keys = ['username', 'password', 'dateJoined', 'email', 'numWifiAdded']

def lambda_handler(event, context):
    print('Request body', event['body'])

    # Response template
    response = {
        'statusCode': 400,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': {'Error': True},
        'isBase64Encoded': False
    }

    # Dynamodb submission template
    dynamo_submission = {'uuid': '', 'username': '','password': '', 'dateJoined': '', 'email': '', 'numWifiAdded': '',}

    # Get the required parameters from the request json body
    try:
        req_body = json.loads(event['body'])
    except:
        response['body']['Cause'] = 'Invalid request body'
        return response

    # Required parameters
    for k in required_body_keys:
        if k not in req_body.keys():
            response['body']['Cause'] = 'Error: {p} key missing'.format(p=k)
            return response

    user_name = req_body['username']
    user_password = req_body['password']
    user_datejoined = req_body['dateJoined']
    user_email = req_body['email']
    user_numWifiAdd = req_body['numWifiAdded']
    

    # generate a UUID for the network submission
    submission_uuid = str(uuid.uuid4())

    # STORE ALL SUBMISSION VALUES IN DYNAMO, INDEXED BY UUID
    dynamo_submission['uuid'] = submission_uuid
    dynamo_submission['username'] = user_name
    dynamo_submission['password'] = user_password
    dynamo_submission['dateJoined'] = user_datejoined
    dynamo_submission['email'] = user_email
    dynamo_submission['numWifiAdded'] = user_numWifiAdd
    
    ddres = wifiuser_table.put_item(Item=dynamo_submission)
    print('DynamoDB result: ', ddres)

    response['statusCode'] = 200
    response['body']['Error'] = False
    response['body']['uuid'] = submission_uuid
    response['body'] = json.dumps(response['body'])
    return response
