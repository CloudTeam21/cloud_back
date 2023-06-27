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
    # bucket_name = 'bucket-files' #TODO envirement variable
    folder_name = event['pathParameters']['album'].replace("-", "/") + "/"
    
    if (folder_name.startswith("all/")):
        folder_name = folder_name[3:]
    else:
        folder_name= "/" + folder_name
    cognito_user = event['requestContext']['authorizer']['claims']
    path = cognito_user['cognito:username'] + folder_name
    # Table name
    table = dynamodb.Table(table_name)
    
    response = table.scan(
        FilterExpression='begins_with(#file, :prefix)',
        ExpressionAttributeNames={'#file': 'file'},
        ExpressionAttributeValues={':prefix': path}
    )
    
    files_metadata = response['Items']
    files_metadata = sorted(files_metadata, key=lambda x: x['added'], reverse=True)
    
    files_data = []
    for metadata in files_metadata:
        file_key = metadata['file']
        if "/" in file_key.split(path)[1]:
            continue
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read() 
        file_content_base64 = base64.b64encode(file_content)
        files_data.append({'metadata': metadata, 'content': file_content_base64})

    # Step 3: Combine DynamoDB Data and Files
    combined_data = {'files': files_data}

    return create_response(200, combined_data)
