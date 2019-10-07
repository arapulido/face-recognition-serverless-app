import json
import logging
import requests

from datadog_lambda.metric import lambda_metric
from datadog_lambda.wrapper import datadog_lambda_wrapper

import boto3

def handler(event, context):
    params = json.loads(event['body'])

    if 'srcBucket' not in params or 'name' not in params:
        logging.error("Validation failed")
        raise Exception("Failed to check image")

    client=boto3.client('rekognition')

    data = client.detect_faces(
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

    response = requests.post('https://llcjf8qym2.execute-api.us-east-1.amazonaws.com/dev/search-faces', event['body'])    

    if response.status_code != 200:
        raise Exception
    
    response = {
        "statusCode": 200,
        "body": response.text
    }

    return response
