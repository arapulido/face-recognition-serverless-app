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

    rekognition_client = boto3.client('rekognition')
    sns_client = boto3.client('sns')

    collection_id = os.environ['REKOGNITION_COLLECTION_ID']

    data = rekognition_client.index_faces(
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

    params['faceId'] = data['FaceRecords'][0]['Face']['FaceId']
    sns_client.publish(
        TopicArn=os.environ['FACE_DETECTION_PERSIST_TOPIC'],
        Message=json.dumps(params))

    response = {
        "statusCode": 200,
        "body": json.dumps(data)
    }

    return response
