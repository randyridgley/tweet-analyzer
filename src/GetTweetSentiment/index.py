from __future__ import print_function

import base64
import json
import boto3
import os

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

print('Loading function')
    
def handler(event, context):
    sid = SentimentIntensityAnalyzer()
    text = event['text']
    sentiment_value = sid.polarity_scores(text)['compound']
    print('sentiment value: ' + sentiment_value)
    if float(sentiment_value) < 0.0:
        sentiment = "neg"
    elif float(sentiment_value) >= 0.0:
        sentiment = "pos"
    print(text + ","  + sentiment + "," + sentiment_value)
    event['sentiment'] = sentiment
    event['sentimentValue'] = sentiment_value

    
    return json.dumps(event)

