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

def download_file(event, context):
    file_name = event['pathParameters']['file']
    file_name = file_name.replace("-","/")

    # Check if the user has access to download the file
    if not has_access_to_download(event,file_name):
        return create_response(403, {"message": "Access denied"})

    # Generate a pre-signed URL for downloading the file
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_name
            },
            ExpiresIn=3600  # URL expiration time in seconds
        )
        return create_response(200, {"url": url})
    except ClientError as e:
        return create_response(500, {"message": "Failed to generate download URL"})

def has_access_to_download(event,file_name):
    cognito_user = event['requestContext']['authorizer']['claims']
    username = cognito_user['cognito:username']

    table = dynamodb.Table(table_name)
    item = table.get_item(Key={'file': file_name})

    if 'Item' in item:
        data = item['Item']
        if data['file'].startswith(username + '/'):  # Check if the file is owned by the user
            return True
        shared_with = data.get('shared_with', [])
        if username in shared_with:  # Check if the file is shared with the user
            return True

    return False
