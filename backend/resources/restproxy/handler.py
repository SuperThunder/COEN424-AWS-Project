import json

def lambda_handler(event, context):
    
    # TODO Handle the request based on the httpMethod and the path parameters of the event.
    
    # TODO Methods to handle:
    # 1) GET /users/{user_id+}                                      -> full info of specific user, except favorites and markers
    # 3) GET /users/{user_id+}/markers                              -> full list of user's markers
    # 5) GET and DELETE /users/{user_id+}/markers/marker_id         -> GET full info of the specific marker / DELETE the specific marker from the system entirely
    # 6) GET and UPDATE (or POST) /networks/{marker_id+}            -> GET full info of a specific marker / UPDATE the data of the speicific marker

    return {
        'statusCode': 200,
        'body': json.dumps('Request Method:'+event['httpMethod']+',  Request Path: '+event['path'])
    }
