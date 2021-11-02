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
# region = os.environ['AWS_REGION']
# service = 'es'

# credentials = boto3.Session().get_credentials()
# awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# opensearch_http_secret = json.loads(os.environ['OPENSEARCH_USER_SECRET'])
# requests_session = requests.Session()
# requests_session.auth=(opensearch_http_secret['username'], opensearch_http_secret['password'])

opensearch_http_secret = json.loads(os.environ['OPENSEARCH_USER_SECRET'])
opensearch_http_auth = (opensearch_http_secret['username'], opensearch_http_secret['password'])

host = 'https://' + opensearch_url + '/'
index_url = host + os.environ['OPENSEARCH_WIFI_NETWORK_INDEX'] + '/'
search_url = index_url + '_search'


def lambda_handler(event, context):
    print('Request headers', event['headers'])
    print('Request params', event['queryStringParameters'])
    print('Search URL: ', search_url)

    # response template
    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': '',
        'isBase64Encoded': False
    }

    req_params = event['queryStringParameters']

    # Required parameters
    required_params = ['radius', 'lat', 'lon']
    for param in required_params:
        if param not in req_params.keys():
            response['body'] = 'Error: {p} param missing'.format(p=param)
            response['statusCode'] = 400
            return response

    # lat/lon must be valid floats
    try:
        lat_f = float(req_params['lat'])
        lon_f = float(req_params['lon'])
    except:
        response['body'] = 'Error: non-float lat/lon'
        response['statusCode'] = 400

    # radius must be valid int
    try:
        req_geo_radius = int(req_params['radius'])
    except:
        response['body'] = 'Error: non-int radius'
        response['statusCode'] = 400
        return response

    # radius must be >0, < maximum specified in config
    geo_radius_max = int(os.environ['GEO_RADIUS_LIMIT_METRE'])
    if (req_geo_radius <= 0 or req_geo_radius > geo_radius_max):
        response['body'] = 'Radius must be at least 0 and less than {ub}'.format(ub=geo_radius_max)
        response['statusCode'] = 400
        return response

    query_size_limit = int(os.environ['OPENSEARCH_GET_WIFI_NETWORK_LIMIT'])
    query = {
        "query": {
            "bool": {
                "must": {
                    "match_all": {}
                },
                "filter": {
                    "geo_distance": {
                        "distance": str(req_geo_radius)+'m',
                        "location": {
                            "lat": lat_f,
                            "lon": lon_f
                        }
                    }
                }
            }
        }
    }

    headers = {"Content-Type": "application/json"}

    # req = requests.get(search_url, auth=awsauth, headers=headers, data=json.dumps(query))
    search_req = requests.get(search_url, auth=opensearch_http_auth, headers=headers, data=json.dumps(query))

    # return result directly from opensearch
    # todo: maybe only return body if status is 200
    response['body'] = search_req.text
    response['statusCode'] = search_req.status_code

    return response
