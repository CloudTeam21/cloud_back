import json
import boto3
import base64
import os
from utility.utils import create_response

table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def get_files(event, context):
    # Extract the file content and metadata from the request
    request_body = json.loads(event['body'])
    # bucket_name = 'bucket-files' #TODO envirement variable
    
    cognito_user = event.requestContext.authorizer.claims
    path = cognito_user['cognito:username'] + "/"

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path)
    
    objects = response['Contents']
    filtered_objects = []
    
    for obj in objects:
        if obj['Key'].startswith(prefix) and obj['Key'].endswith('/'):
            filtered_objects.append(obj)

    return create_response(200, filtered_objects)
