import json
import logging
import requests
import os

from datadog_lambda.metric import lambda_metric
from datadog_lambda.wrapper import datadog_lambda_wrapper
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

import boto3

# Set logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

@datadog_lambda_wrapper
def handler(event, context):
    patch_all()
    params = json.loads(event['body'])

    if 'srcBucket' not in params or 'name' not in params:
        logger.error("Validation failed. Missing parameters")
        raise Exception("Missing parameters")

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

    if len(data['FaceDetails']) < 1:
        # Count image without faces
        lambda_metric(
            "face_recognition.images_without_faces",
            1,
            tags=['bucket:'+params['srcBucket'],
            'image_name:'+params['name']]
        )
        logger.info('Uploaded an image without faces: %s', params['name'])

        body = {"RekognitionCode": "NoFace",
            "ImageName": params['name']}

        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

        return response

    if len(data['FaceDetails']) > 1:
        # Count image with more than 1 face
        lambda_metric(
            "face_recognition.images_with_multiple_faces",
            1,
            tags=['bucket:'+params['srcBucket'],
            'image_name:'+params['name']]
        )
        logger.info('Uploaded an image more than 1 face: %s', params['name'])

        body = {"RekognitionCode": "MultipleFace",
            "ImageName": params['name']}

        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }

        return response

    search_endpoint = os.environ['FACE_SEARCH_ENDPOINT']

    if search_endpoint == 'ENDPOINT_NOT_SET':
        logger.error('FACE_SEARCH_ENDPOINT is not correctly set')
        raise Exception('Redeploy the application with the correct --face-search-endpoint parameter')

    response = requests.post(search_endpoint, event['body'])

    if response.status_code != 200:
        raise Exception

    body = json.loads(response.text)

    # If it was the first time that we had seen that face, index it
    if 'RekognitionCode' not in body:
        sns_client.publish(
            TopicArn=os.environ['FACE_DETECTION_INDEX_TOPIC'],
            Message=json.dumps(params))

    response = {
        "statusCode": 200,
        "body": response.text
    }

    return response
