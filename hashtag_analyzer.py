#!/usr/bin/env python3

import sys
import json
import datetime
from operator import itemgetter

def process_mapper_line(line):
    try:
        tweet = json.loads(line)
        
        timestamp = tweet.get("timestamp")
        if not timestamp:
            return
            
        date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        month_key = f"{date.year}-{date.month:02d}"
        
        hashtags = tweet.get("hashtags", [])
        
        for hashtag in hashtags:
            hashtag = hashtag.lower().strip()
            if hashtag.startswith('#'):
                hashtag = hashtag[1:]
                
            if hashtag:
                print(f"{month_key}\t{hashtag}\t1")
                
    except Exception as e:
        sys.stderr.write(f"Error processing line: {e}\n")

def output_top_hashtags(current_month, hashtag_counts):
    top_hashtags = sorted(hashtag_counts.items(), key=itemgetter(1), reverse=True)[:10]
    
    print(f"Top 10 hashtags for {current_month}:")
    for hashtag, count in top_hashtags:
        print(f"{hashtag}: {count}")
    print("---")

def process_reducer():
    hashtag_counts = {}
    current_month = None
    
    for line in sys.stdin:
        try:
            month_key, hashtag, count = line.strip().split('\t')
            count = int(count)
            
            if current_month is not None and month_key != current_month:
                output_top_hashtags(current_month, hashtag_counts)
                hashtag_counts = {}
            
            current_month = month_key
            
            hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + count
                
        except Exception as e:
            sys.stderr.write(f"Error reducing line: {e}\n")
    
    if current_month is not None:
        output_top_hashtags(current_month, hashtag_counts)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mapper":
        for line in sys.stdin:
            process_mapper_line(line)
    else:
        process_reducer()
