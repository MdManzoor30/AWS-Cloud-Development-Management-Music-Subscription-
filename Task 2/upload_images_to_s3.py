import json
import boto3
import requests
import os

"""
Code adapted from AWS Boto3 documentation and Python `requests` library documentation:
AWS Boto3 documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
Python `requests` library documentation: https://realpython.com/python-requests/
"""

def download_images_and_upload_to_s3(json_file, bucket_name):
    # Initialize a boto3 client for S3
    s3_client = boto3.client('s3')

    # Load the JSON data
    with open(json_file) as file:
        data = json.load(file)
        songs = data['songs']

        for song in songs:
            img_url = song['img_url']
            artist = song['artist']
            image_name = os.path.basename(img_url)
            local_filename = f"{artist}_{image_name}"

            # Download the image
            response = requests.get(img_url)
            if response.status_code == 200:
                # Save the image to a local file
                with open(local_filename, 'wb') as f:
                    f.write(response.content)

                # Upload the image to S3
                s3_client.upload_file(local_filename, bucket_name, f"artist_images/{local_filename}")

                # Optional: Remove the local file after upload
                os.remove(local_filename)

                print(f"Uploaded {local_filename} to S3 bucket {bucket_name}")

if __name__ == '__main__':
    json_file = 'a1.json'
    bucket_name = 'mohamed-manzoor'
    download_images_and_upload_to_s3(json_file, bucket_name)