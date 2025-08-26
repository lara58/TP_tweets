#!/usr/bin/env python3

import sys
import json
import datetime
from textblob import TextBlob

def process_mapper_line(line):
    try:
        tweet = json.loads(line)
        
        text = tweet.get("tweet_text", "")
        timestamp = tweet.get("timestamp")
        
        if not text or not timestamp:
            return
            
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity
        
        date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        day_key = f"{date.year}-{date.month:02d}-{date.day:02d}"
        
        print(f"{day_key}\t{sentiment_score}")
        
    except Exception as e:
        sys.stderr.write(f"Error processing line: {e}\n")

def output_daily_sentiment(current_day, daily_sentiment, daily_count):
    average_sentiment = daily_sentiment[current_day] / daily_count[current_day]
    
    sentiment_label = "neutre"
    if average_sentiment > 0.1:
        sentiment_label = "positif"
    elif average_sentiment < -0.1:
        sentiment_label = "négatif"
    
    print(f"{current_day}\t{average_sentiment:.4f}\t{sentiment_label}\t{daily_count[current_day]}")

def process_reducer():
    daily_sentiment = {}
    daily_count = {}
    current_day = None
    
    for line in sys.stdin:
        try:
            day_key, sentiment_score = line.strip().split('\t')
            sentiment_score = float(sentiment_score)
            
            if current_day is not None and day_key != current_day:
                output_daily_sentiment(current_day, daily_sentiment, daily_count)
                daily_sentiment = {}
                daily_count = {}
            
            current_day = day_key
            
            daily_sentiment[day_key] = daily_sentiment.get(day_key, 0) + sentiment_score
            daily_count[day_key] = daily_count.get(day_key, 0) + 1
                
        except Exception as e:
            sys.stderr.write(f"Error reducing line: {e}\n")
    
    if current_day is not None:
        output_daily_sentiment(current_day, daily_sentiment, daily_count)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mapper":
        for line in sys.stdin:
            process_mapper_line(line)
    else:
        process_reducer()
