import json
import os
import boto3
from utility.utils import create_response

bucket_name = os.environ['BUCKET_NAME']
table_name = os.environ['TABLE_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
cognito_client = boto3.client('cognito-idp', region_name='eu-central-1')
ses_client = boto3.client('ses')

def move_file(event, context):
    # Extract the user ID and file paths from the request
    user_id = event['requestContext']['authorizer']['claims']['cognito:username']
    request_body = json.loads(event['body'])
    old_file_path = request_body['old_file_path']
    new_file_path = request_body['new_file_path']
    print(user_id)

    # Check if the user is authorized and the owner of the file
    if not is_owner(user_id, old_file_path):
        return create_response(403, {"message": "User is not the owner of the file"})

    try:
        # Get the existing item
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'file': old_file_path})
        existing_item = response.get('Item')
        
        if existing_item:
            # Delete the existing item
            table.delete_item(Key={'file': old_file_path})
        
            # Create a new item with the updated file value
            new_item = {**existing_item, 'file': new_file_path}
            table.put_item(Item=new_item)
        else:
            # Handle the case where the item with the specified key does not exist
            return create_response(400, {"message": 'Item not found'})

        send_email_notification(new_file_path, user_id)
        return create_response(200, {"message": "File path changed successfully"})
    except Exception as e:
        return create_response(500, {"message": str(e)})

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
    body = f"The file '{file_path}' has been moved."

    ses_client.send_email(
        Source="karolinatrambolina@gmail.com",
        Destination={"ToAddresses": ["karolinatrambolina@gmail.com"]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        }
    )
