from __future__ import print_function

import base64
import json
import boto3
import botocore.session
import botocore.exceptions
import os

print('Loading function')

# get the region name from the environment variable 'AWS_DEFAULT_REGION'
region = os.environ['AWS_DEFAULT_REGION']
print('Working in region: ', region)
firehose = boto3.client('firehose', region)
s3_client = boto3.client('s3', region)
sf = boto3.client("stepfunctions", region)

# get the Delivery Stream name from the ENV Variables
DELIVERY_STREAM_NAME = os.environ['DELIVERY_STREAM_NAME']
print('Delivery Stream name is ', DELIVERY_STREAM_NAME)
    
def handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record['kinesis']['data'])
        print("Decoded payload: " + payload)
        tweet = json.loads(payload)
        data = {}
        data['text'] = tweet['text']
        data['created_at'] = tweet['created_at']
        data['screen_name'] = tweet['user']['screen_name']
        data['id'] = tweet['id_str']
        data['place'] = tweet['place']
        data['verified'] = tweet['user']['verified']

        if tweet['entities'].has_key('hashtags'):
            data['hashtags'] = tweet['entities']['hashtags']
            
        data['timestamp_ms'] = tweet['timestamp_ms']
        data['lang'] = tweet['lang']

        images = []
        if 'entities' in tweet and 'media' in tweet['entities']:
            for media in  tweet['entities']['media']:
                image = {}
                image['media_url_https'] = media['media_url_https']
                image['id'] = media['id']
                image['type'] = media['type']
                image['url'] = media['url']
                images.append(image)

        data['media'] = images
        
        if images.count > 0:
            sf_payload = json.dumps(data)
            sf.start_execution(
                stateMachineArn=os.environ['STATE_MACHINE_ARN'],
                input=sf_payload,
            )

        # Send the raw tweets to the firehose for historical storage of tweet for ad-hoc querying later
        firehose.put_record(DeliveryStreamName=DELIVERY_STREAM_NAME,
            Record={
                'Data': payload
            })
    return data

