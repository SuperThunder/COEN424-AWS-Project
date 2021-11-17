import json
import os
import requests
import boto3
import uuid
from decimal import Decimal

# handler for a POST to submit a wifi network given:
#   Network name (SSID)
#   User ID of poster
#   Password of network (plaintext)
#   Security type (None, WEP, WPA, WPA2, WPA3)
#   lat, lon of network

# We will generate a UUID to uniquely identify the network submission

dynamodb = boto3.resource('dynamodb')
wifinetwork_table_name = os.environ['WIFINETWORK_TABLE_NAME']
wifinetwork_table = dynamodb.Table(wifinetwork_table_name)

opensearch_url = os.environ['OPENSEARCH_URL']
opensearch_http_secret = json.loads(os.environ['OPENSEARCH_USER_SECRET'])
opensearch_http_auth = (opensearch_http_secret['username'], opensearch_http_secret['password'])

host = 'https://' + opensearch_url + '/'
index_url = host + os.environ['OPENSEARCH_WIFI_NETWORK_INDEX'] + '/'
doc_url = index_url + '_doc'

required_body_keys = ['ssid', 'password', 'submitter', 'security_type', 'lat', 'lon']
allowed_wireless_security_types = ['Open', 'WEP', 'WPA', 'WPA2', 'WPA3']


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

    # OpenSearch request template
    opensearch_request = {
        "uuid": '',
        "location": {
            "lat": -0.0,
            "lon": -0.0
        }
    }

    # Dynamodb submission template
    dynamo_submission = {'ssid': '', 'password': '', 'sectype': '', 'submitter': '', 'uuid': '', 'lat': '', 'lon': ''}

    # Get the required parameters from the request json body
    try:
        req_body = json.loads(event['body'])
    except:
        response['body']['Cause'] = 'Invalid request body'
        response['body'] = json.dumps(response['body'])
        return response

    # Required parameters
    for k in required_body_keys:
        if k not in req_body.keys():
            response['body']['Cause'] = 'Error: {p} key missing'.format(p=k)
            response['body'] = json.dumps(response['body'])
            return response

    wifi_ssid = req_body['ssid']
    wifi_password = req_body['password']
    wifi_sectype = req_body['security_type']
    submitting_user = req_body['submitter']
    lat = req_body['lat']
    lon = req_body['lon']

    if (wifi_sectype not in allowed_wireless_security_types):
        response['body']['Error'] = True
        response['body']['Cause'] = 'Wifi security type {type} not in {lt}'.format(type=wifi_sectype, lt=str(
            allowed_wireless_security_types))
        response['statusCode'] = 400
        response['body'] = json.dumps(response['body'])
        return response

    # generate a UUID for the network submission
    submission_uuid = str(uuid.uuid4())

    # STORE ALL SUBMISSION VALUES IN DYNAMO, INDEXED BY UUID
    dynamo_submission['uuid'] = submission_uuid
    dynamo_submission['ssid'] = wifi_ssid
    dynamo_submission['password'] = wifi_password
    dynamo_submission['submitter'] = submitting_user
    dynamo_submission['sectype'] = wifi_sectype
    dynamo_submission['lat'] = Decimal(str(lat))  # Dynamo does not accept floats
    dynamo_submission['lon'] = Decimal(str(lon))
    ddres = wifinetwork_table.put_item(Item=dynamo_submission)
    print('DynamoDB result: ', ddres)

    # STORE THE LAT/LON AND UUID IN OPENSEARCH
    opensearch_headers = {"Content-Type": "application/json"}

    opensearch_request['uuid'] = submission_uuid
    opensearch_request['location']['lat'] = lat
    opensearch_request['location']['lon'] = lon

    # req = requests.get(search_url, auth=awsauth, headers=headers, data=json.dumps(query))
    opensearch_submit_req = requests.post(doc_url, auth=opensearch_http_auth, headers=opensearch_headers,
                                          data=json.dumps(opensearch_request))

    print('Elasticsearch response for uuid {u}:'.format(u=uuid), opensearch_submit_req.content)

    response['statusCode'] = 200
    response['body']['Error'] = False
    response['body']['uuid'] = submission_uuid
    response['body'] = json.dumps(response['body'])
    return response
