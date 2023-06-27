import boto3
import json
from utility.utils import create_response
from datetime import datetime


def create_user(event, context):
    cognito_client = boto3.client('cognito-idp', region_name='eu-central-1')
    user_pool_id = 'eu-central-1_GWyc5yETX'

    validated_data = event
    birth_date = datetime.strptime(validated_data['birthDate'], '%Y-%m-%d').date()
    birth_date_str = birth_date.isoformat()

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
            'Value': birth_date_str
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
        user_created = response['User']
        return create_response(200, {"body": json.dumps({'userCreated': user_created})})
    except cognito_client.exceptions.UsernameExistsException:
        return create_response(400, {'message': 'Username already exists'})
    except Exception as e:
        return create_response(400, {'message': 'Error creating user', 'error': str(e)})
