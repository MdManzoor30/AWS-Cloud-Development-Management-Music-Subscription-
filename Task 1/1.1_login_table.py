import boto3

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')

def create_table():
    """
    Function to create a DynamoDB table.
    Code adapted from AWS Boto3 Documentation:
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html
    """
    table = dynamodb.create_table(
        TableName='login',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'}  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'}  # S for string type
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName='login')
    print("Table created successfully.")

if __name__ == "__main__":
    create_table()
