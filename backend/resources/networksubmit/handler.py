import json


# handler for a POST to submit a wifi network given:
#   Network name (SSID)
#   User ID of poster
#   Password of network (plaintext)
#   (lon, lat) of network

# We will generate a UUID to uniquely identify the network submission

def lambda_handler(event, context):
    print('Request body', event['body'])

    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': '{GET}',
        'isBase64Encoded': False
    }

    return response