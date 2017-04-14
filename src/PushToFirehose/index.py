from __future__ import print_function

import base64
import json
import boto3
import botocore.exceptions
import os

print('Loading function')

# get the region name from the environment variable 'AWS_DEFAULT_REGION'
region = os.environ['AWS_DEFAULT_REGION']
print('Working in region: ', region)
firehose = boto3.client('firehose', region)

# get the Delivery Stream name from the ENV Variables
DELIVERY_STREAM_NAME = os.environ['DELIVERY_STREAM_NAME']
print('Delivery Stream name is ', DELIVERY_STREAM_NAME)
    
def handler(event, context):
    for item in event:
        tweet = json.dumps(item)
        print(tweet)
        # Send the processed tweets to the firehose for use in Athena and Quicksight
        firehose.put_record(DeliveryStreamName=DELIVERY_STREAM_NAME,
            Record={
                'Data': tweet
            })
    return 'Successfully processed {} records.'.format(len(event))

