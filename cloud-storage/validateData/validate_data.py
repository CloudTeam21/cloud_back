import boto3
import json
from utility.utils import create_response
import re

def validate_data(event, context):
    print(event)
    request_data = event
    validated_data = {}

    # Perform validation logic on request_data
    if "firstName" in request_data:
        validated_data["firstName"] = request_data["firstName"]

    if "lastName" in request_data:
        validated_data["lastName"] = request_data["lastName"]

    if "email" in request_data:
        email = request_data["email"]
        if validate_email(email):
            validated_data["email"] = email
        else:
            return create_response(400, {"message": "Invalid email"})

    if "username" in request_data:
        username = request_data["username"]
        if validate_username(username):
            validated_data["username"] = username
        else:
            return create_response(400, {"message": "Invalid username"})

    if "birthDate" in request_data:
        birth_date = request_data["birthDate"]
        if validate_birth_date(birth_date):
            validated_data["birthDate"] = birth_date
        else:
            return create_response(400, {"message": "Invalid birth date"})

    if "password" in request_data:
        password = request_data["password"]
        if validate_password(password):
            validated_data["password"] = password
        else:
            return create_response(400, {"message": "Invalid password format"})

    if "invitingUser" in request_data:
        validated_data["invitingUser"] = request_data["invitingUser"]

    # Call Cognito functions to validate data
    if not validate_with_cognito(validated_data["username"]):
        return create_response(400, {"message": "Username already exists"})
    
    if validate_with_cognito(validated_data["invitingUser"]):
        return create_response(400, {"message": "Inviting user does not exist"})

    return validated_data

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_username(username):
    return len(username) >= 6  # Username must be at least 6 characters long

def validate_birth_date(birth_date):
    try:
        birth_year = int(birth_date.split("-")[0])
        return 1900 <= birth_year <= 2023
    except ValueError:
        return False  # Invalid date format
    
def validate_password(password):
    pattern = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[.#?!@$%^&*-]).{8,}$"
    return re.match(pattern, password) is not None


def validate_with_cognito(username):
    client = boto3.client("cognito-idp", region_name="eu-central-1")  # Update with your desired region

    try:
        response = client.admin_get_user(
            UserPoolId="eu-central-1_GWyc5yETX",
            Username=username
        )
        if response and "Username" in response:
            return False
        else:
            return True
    except client.exceptions.UserNotFoundException:
        return True

