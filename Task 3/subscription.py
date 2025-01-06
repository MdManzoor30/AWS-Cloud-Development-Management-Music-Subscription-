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
        table.put_item(
            Item={
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
        'body': json.dumps('Subscribed to song successfully')
    }
