import boto3
from utility.utils import create_response

def send_verification_email(event, context):
    request_data = event['body']
    inviting_user_email = validate_with_cognito(request_data["invitingUser"])
    username = request_data["username"]
    invitedBy = request_data["invitingUser"]
 
    client = boto3.client('ses')
    
    accept = f'<a href="http://localhost:4200/accept?username={username}&invitedBy={invitedBy}">localhost:4200/accept?username={username}&invitedBy={invitedBy}</a>'
    deny = f'<a href="http://localhost:4200/deny?username={username}&invitedBy={invitedBy}">localhost:4200/deny?username={username}&invitedBy={invitedBy}</a>'
    
    
    # Compose the email message
    subject = 'Email Verification'
    message = f'Your family member with username {username} has accepted your invitation. To grant them access to your files click link {accept} or if you want to deny click {deny}.'

    response = client.send_email(
        Source='karolinatrambolina@gmail.com',
        Destination={
            'ToAddresses': [inviting_user_email]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Html': {
                    'Data': message
                }
            }
        }
    )
    
    return { 
        'statusCode': 200, 
        'body': request_data
        }

def validate_with_cognito(username):
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
