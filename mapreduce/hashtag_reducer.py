#!/usr/bin/env python3

import sys
from collections import defaultdict
from operator import itemgetter

def output_top_hashtags(month, hashtag_counts):
    top_hashtags = sorted(hashtag_counts.items(), key=itemgetter(1), reverse=True)[:10]
    print(f"Top 10 hashtags for {month}:")
    for hashtag, count in top_hashtags:
        print(f"#{hashtag}: {count}")
    print("---")

if __name__ == "__main__":
    current_month = None
    hashtag_counts = defaultdict(int)
    
    for line in sys.stdin:
        try:
            month_key, hashtag, count = line.strip().split('\t')
            count = int(count)
            
            if current_month is not None and month_key != current_month:
                output_top_hashtags(current_month, hashtag_counts)
                hashtag_counts = defaultdict(int)
            
            current_month = month_key
            hashtag_counts[hashtag] += count
                
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
    
    if current_month is not None:
        output_top_hashtags(current_month, hashtag_counts)
