import boto3
import json


"""
Code adapted from AWS Boto3 documentation and other sources:
- AWS Boto3 DynamoDB documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html
- JSON handling in Python: https://docs.python.org/3/library/json.html
"""

def load_data(file_path, table_name):
    # Initialize a DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Load the JSON data
    with open(file_path) as json_file:
        data = json.load(json_file)
        songs = data['songs']

        for song in songs:
            title = song['title']
            artist = song['artist']
            year = song['year']
            web_url = song['web_url']
            img_url = song['img_url']  # Ensure the key matches your JSON structure

            print(f"Adding song: {title}, {artist}")

            # Put the song into the DynamoDB table
            table.put_item(
                Item={
                    'title': title,
                    'artist': artist,
                    'year': year,
                    'web_url': web_url,
                    'img_url': img_url
                }
            )

if __name__ == '__main__':
    file_path = 'a1.json'  # Path to your JSON file
    table_name = 'music'  # DynamoDB table name
    load_data(file_path, table_name)
