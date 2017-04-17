from __future__ import print_function

import base64
import json
import boto3
import botocore.exceptions
import os
import decimal
import sys

print('Loading function')

# get the region name from the environment variable 'AWS_DEFAULT_REGION'
region = os.environ['AWS_DEFAULT_REGION']
print('Working in region: ', region)
firehose = boto3.client('firehose', region)
dynamodb = boto3.resource('dynamodb', region)

# get the Delivery Stream name from the ENV Variables
DELIVERY_STREAM_NAME = os.environ['DELIVERY_STREAM_NAME']
print('Delivery Stream name is ', DELIVERY_STREAM_NAME)
    
def handler(event, context):
    try:
        # depending how the message comes in you might need to pull the tweets from a nested source
        if 'tweets' in event:
            items = event['tweets']
        else:
            items = event
            
        table = dynamodb.Table(DYNAMODB_SENTIMENT_TABLE)
        with table.batch_writer() as batch:
            for item in items:
                tweet = json.dumps(item) + '\n'
                
                print(tweet)
                # Send the processed tweets to the firehose for use in Athena and Quicksight
                firehose.put_record(DeliveryStreamName=DELIVERY_STREAM_NAME,
                    Record={
                        'Data': bytes(tweet)
                    })

                # If tweet has coordinates throw it in DynamoDB
                if 'place_coordinates' in tweet:
                    coordinates = item['place_coordinates'][0][0]
                    latitude = coordinates[1]
                    longitude = coordinates[0]
                    # send portion of data to dynamo db to query with api gateway
                    batch.put_item(
                        Item={
                            'id': item['id'],
                            'sentiment': item['text_analysis_sentiment'],
                            'sentiment_value': str(item['text_analysis_sentiment_value']),
                            'text': item['text'],
                            'screen_name': item['screen_name'],
                            'timestamp': item['timestamp_ms'],
                            'latitude' : str(latitude),
                            'longitude': str(longitude)
                        }
                    )
   
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e), e)
        
    return 'Successfully processed {} records.'.format(len(event))

