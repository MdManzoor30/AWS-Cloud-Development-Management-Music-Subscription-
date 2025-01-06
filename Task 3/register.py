import json
import boto3
import hashlib
import os

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['USER_TABLE'])

    body = json.loads(event['body'])
    email = body['email']
    username = body['username']
    password = hashlib.sha256(body['password'].encode()).hexdigest()

    try:
        table.put_item(
            Item={
                'email': email,
                'user_name': username,
                'password': password
            },
            ConditionExpression='attribute_not_exists(email)'
        )
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }

    return {
        'statusCode': 200,
        'body': json.dumps('User registered successfully')
    }
