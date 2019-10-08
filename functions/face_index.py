import json
import logging
import os

from datadog_lambda.metric import lambda_metric
from datadog_lambda.wrapper import datadog_lambda_wrapper

import boto3

@datadog_lambda_wrapper
def handler(event, context):
    params = json.loads(event['Records'][0]['Sns']['Message'])

    if 'srcBucket' not in params or 'name' not in params:
        logging.error("Validation failed")
        raise Exception("Failed to check image")

    client=boto3.client('rekognition')
    collection_id = os.environ['REKOGNITION_COLLECTION_ID']

    data = client.index_faces(
        CollectionId=collection_id,
        DetectionAttributes=[],
        ExternalImageId= params['userId'],
        Image={
            'S3Object': {
                'Bucket': params['srcBucket'],
                'Name': params['name'],
            }
        }
    )

    response = {
        "statusCode": 200,
        "body": json.dumps(data)
    }

    return response
