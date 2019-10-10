import json
import logging
import requests
import os

from datadog_lambda.metric import lambda_metric
from datadog_lambda.wrapper import datadog_lambda_wrapper
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

import boto3

@datadog_lambda_wrapper
def handler(event, context):
    patch_all()
    params = json.loads(event['body'])

    if 'srcBucket' not in params or 'name' not in params:
        logging.error("Validation failed")
        raise Exception("Failed to check image")

    rekognition_client = boto3.client('rekognition')
    sns_client = boto3.client('sns')

    data = rekognition_client.detect_faces(
        Image={
            'S3Object': {
                'Bucket': params['srcBucket'],
                'Name': params['name'],
            }
        },
        Attributes=['ALL']
    )

    if len(data['FaceDetails']) != 1:
        raise Exception

    search_endpoint = os.environ['FACE_SEARCH_ENDPOINT']

    if search_endpoint == 'ENDPOINT_NOT_SET':
        raise Exception('Redeploy the application with the correct --face-search-endpoint parameter')

    response = requests.post(search_endpoint, event['body'])

    if response.status_code != 200:
        raise Exception

    sns_client.publish(
        TopicArn=os.environ['FACE_DETECTION_INDEX_TOPIC'],
        Message=json.dumps(params))

    response = {
        "statusCode": 200,
        "body": response.text
    }

    return response
