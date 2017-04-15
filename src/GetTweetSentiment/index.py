from __future__ import print_function

import base64
import json
import urllib

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

print('Loading function')
    
def handler(event, context):
    print(event)
    tweets = []
    for tweet in event:
        sid = SentimentIntensityAnalyzer()
        text = tweet['text']
        sentiment_value = sid.polarity_scores(text)['compound']
        print(sentiment_value)
        if float(sentiment_value) < 0.0:
            sentiment = "negative"
        elif float(sentiment_value) > 0.0:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        tweet['text_analysis'] = {}
        tweet['text_analysis']['sentiment'] = sentiment
        tweet['text_analysis']['sentimentValue'] = sentiment_value    
        tweets.append(tweet)

    return tweets

