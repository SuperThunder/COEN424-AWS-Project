import json
import requests
import boto3
import os
from requests_aws4auth import AWS4Auth

# handler for GET with a (lat,lon) coordinate and radius

# Look up the coordinate in Elastic, get the UUIDs, then look those up in Dynamo
# Then return the results back

dynamodb = boto3.resource('dynamodb')
wifinetwork_table_name = os.environ['WIFINETWORK_TABLE_NAME']
wifinetwork_table = dynamodb.Table(wifinetwork_table_name)

def lambda_handler(event, context):
    
    # TODO Return either all the users or process other parameters to return only few users
    #      very brief information like the username / userID in the system so we can reach his data,
    #      full and specific user info should be fetched using the proxy path as the user ID should be the first segment
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello world!')
    }
