import json
import os
import requests
import uuid

# handler for a POST to submit a wifi network given:
#   Network name (SSID)
#   User ID of poster
#   Password of network (plaintext)
#   Security type (None, WEP, WPA, WPA2, WPA3)
#   lat, lon of network

# We will generate a UUID to uniquely identify the network submission

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

    # Get the required parameters from the request json body
    try:
        req_body = json.loads(event['body'])
    except:
        response['body']['Cause'] = 'Invalid request body'
        return response

    # Required parameters
    for k in required_body_keys:
        if k not in required_body_keys.keys():
            response['body'] = 'Error: {p} key missing'.format(p=k)
            response['statusCode'] = 400
            return response

    wifi_ssid = req_body['ssid']
    wifi_password = req_body['password']
    wifi_sectype = req_body['security_type']
    submitting_user = req_body['submitter']
    lat = req_body['lat']
    lon = req_body['lon']

    # TODO: check that user exists, sectype is in allowed list

    if(wifi_sectype not in allowed_wireless_security_types):
        response['body']['Error'] = True
        response['body']['Cause'] = 'Wifi security type {t} not in {l}'.format(t=wifi_sectype,l=str(allowed_wireless_security_types))
        response['statusCode'] = 400

    # generate a UUID for the network submission
    submission_uuid = str(uuid.uuid4())

    # STORE THE LAT/LON AND UUID IN OPENSEARCH
    opensearch_headers = {"Content-Type": "application/json"}

    opensearch_request['uuid'] = submission_uuid
    opensearch_request['location']['lat'] = lat
    opensearch_request['location']['lon'] = lon

    # req = requests.get(search_url, auth=awsauth, headers=headers, data=json.dumps(query))
    opensearch_submit_req = requests.post(doc_url, auth=opensearch_http_auth, headers=opensearch_headers, data=json.dumps(opensearch_request))

    print('Elasticsearch response:', opensearch_submit_req.content)


    # TODO: need to store submission values in dynamodb too!
    # STORE SUBMISSION VALUES IN DYNAMODB



    return response
