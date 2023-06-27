import boto3
import json
import os
from utility.utils import create_response
from datetime import datetime

table_name = os.environ['INVITES_TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def create_user(event, context):
    cognito_client = boto3.client('cognito-idp', region_name='eu-central-1')
    user_pool_id = 'eu-central-1_GWyc5yETX'

    validated_data = event['body']

    user_attributes = [
        {
            'Name': 'email',
            'Value': validated_data['email']
        },
        {
            'Name': 'given_name',
            'Value': validated_data['firstName']
        },
        {
            'Name': 'family_name',
            'Value': validated_data['lastName']
        },
        {
            'Name': 'birthdate',
            'Value': validated_data['birthDate']
        }
    ]

    try:
        response = cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=validated_data['username'],
            UserAttributes=user_attributes,
            TemporaryPassword=validated_data['password'],
            MessageAction='SUPPRESS'  # Do not send a verification message
        )
        
        table = dynamodb.Table(table_name)
        table.put_item(
        Item={
            'username': validated_data['username'],
            'invitedBy': validated_data['invitingUser'],
            'status': 'PENDING'
        }
    )
        
        return { 
        'statusCode': 200, 
        'body': validated_data
        }
    except cognito_client.exceptions.UsernameExistsException:
        return create_response(400, {'message': 'Username already exists'})
    except Exception as e:
        return create_response(400, {'message': 'Error creating user', 'error': str(e)})
