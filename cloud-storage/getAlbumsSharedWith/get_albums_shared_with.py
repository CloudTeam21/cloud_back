import boto3
import os
from utility.utils import create_response

table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')

def get_albums_shared_with(event, context):
    folder_name = event['pathParameters']['album'].replace("-", "/")
    if (folder_name.startswith("/all/")):
        folder_name = folder_name[4:]
    # else:
    #     folder_name= "/" + folder_name
    cognito_user = event['requestContext']['authorizer']['claims']
    path = cognito_user['cognito:username'] + folder_name
    print(path)
    table = dynamodb.Table(table_name)
    
    response = table.scan(
        FilterExpression='begins_with(#file, :prefix)',
        ExpressionAttributeNames={'#file': 'file'},
        ExpressionAttributeValues={':prefix': path}
    )

    files = response['Items']
    shared_with_list = []
    print(len(files))
    for file in files:
        if 'shared_with' in file:
            for i in file['shared_with']:
                shared_with_list.append(i)
    shared_with_list = set(shared_with_list)
    
    return create_response(200, list(shared_with_list))