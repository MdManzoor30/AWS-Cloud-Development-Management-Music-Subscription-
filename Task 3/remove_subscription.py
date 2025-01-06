import json
import boto3
import os

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['SUBSCRIPTION_TABLE'])

    body = json.loads(event['body'])
    email = body['email']
    title = body['title']

    try:
        table.delete_item(
            Key={
                'email': email,
                'title': title
            }
        )
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Unsubscribed from song successfully')
    }
