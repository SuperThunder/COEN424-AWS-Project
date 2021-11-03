import json
import os
import requests

# handler for a POST to submit a wifi network given:
#   Network name (SSID)
#   User ID of poster
#   Password of network (plaintext)
#   Security type (None, WEP, WPA2, WPA3)
#   (lon, lat) of network

# We will generate a UUID to uniquely identify the network submission

opensearch_url = os.environ['OPENSEARCH_URL']
opensearch_http_secret = json.loads(os.environ['OPENSEARCH_USER_SECRET'])
opensearch_http_auth = (opensearch_http_secret['username'], opensearch_http_secret['password'])

host = 'https://' + opensearch_url + '/'
index_url = host + os.environ['OPENSEARCH_WIFI_NETWORK_INDEX'] + '/'
search_url = index_url + '_search'

def lambda_handler(event, context):
    print('Request body', event['body'])

    req_body = json.loads(event['body'])



    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': '{SUBMIT WIFI NETWORK (POST)}',
        'isBase64Encoded': False
    }

    return response