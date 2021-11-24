import json
import requests
import boto3
import os
import decimal

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
required_params = ['radius', 'lat', 'lon']


def lambda_handler(event, context):
    print('Request headers: ', event['headers'])
    print('Request params: ', event['queryStringParameters'])
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

    # lat/lon must be valid floats
    try:
        lat_f = float(req_params['lat'])
        lon_f = float(req_params['lon'])
    except:
        response['body'] = 'Error: non-float lat/lon'
        return response

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

    # check if opensearch search was successful
    if(search_req.status_code != 200):
        print('Search encountered an error', search_req.content)
        response['body'] = 'Search encountered an error ({e})'.format(e=search_req.content)
        response['statusCode'] = 500
        return response

    search_json = json.loads(search_req.content)

    # no results
    if(search_json['hits']['total']['value'] == 0):
        response['body'] = ''
        response['statusCode'] = 204  # 'no content'

    # DynamoDB key query template
    dynamo_key = {
        'uuid': ''
    }

    # If we got results, get them from DynamoDB by using the UUID that links Dynamo and OpenSearch values
    dynamo_results = []
    os_hits = search_json['hits']['hits']
    for hit in os_hits:
        uuid = hit['_source']['uuid']
        try:
            dynamo_key['uuid'] = uuid
            ddres = wifinetwork_table.get_item(Key=dynamo_key)

            # get_item returns 200 even for primary keys that don't exist
            # and the library does not throw an exception!
            if not 'Item' in ddres.keys():
                print('UUID {u} does not exist in DynamoDB. Is it a leftover in Opensearch?'.format(u=uuid))
                continue # skip to next item

        except Exception as e:
            # Try to ignore invalid keys (existing in OpenSearch but not Dynamo), but log that they happened
            print('Error retrieving UUID {u} from Dynamo: {e}'.format(u=uuid, e=e))
            continue # skip to next item

        item = ddres['Item']
        # json does not know how to serialize Decimal, so convert back to float
        #item['lat'] = float(item['lat'])
        #item['lon'] = float(item['lon'])

        for x in item.keys():
            if type(x) == decimal.Decimal:
                item[x] = float(item[x])

        dynamo_results.append(item)

    response['body'] = json.dumps({'results': dynamo_results})
    response['statusCode'] = 200

    return response
