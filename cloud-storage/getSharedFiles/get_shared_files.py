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

    cognito_user = event['requestContext']['authorizer']['claims']

    # Table name
    table = dynamodb.Table(table_name)
    
    response = table.scan(
    FilterExpression='contains(shared_with, :cognito_user)',
    ExpressionAttributeValues={':cognito_user': cognito_user}
    )
    
    files_metadata = response['Items']
    files_metadata = sorted(files_metadata, key=lambda x: x['added'], reverse=True)
    
    files_data = []
    
    for metadata in files_metadata:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read() 
        file_content_base64 = base64.b64encode(file_content)
        files_data.append({'metadata': metadata, 'content': file_content_base64})

    # Step 3: Combine DynamoDB Data and Files
    combined_data = {'files': files_data}

    return create_response(200, combined_data)
