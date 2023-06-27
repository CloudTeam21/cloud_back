import boto3
import os

table_name = os.environ['INVITES_TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def check_confirmation(event, context):
    request_data = event['body']

    invites_table = dynamodb.Table(table_name)

    response = invites_table.get_item(
            Key={
                'username': request_data['username']
            }
    )
    item = response.get('Item')
    
    if item and item.get('invitedBy') == request_data['invitingUser']:
        if item.get('status') == 'PENDING':
            if item.get('status') == 'PENDING':
                raise Exception('Invitation still pending')
        if item.get('status') == 'ACCEPTED':
            return { 
            'statusCode': 200, 
            'body': request_data,
            'message': 'Invitation accepted'
            }
        elif item.get('status') == 'DENIED':
            return { 
            'statusCode': 400, 
            'body': request_data,
            'message': 'Invite denied'
            }
    return { 
    'statusCode': 400, 
    'body': request_data,
    'message': 'Invalid request'
    }