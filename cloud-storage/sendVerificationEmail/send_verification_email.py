import boto3
import json
from utility.utils import create_response

def send_verification_email(event, context):
    request_data = event
    print(request_data)
    inviting_user_email = validate_with_cognito(request_data["invitingUser"])
    print(inviting_user_email)
    username = request_data["username"]
    client = boto3.client('cognito-idp')
 
    response = client.admin_create_user(
        UserPoolId='eu-central-1_GWyc5yETX',
        Username=username,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': inviting_user_email
            }
        ],
        MessageAction='RESEND'
    )

    # Handle the response and any additional logic
    # ...
    return create_response(200, "Verification email sent successfully")

def validate_with_cognito(username):
    client = boto3.client("cognito-idp", region_name="eu-central-1")  # Update with your desired region

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
