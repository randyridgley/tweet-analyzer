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
    people = {}
    for label in event['labels']:
        if "Person" in label.values():
            image_data = BytesIO(urlopen(label['media_url_https']).read())
            print "{Name} - {Confidence}%".format(**label)
            person = {}
            for face in detect_faces(image_data.getvalue()):
                print "Face ({Confidence}%)".format(**face)
                #store details
                if 'Smile' in face:
                    person['Smile'] = face['Smile']['Value']
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
    event['people'] = people
    return json.dumps(event)

