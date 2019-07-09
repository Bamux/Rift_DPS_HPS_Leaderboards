import logging
import boto3
from botocore.exceptions import ClientError
import os


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ContentType': 'text/html'})
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    path = "public"
    files = os.listdir(path)
    for file in files:
        if ".html" in file:
            upload_file(path + "/" + file, "rift-stats", file)
            print(file + " uploaded")


if __name__ == "__main__":
    main()
