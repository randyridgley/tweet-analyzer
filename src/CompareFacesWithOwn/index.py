from __future__ import print_function

import base64
import json
import boto3
import botocore.session
import botocore.exceptions
import os


# get the Delivery Stream name from the ENV Variables
DELIVERY_STREAM_NAME = os.environ['DELIVERY_STREAM_NAME']
print('Delivery Stream name is ', DELIVERY_STREAM_NAME)

COMPARE_FACE_BUCKET = os.environ['COMPARE_FACE_BUCKET']
COMPARE_FACE_KEY = os.environ['COMPARE_FACE_KEY']
SIMILARITY_THRESHOLD = os.environ['SIMILARITY_THRESHOLD']
MATCH_TOPIC_ARN = os.environ['MATCH_TOPIC_ARN']

print('Working in region: ', region)
rekognition = boto3.client("rekognition", region)
sns = boto3.client('sns')

def handler(event, context):
    for label in event['labels']:
        if "Person" in label.values():
            image_data = BytesIO(urlopen(label['media_url_https']).read())

            response = rekognition.compare_faces(
                SourceImage={
                    'S3Object': {
                        'Bucket': COMPARE_FACE_BUCKET,
                        'Name': COMPARE_FACE_KEY
                    }
                },
                Bytes=image_data.getvalue(),
                SimilarityThreshold=SIMILARITY_THRESHOLD
            )

            if len(response['FaceMatches'])!=0:
                msg = "Found a match at %s" % label['media_url_https']
                response = client.publish(
                    TopicArn=MATCH_TOPIC_ARN,
                    Message=msg,
                    Subject='Found a match on twitter',
                    MessageStructure='string',
                )
    
    return json.dumps(event)

