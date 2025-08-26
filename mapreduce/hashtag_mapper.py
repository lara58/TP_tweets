#!/usr/bin/env python3

import sys
import json
import datetime

def process_tweet(line):
    if not (line.strip().startswith('{') and line.strip().endswith('}')):
        return
    
    tweet = json.loads(line.strip())
    timestamp = tweet.get("timestamp")
    if not timestamp:
        return
        
    date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    month_key = f"{date.year}-{date.month:02d}"
    
    for hashtag in tweet.get("hashtags", []):
        hashtag = hashtag.lower().strip()
        if hashtag.startswith('#'):
            hashtag = hashtag[1:]
            
        if hashtag:
            print(f"{month_key}\t{hashtag}\t1")

if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip() == '[':
            continue
        try:
            process_tweet(line)
        except Exception as e:
            sys.stderr.write(f"Error: {str(e)}\n")
