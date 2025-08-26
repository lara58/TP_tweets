#!/usr/bin/env python3

import sys
import json
from textblob import TextBlob

def process_tweet(line):
    if not (line.strip().startswith('{') and line.strip().endswith('}')):
        return
        
    tweet = json.loads(line.strip())
    
    location = tweet.get("location", {})
    city = location.get("city", "unknown")
    
    if city == "unknown":
        return
    
    text = tweet.get("tweet_text", "")
    
    sentiment = 0.0
    try:
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
    except:
        pass
    
    print(f"{city}\t{sentiment}")

if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip() == '[':
            continue
        try:
            process_tweet(line)
        except Exception as e:
            sys.stderr.write(f"Error: {str(e)}\n")
