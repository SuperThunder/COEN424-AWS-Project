import json
import requests
import boto3
import os
from requests_aws4auth import AWS4Auth

# handler for GET with a (lat,lon) coordinate and radius

# Look up the coordinate in Elastic, get the UUIDs, then look those up in Dynamo
# Then return the results back

# https://docs.aws.amazon.com/opensearch-service/latest/developerguide/search-example.html
opensearch_url = os.environ['OPENSEARCH_URL']
region = os.environ['AWS_REGION']
service = 'es'

#credentials = boto3.Session().get_credentials()
#awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

#opensearch_http_secret = json.loads(os.environ['OPENSEARCH_USER_SECRET'])
#requests_session = requests.Session()
#requests_session.auth=(opensearch_http_secret['username'], opensearch_http_secret['password'])

opensearch_http_secret = json.loads(os.environ['OPENSEARCH_USER_SECRET'])
opensearch_http_auth=(opensearch_http_secret['username'], opensearch_http_secret['password'])

host = 'https://' + opensearch_url + '/'
index_url = host + os.environ['OPENSEARCH_WIFI_NETWORK_INDEX'] + '/'
search_url = index_url + '_search'

def lambda_handler(event, context):
    print('Request headers', event['headers'])
    print('Search URL: ', search_url)

    print(os.environ['OPENSEARCH_USER_SECRET'])

    query_size_limit = int(os.environ['OPENSEARCH_GET_WIFI_NETWORK_LIMIT'])
    geo_radius = os.environ['GEO_RADIUS_LIMIT_METRE']
    query = {
        "size": query_size_limit,
    }

    headers = {"Content-Type": "application/json"}

    #req = requests.get(search_url, auth=awsauth, headers=headers, data=json.dumps(query))
    req = requests.get(search_url, auth=opensearch_http_auth, headers=headers, data=json.dumps(query))

    if(req.status_code == 200):
        response = {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': req.text,
            'isBase64Encoded': False
        }
    else:
        response = {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': req.text,
            'isBase64Encoded': False
        }


    return response