import json

def create_response(status, body):
    return { 
        'statusCode': status, 
        'headers': {
            'Access-Control-Allow-Origin': 'http://localhost:4200',
        },
        'body': json.dumps(body, default=str)
        }
