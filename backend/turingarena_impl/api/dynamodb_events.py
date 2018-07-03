import time

import boto3


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
