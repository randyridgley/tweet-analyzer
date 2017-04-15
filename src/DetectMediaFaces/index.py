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
print('Working in region: ', region)
rekognition = boto3.client("rekognition", region)

def detect_faces(image, attributes=['ALL']):
	response = rekognition.detect_faces(
        Image={'Bytes': image}, 
        Attributes=attributes)
	return response['FaceDetails']

def handler(event, context):
    tweets = []

    for tweet in event:
        people = []
        people_count = 0

        if 'image_analysis_labels' in tweet:
            for label in tweet['image_analysis_labels']:
                if "Person" in label.values():
                    people_count +=1
                    image_data = BytesIO(urlopen(label['media_url_https']).read())
                    person = {}
                    for face in detect_faces(image_data.getvalue()):
                        #store details
                        print(json.dumps(face))
                        person['BoundingBox'] = face['BoundingBox']
                        if 'Smile' in face:
                            person['Smile'] = face['Smile']['Confidence']
                        if 'Gender' in face:
                            person['Gender'] = face['Gender']['Value']
                        if 'AgeRange' in face:
                            person['AgeRange'] = face['AgeRange']
                        if 'Emotions' in face:
                            emotions = []

                            for e in face['Emotions']:
                                emotions.append(e)
                            
                            person['emotions'] = emotions
                        people.append(person)
            tweet['image_analysis_people'] = people
            tweet['image_analysis_people_count'] = people_count
        
        tweets.append(tweet)
    return tweets

