import json
import boto3
import os
import tempfile
from utility.utils import create_response
from zipfile import ZipFile

table_name = os.environ['TABLE_NAME']
bucket_name = os.environ['BUCKET_NAME']
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def download_album(event, context):
    folder_name = event['pathParameters']['album']
    cognito_user = event['requestContext']['authorizer']['claims']
    username = cognito_user['cognito:username']
    path = username + "/" + folder_name + "/"

    # Check if the user has access to download the album
    if not has_access_to_download(event,path):
        return create_response(403, {"message": "Access denied"})

    # Generate a temporary file to store the downloaded objects
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_name = temp_file.name

    try:
        with ZipFile(temp_file_name, 'w') as zip_file:
            # Download and add each file/folder to the zip file
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path)
            objects = response.get('Contents', [])
            for obj in objects:
                key = obj['Key']
                file_name = key.split('/')[-1]
                if key.endswith('/'):
                    # Create a folder in the zip file
                    zip_file.write(temp_file_name, file_name + '/')
                else:
                    # Download the file and add it to the zip file
                    s3_client.download_file(bucket_name, key, temp_file_name)
                    zip_file.write(temp_file_name, file_name)

        # Return the zip file as a download response
        with open(temp_file_name, 'rb') as file:
            zip_data = file.read()

        return create_response(200, zip_data, headers={'Content-Type': 'application/zip', 'Content-Disposition': f'attachment; filename="{folder_name}.zip"'})
    except Exception as e:
        return create_response(500, {"message": "Failed to download album"})
    finally:
        # Clean up the temporary file
        temp_file.close()
        os.remove(temp_file_name)

def has_access_to_download(event,path):
    cognito_user = event['requestContext']['authorizer']['claims']
    username = cognito_user['cognito:username']

    table = dynamodb.Table(table_name)
    item = table.get_item(Key={'file': path})

    if 'Item' in item:
        data = item['Item']
        if data['file'].startswith(username + '/'):  # Check if the album is owned by the user
            return True
        shared_with = data.get('shared_with', [])
        if username in shared_with:  # Check if the album is shared with the user
            return True

    return False
