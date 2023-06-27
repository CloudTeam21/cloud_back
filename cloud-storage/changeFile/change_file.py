from datetime import datetime
import json
import boto3
import os

from utility.utils import create_response

bucket_name = os.environ['BUCKET_NAME']
table_name = os.environ['TABLE_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
cognito_client = boto3.client('cognito-idp', region_name='eu-central-1')
ses_client = boto3.client('ses')

def upload_content(event, context):
    user_id = event['requestContext']['authorizer']['claims']['sub']
        # Extract the file path, caption, and tags from the request
    request_body = json.loads(event['body'])
    file_path = request_body['file_path']
    caption = request_body['caption']
    tags = request_body['tags']

    # Update the caption, tags, and lastModified in the DynamoDB table
    table = dynamodb.Table(table_name)
    current_time = datetime.now().isoformat()
    response = table.update_item(
        Key={
            'file': file_path
        },
        UpdateExpression='SET caption = :caption, tags = :tags, lastModified = :lastModified',
        ExpressionAttributeValues={
            ':caption': caption,
            ':tags': tags,
            ':lastModified': current_time
        }
    )
    send_email_notification(file_path, user_id)
    return create_response(200, {"message": "File updated successfully"})

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

def send_email_notification(file_path, user_id):
    subject = "File Changed Notification"
    body = f"The file '{file_path}' has been changed."
    
    ses_client.send_email(
        Source="karolinatrambolina@gmail.com",
        Destination={"ToAddresses": ["karolinatrambolina@gmail.com"]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        }
    )