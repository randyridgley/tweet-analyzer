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
labels = int(os.environ['MAX_LABELS'])
print('Max Labels=', labels)
confidence = int(os.environ['MIN_CONFIDENCE'])
print('Confidence=', confidence)
print('Working in region: ', region)
rekognition = boto3.client("rekognition", region)
    
def detect_labels(image):
    response = rekognition.detect_labels(
		Image={'Bytes': image},
		MaxLabels=labels,
		MinConfidence=confidence,
	)
    return response['Labels']

def handler(event, context):
    tweets = []
    response = {}

    for tweet in event:
        if 'media' in tweet:
            labels = []
            tweet['hasPerson'] = False
            response['hasPerson'] = False
            for media in tweet['media']:
                if media['type'] == 'photo':
                    image_data = BytesIO(urlopen(media['media_url_https']).read())

                    for label in detect_labels(image_data.getvalue()):
                        if "Person" in label.values() or "People" in label.values():
                            tweet['hasPerson'] = True
                            response['hasPerson'] = True

                        label['media_url_https'] = media['media_url_https']
                        print(label)
                        labels.append(label)
            tweet['image_analysis'] = {}
            tweet['image_analysis']['labels'] = labels
            tweets.append(tweet)
    response['tweets'] = tweets
    print(json.dumps(response))
    return response

