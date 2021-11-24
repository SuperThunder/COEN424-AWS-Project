import json
import requests
import boto3
import os
from requests_aws4auth import AWS4Auth

# handler for GET with a (lat,lon) coordinate and radius

# Look up the coordinate in Elastic, get the UUIDs, then look those up in Dynamo
# Then return the results back

dynamodb = boto3.resource('dynamodb')
wifinetwork_table_name = "backend-Project424Backend-NetworkDynamoDB591E2ABE-1UWQYVER05ZNL"
wifinetwork_table = dynamodb.Table(wifinetwork_table_name)

uuid = "58e09de4-23f0-4691-8b78-4cd04dacf63a"

dynamo_key = {
    'uuid': uuid
}

ddres = wifinetwork_table.get_item(Key=dynamo_key)

print(ddres)
