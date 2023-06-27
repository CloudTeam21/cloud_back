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

def delete(event, context):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    file_path = event['pathParameters']['file']

    if True:
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=file_path
        )

        table = dynamodb.Table(table_name)
        deleted = table.delete_item(
            Key={'file': file_path}
        )
        send_email_notification(file_path, user_id)
        response = create_response(200, {"message": "File deleted successfully"})
    else:
        response = create_response(403, {'message': "You don't have access"})
    

    return response

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
    # user = cognito_client.admin_get_user(
    #         UserPoolId='eu-central-1_GWyc5yETX',
    #         Username=user_id
    #     )
    # recipient_email = None
    # for attribute in user['UserAttributes']:
    #     if attribute['Name'] == 'email':
    #         recipient_email = attribute['Value']
    #         break
    subject = "File Deleted Notification"
    body = f"The file '{file_path}' has been deleted."
    
    ses_client.send_email(
        Source="karolinatrambolina@gmail.com",
        Destination={"ToAddresses": ["karolinatrambolina@gmail.com"]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        }
    )
