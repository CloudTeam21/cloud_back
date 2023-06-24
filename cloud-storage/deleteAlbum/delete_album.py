import json
import boto3
import base64
import os
from utility.utils import create_response

table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def delete_album(event, context):
    
    cognito_user = event['requestContext']['authorizer']['claims']

    folder_name = event['pathParameters']['album']
    path = cognito_user['cognito:username'] + "/" + folder_name + "/"

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path)

    if 'Contents' in response:
        objects = [{'Key': obj['Key']} for obj in response['Contents']]
        s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects})
    # Upload the file to S3

    table = dynamodb.Table(table_name)
    
    response = table.scan(
        FilterExpression='begins_with(#file, :prefix)',
        ExpressionAttributeNames={'#file': 'file'},
        ExpressionAttributeValues={':prefix': path}
    )

    items = response['Items']

    for item in items:
        print(item['file'])
        table.delete_item(Key={'file': item['file']})

    return create_response(200, {"message": "Album deleted successfully"})
