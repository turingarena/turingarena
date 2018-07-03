import json
import time

import boto3

from turingarena_impl.evaluation.events import EvaluationEvent


def store_events(evaluation_id, events):
    dynamodb = boto3.client("dynamodb")

    for i, e in enumerate(events):
        dynamodb.put_item(
            TableName='EvaluationEventsTable',
            Item={
                'evaluation_id': {
                    'S': evaluation_id,
                },
                'index': {
                    'N': str(i),
                },
                'data': {
                    'S': str(e) + "\n",
                },
                'expires': {
                    'N': str(int(time.time() + 10 * 60)),
                },
            },
        )


def load_events(evaluation_id, after):
    dynamodb = boto3.client("dynamodb")

    response = dynamodb.query(
        TableName='EvaluationEventsTable',
        Limit=100,
        ConsistentRead=False,
        KeyConditionExpression='#evaluation_id = :evaluation_id AND #index >= :after',
        ExpressionAttributeNames={
            '#evaluation_id': "evaluation_id",
            "#index": "index",
        },
        ExpressionAttributeValues={
            ':evaluation_id': {
                'S': evaluation_id,
            },
            ':after': {
                'N': str(after),
            },
        }
    )

    return [
        json.loads(line)
        for item in response['Items']
        for line in item['data']['S'].splitlines()
    ]
