from __future__ import print_function

import base64
import json
import boto3
from io import BytesIO
from urllib2 import urlopen
import os

print('Loading function')

# get the region name from the environment variable 'AWS_DEFAULT_REGION'
region = os.environ['AWS_DEFAULT_REGION']
labels = os.environ['MAX_LABELS']
confidence = os.environ['MIN_CONFIDENCE']

print('Working in region: ', region)
rekognition = boto3.client("rekognition", region)
    
def detect_labels(image, max_labels=10, min_confidence=95):
    response = rekognition.detect_labels(
		Image={'Bytes': image},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
	)
    return response['Labels']

def handler(event, context):
    tweet = json.loads(event)
    for media in tweet['entities']['media']:
        image_data = BytesIO(urlopen(tweet['media_url_https']).read())

        labels = {}
        for label in detect_labels(image_data.getvalue(), labels, confidence):
            label['media_url_https'] = tweet['media_url_https']
            labels.append(label)

        event['labels'] = labels
    return json.dumps(tweet)

