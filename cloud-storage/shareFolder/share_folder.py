import json
import boto3
import os
from utility.utils import create_response
from botocore.exceptions import ClientError

table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
cognito_client = boto3.client('cognito-idp')

def shareFile(event, context):
    request_body = json.loads(event['body'])
    usernames = request_body['usernames']
    file_name = request_body['file']
    cognito_user = event['requestContext']['authorizer']['claims']['cognito:username']
    file_name = cognito_user + file_name[4:]
    print(file_name)
    
    table = dynamodb.Table(table_name)
    item = table.get_item(Key={'file': file_name})

    message = "File shared successfully"
    if 'Item' in item:

        data = item['Item']
        shared_with_list = []
        
        for username in usernames:
            if check_username_exists(username):
                shared_with_list.append(username)
            else:
                message = "Some usernames do not exist"

        if event['requestContext']['authorizer']['claims']['cognito:username'] in shared_with_list:
            shared_with_list.remove(event['requestContext']['authorizer']['claims']['cognito:username'])

        if not shared_with_list:
            result = table.update_item(
                Key={'file': data['file']},
                UpdateExpression="REMOVE shared_with",
                ReturnValues="UPDATED_NEW"
            )
        else:
            result = table.update_item(
                Key={'file': data['file']},
                UpdateExpression="SET shared_with = :my_value",
                ExpressionAttributeValues={":my_value": set(shared_with_list)},
                ReturnValues="UPDATED_NEW"
            )
        return create_response(200, {"message": message})
    else:
        return create_response(400, {"message": "File not found"})

def check_username_exists(username):
    user_pool_id = 'eu-central-1_GWyc5yETX'

    try:
        response = cognito_client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        return True  # Users exists
    except ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            return False  # User does not exist
