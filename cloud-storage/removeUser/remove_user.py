import boto3

def remove_user(event, context):
    request_data = event['body']
    username = request_data['username']
    user_pool_id = 'eu-central-1_GWyc5yETX'

    cognito_client = boto3.client('cognito-idp')

    try:
        response = cognito_client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        return {
            'statusCode': 200,
            'body': 'User removed successfully'
        }
    except cognito_client.exceptions.UserNotFoundException:
        return {
            'statusCode': 404,
            'body': 'User not found'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': 'Error occurred: ' + str(e)
        }