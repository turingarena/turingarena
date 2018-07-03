import json
import time

import boto3

dynamodb = boto3.client("dynamodb")


def store_event(evaluation_id, index, data):
    dynamodb.put_item(
        TableName='EvaluationEventsTable',
        Item={
            'evaluation_id': {
                'S': evaluation_id,
            },
            'index': {
                'N': str(index),
            },
            'data': {
                'S': data,
            },
            'expires': {
                'N': str(int(time.time() + 10 * 60)),
            },
        },
    )


def store_events(evaluation_id, events):
    i = -1
    for i, e in enumerate(events):
        store_event(evaluation_id, i, str(e) + "\n")
    store_event(evaluation_id, i + 1, json.dumps("EOS") + "\n")


def load_event_page(evaluation_id, after):
    dynamodb = boto3.client("dynamodb")

    if after is None:
        after_index = -1
    else:
        after_index = after

    limit = 100
    response = dynamodb.query(
        TableName='EvaluationEventsTable',
        Limit=limit,
        ConsistentRead=False,
        KeyConditionExpression='#evaluation_id = :evaluation_id AND #index > :after',
        ExpressionAttributeNames={
            '#evaluation_id': "evaluation_id",
            "#index": "index",
        },
        ExpressionAttributeValues={
            ':evaluation_id': {
                'S': evaluation_id,
            },
            ':after': {
                'N': str(after_index),
            },
        }
    )

    data = [
        json.loads(line)
        for item in response['Items']
        for line in item['data']['S'].splitlines()
    ]

    last = False
    if data and data[-1] == "EOS":
        data = data[:-1]
        last = True

    if after is None:
        begin = None
    else:
        begin = str(after)

    if last:
        end = None
    elif after is None:
        end = str(len(data) - 1)
    else:
        end = str(after + len(data))

    return dict(
        data=data,
        begin=begin,
        end=end,
    )
