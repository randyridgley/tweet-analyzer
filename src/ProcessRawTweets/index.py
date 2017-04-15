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
    tweets = []
    count = 0

    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        payload = base64.b64decode(record['kinesis']['data'])
        print("Decoded payload: " + payload)
        tweet = json.loads(payload)

        if not tweet.has_key('text'):
            continue
        
        try:
            data = {}
            data['text'] = tweet['text']
            data['created_at'] = tweet['created_at']
            data['screen_name'] = tweet['user']['screen_name']
            data['id'] = tweet['id_str']
            data['place_country_code'] = tweet['place']['country_code']
            data['place_coordinates'] = tweet['place']['bounding_box']['coordinates']
            data['place_full_name'] = tweet['place']['full_name']
            data['verified'] = tweet['user']['verified']

            if tweet['entities'].has_key('hashtags'):
                data['hashtags'] = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
                
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
            
            tweets.append(data)
            count += 1

            if count >= 20:
                sf_payload = json.dumps(tweets)
                print(sf_payload)
                sf.start_execution(
                    stateMachineArn=os.environ['STATE_MACHINE_ARN'],
                    input=sf_payload,
                )     
                tweets = []
                count = 0

            # Send the raw tweets to the firehose for historical storage of tweet for ad-hoc querying later
            print("Sending Record to firehose")
            firehose.put_record(DeliveryStreamName=DELIVERY_STREAM_NAME,
                Record={
                    'Data': payload
                })
        except:
            print(e)
            pass

    if tweets:
        print('starting state machine for tweets.')
        print(tweets)
        sf_payload = json.dumps(tweets)
        print(sf_payload)
        sf.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=sf_payload,
        )        
    return 'Successfully processed {} records.'.format(len(event['Records']))

