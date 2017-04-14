from __future__ import print_function

from io import BytesIO
from urllib2 import urlopen

import base64
import json
import boto3
import os

COMPARE_FACE_BUCKET = os.environ['COMPARE_FACE_BUCKET']
COMPARE_FACE_KEY = os.environ['COMPARE_FACE_KEY']
MATCH_TOPIC_ARN = os.environ['MATCH_TOPIC_ARN']
region = os.environ['AWS_DEFAULT_REGION']

print('Working in region: ', region)
rekognition = boto3.client("rekognition", region)
sns = boto3.client('sns')

def handler(event, context):
    tweets = []

    for tweet in event:
        if 'image_analysis' in event:
            for label in event['image_analysis']['labels']:
                if "Person" in label.values():
                    image_data = BytesIO(urlopen(label['media_url_https']).read())

                    response = rekognition.compare_faces(
                        SourceImage={
                            'S3Object': {
                                'Bucket': COMPARE_FACE_BUCKET,
                                'Name': COMPARE_FACE_KEY
                            }
                        },
                        TargetImage={
                            'Bytes' : image_data.getvalue()
                        }
                    )
                    print('Match response ', json.dumps(response))
                    if len(response['FaceMatches'])!=0:
                        msg = "Found a match at %s" % label['media_url_https']
                        response = sns.publish(
                            TopicArn=MATCH_TOPIC_ARN,
                            Message=msg,
                            Subject='Found a match on twitter',
                            MessageStructure='string',
                        )
        
        tweets.append(tweet)
    
    return tweets

