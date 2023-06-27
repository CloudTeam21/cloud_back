import boto3
import os
from utility.utils import create_response

table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def grant_access(event, context):
    request_body = event['body']
    response = verify_user(request_body['username'], request_body['password'])
    if response['statusCode'] != 200:
        return response

    table = dynamodb.Table(table_name)
    response = table.scan()

    items = response['Items']

    # Filter items based on the "file" attribute
    filtered_items = [item for item in items if item.get('file', '').startswith(request_body['invitingUser'])]

    # Update items
    for item in filtered_items:
        shared_with_set = item.get('shared_with')
        if not shared_with_set:
            shared_with_set = []
        shared_with_set = list(shared_with_set)
        shared_with_set.append(request_body['username'])
        shared_with_set = set(shared_with_set)

        table.update_item(
            Key={'file': item['file']},
            UpdateExpression='SET shared_with = :shared',
            ExpressionAttributeValues={':shared': shared_with_set}
        )


def verify_user(username, password):
    client = boto3.client('cognito-idp', region_name='eu-central-1')
    try:
        response = client.admin_update_user_attributes(
            UserPoolId='eu-central-1_GWyc5yETX',
            Username=username,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ]
        )
        client.admin_set_user_password(
            UserPoolId='eu-central-1_GWyc5yETX',
            Username=username,
            Password=password,
            Permanent=True
        )
        return create_response(200, 'User verification status updated successfully')
    except client.exceptions.UserNotFoundException:
        return create_response(400, 'User not found') 
    except Exception as e:
        return create_response(400, 'Error updating user verification status: ' + str(e))
