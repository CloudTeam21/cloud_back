import json
import boto3
import base64
import os
from utility.utils import create_response

table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def create_album(event, context):

    request_body = json.loads(event['body'])
    folder_name = request_body.get('foldername', "")
    
    cognito_user = event['requestContext']['authorizer']['claims']
    path = cognito_user['cognito:username'] + "/" + folder_name + "/"

    # Upload the file to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key= path
    )
    
    return create_response(200, {"message": "Album created successfully"})
