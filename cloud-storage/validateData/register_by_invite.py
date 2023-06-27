import boto3

def lambda_handler(event, context):
    user_data = event['user_data']
    user_pool_id = 'eu-central-1_GWyc5yETX'
    cognito_client = boto3.client('cognito-idp')

    try:
        # Perform validation on the user data
        is_valid = validate_user_data(user_data)
        if not is_valid:
            raise ValueError("Invalid user data")

        # Extract user data
        firstName = user_data['firstName']
        lastName = user_data['lastName']
        email = user_data['email']
        username = user_data['username']
        password = user_data['password']
        birthDate = user_data['birthDate']
        invitingUser = user_data['invitingUser']

        # Create the user in AWS Cognito
        response = cognito_client.sign_up(
            ClientId='7829mrqnglbe1o4sl91k3q18ap',
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'given_name',
                    'Value': firstName
                },
                {
                    'Name': 'family_name',
                    'Value': lastName
                },
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'birthdate',
                    'Value': birthDate
                },
                # Add any other relevant attributes for the user
            ],
            ValidationData=[
                {
                    'Name': 'custom:invitingUser',
                    'Value': invitingUser
                }
            ],
            UserPoolId=user_pool_id
        )

        print("User created in Cognito")
        return {
            'statusCode': 200,
            'body': 'User created successfully'
        }
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return {
            'statusCode': 400,
            'body': 'Invalid user data'
        }

def validate_user_data(user_data):
    # Perform validation on the user data
    # Implement your validation logic here
    # Return True if the data is valid, False otherwise
    return True
