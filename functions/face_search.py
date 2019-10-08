import json
import logging
import os
from datadog_lambda.metric import lambda_metric
from datadog_lambda.wrapper import datadog_lambda_wrapper

import boto3

@datadog_lambda_wrapper
def handler(event, context):
    params = json.loads(event['body'])

    if 'srcBucket' not in params or 'name' not in params:
        logging.error("Validation failed")
        raise Exception("Failed to check image")

    client=boto3.client('rekognition')
    collection_id = os.environ['REKOGNITION_COLLECTION_ID']

    data = client.search_faces_by_image(
        CollectionId=collection_id,
        Image={
            'S3Object': {
                'Bucket': params['srcBucket'],
                'Name': params['name'],
            }
        },
        FaceMatchThreshold=70.0,
        MaxFaces=3,
    )

    if len(data['FaceMatches']) > 0:
        raise Exception

    response = {
        "statusCode": 200,
        "body": json.dumps(data)
    }

    return response
