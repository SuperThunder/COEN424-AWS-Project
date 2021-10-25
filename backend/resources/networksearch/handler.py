import json


# handler for GET with a (lon,lat) coordinate and radius

# Look up the coordinate in Elastic, get the UUIDs, then look those up in Dynamo
# Then return the results back

def lambda_handler(event, context):
    print('Request body', event['body'])

    response = {
        'statusCode': 418,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': '{SEARCH}',
        'isBase64Encoded': False
    }

    return response