import json
import logging
import os

from datadog_lambda.metric import lambda_metric
from datadog_lambda.wrapper import datadog_lambda_wrapper
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

import boto3

@datadog_lambda_wrapper
def handler(event, context):
    patch_all()
    params = json.loads(event['Records'][0]['Sns']['Message'])

    if 'srcBucket' not in params or 'name' not in params:
        logging.error("Validation failed")
        raise Exception("Failed to check image")

    dynamodb_client = boto3.client('dynamodb')

    dynamodb_item = {}
    for param in params:
        if param == 'userId':
            dynamodb_item['Username'] = {'S': params[param]}
        else:
            dynamodb_item[param] = {'S': params[param]}

    data = dynamodb_client.put_item(
        TableName=os.environ['FACE_DETECTION_DDB_TABLE'],
        Item=dynamodb_item,
        ConditionExpression='attribute_not_exists(Username)'
    )

    response = {
        "statusCode": 200,
        "body": json.dumps(data)
    }

    return response
