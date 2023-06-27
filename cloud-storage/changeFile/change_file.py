import json
import boto3
import os

from utility.utils import create_response

bucket_name = os.environ['BUCKET_NAME']
table_name = os.environ['TABLE_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
cognito_client = boto3.client('cognito-idp', region_name='eu-central-1')

def upload_content(event, context):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    
    content_id = event['pathParameters']['contentId']
    file_name = event['body']['fileName']
    file_content = event['body']['fileContent']
    description = event['body']['description']
    tags = event['body']['tags']
    
    if is_authorized(user_id) and is_owner(user_id, file_name):
        upload_to_s3(content_id, file_name, file_content)
        create_dynamodb_item(content_id, user_id, file_name, description, tags)
        response = create_response(200, {'message': 'File uploaded successfully'})
    else:
        response = create_response(403, {'message': "You don't have access"})
    
    return response

def is_authorized(user_id):
    try:
        response = cognito_client.admin_get_user(
            UserPoolId='eu-central-1_GWyc5yETX',
            Username=user_id
        )
        if response['UserStatus'] == 'CONFIRMED':
            return True
        else:
            return False
    except cognito_client.exceptions.UserNotFoundException:
        return False
    
def is_owner(user_id, path):
    table = dynamodb.Table(table_name)
    response = table.get_item(
        Key={'file': path}
    )

    item = response.get('Item')

    if item:
        owner_username = item.get('file').split('/')[0]

        if owner_username == user_id:
            return True
        
    return False

def upload_to_s3(content_id, file_name, file_content):
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f'{content_id}/{file_name}',
        Body=file_content
    )

def create_dynamodb_item(content_id, user_id, file_name, description, tags):
    table = dynamodb.Table(table_name)
    table.put_item(
        Item={
            'contentId': content_id,
            'userId': user_id,
            'fileName': file_name,
            'description': description,
            'tags': tags
        }
    )
