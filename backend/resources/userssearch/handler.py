import json

def lambda_handler(event, context):
    
    # TODO Return either all the users or process other parameters to return only few users
    #      very brief information like the username / userID in the system so we can reach his data,
    #      full and specific user info should be fetched using the proxy path as the user ID should be the first segment
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello world!')
    }
