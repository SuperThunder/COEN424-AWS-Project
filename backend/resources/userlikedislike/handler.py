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


def lambda_handler(event, context):

    
    return response