import json
import boto3
import base64
import os
from utility.utils import create_response

table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def upload(event, context):
    # Extract the file content and metadata from the request
    request_body = json.loads(event['body'])
    # bucket_name = 'bucket-files' #TODO envirement variable
    file_content = base64.b64decode(request_body['file']['content']  + "="*((4 - len(request_body['file']['content']) % 4) % 4))
    file_name = request_body['file']['filename']
    file_size = request_body['file']['size']
    file_type = request_body['file']['type']
    file_last_modified = request_body['file']['lastModified']
    caption = request_body['file']['caption']
    tags = request_body['file']['tags']
        
    # Upload the file to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=file_content
    )
    
    # Table name
    table = dynamodb.Table(table_name)
    
    # Insert file name into table
    response = table.put_item(
        Item={
            'file': file_name,
            'type': file_type,
            'size': file_size,
            'lastModified': file_last_modified,
            'caption': caption,
            'tags': tags
        }
    )
    
    return create_response(200, {"message": "File uploaded successfully"})
