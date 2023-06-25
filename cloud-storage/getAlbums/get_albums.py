import json
import boto3
import base64
import os
from utility.utils import create_response

table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def get_albums(event, context):
    # bucket_name = 'bucket-files' #TODO envirement variable
    
    cognito_user = event['requestContext']['authorizer']['claims']
    folder_name = event['pathParameters']['album']

    if (folder_name != "all"):
        folder_name= "/" + folder_name
    else:
        folder_name = ""

    path = cognito_user['cognito:username'] + folder_name + "/"

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path)
    objects = response.get('Contents', [])
    filtered_objects = []
    
    for obj in objects:
        if obj['Key'].startswith(path) and obj['Key'].endswith('/'):
            folder = obj['Key'].split(path)[1].split("/")[0]
            if (folder != "" and folder not in filtered_objects):
                filtered_objects.append(folder)
    return create_response(200, filtered_objects)
