import os
import time

import boto3

DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']


def fetch_file(file_id):
    dynamodb = boto3.client("dynamodb")

    response = dynamodb.get_item(
        TableName=DYNAMODB_TABLE,
        Key={
            'id': {
                'S': file_id,
            },
            'index': {
                'N': str(0),
            },
        },
        ConsistentRead=False,
    )

    if not 'Item' in response:
        return dict(url=None)

    return dict(url=response['Item']['url']['S'])


def mark_file_generated(file_id, url):
    dynamodb = boto3.client("dynamodb")

    dynamodb.put_item(
        TableName=DYNAMODB_TABLE,
        Item={
            'id': {
                'S': file_id,
            },
            'index': {
                'N': str(0),
            },
            'url': {
                'S': url,
            },
            'expires': {
                'N': str(int(time.time() + 10 * 60)),
            },
        },
    )
