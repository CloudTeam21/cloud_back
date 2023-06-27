import boto3
from utility.utils import create_response
import os

table_name = os.environ['INVITES_TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def process_invite(event, context):
    path_params = event['pathParameters']
    invite_type = path_params['type']

    # Extract query parameters
    query_params = event['queryStringParameters']
    username = query_params['username']
    invited_by = query_params['invitedBy']

    if invite_type == 'accept':
        status = 'ACCEPTED'
        
    elif invite_type == 'deny':
        status = 'DENIED'
    else:
        return create_response(400, 'Invalid request')

    invites_table = dynamodb.Table(table_name)

    response = invites_table.get_item(
            Key={
                'username': username
            }
    )
    item = response.get('Item')

    if item and item.get('invitedBy') == invited_by:
        response = invites_table.update_item(
            Key={
                'username': username
            },
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':status': status
            }
        )
        notify_user(username, invited_by, status.lower())
        
        return create_response(200, f'Invite {status.lower()}')
    else:
        return create_response(400, 'Invalid invitation')
    
def notify_user(username, invited_by, status):
    email = get_email(username)
    subject = 'Invitation Status'
    message = f'Your family member with username {invited_by} has {status} your invitation.'
    client = boto3.client('ses')
    response = client.send_email(
        Source='karolinatrambolina@gmail.com',
        Destination={
            'ToAddresses': [email]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': message
                }
            }
        }
    )

def get_email(username):
    client = boto3.client("cognito-idp", region_name="eu-central-1")

    try:
        response = client.admin_get_user(
            UserPoolId="eu-central-1_GWyc5yETX",
            Username=username
        )
        if response and "Username" in response:
            for attribute in response['UserAttributes']:
                if attribute['Name'] == 'email':
                    return attribute['Value']
        else:
            return None
    except client.exceptions.UserNotFoundException:
        return None