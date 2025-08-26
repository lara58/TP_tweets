#!/usr/bin/env python3

import sys
import json
import re
from collections import defaultdict

def process_mapper_line(line):
    try:
        tweet = json.loads(line)
        
        location = tweet.get("location", {})
        city = location.get("city", "unknown")
        
        if city == "unknown":
            return
            
        text = tweet.get("tweet_text", "")
        hashtags = tweet.get("hashtags", [])
        
        print(f"{city}\t{text}\t{','.join(hashtags)}")
        
    except Exception as e:
        sys.stderr.write(f"Error processing line: {e}\n")

def output_region_analysis(current_region, region_tweets, region_hashtags):
    tweet_count = len(region_tweets[current_region])
    
    top_hashtags = sorted(region_hashtags[current_region].items(), 
                          key=lambda x: x[1], reverse=True)[:5]
    
    words = []
    for tweet in region_tweets[current_region]:
        clean_text = re.sub(r'#\w+|http\S+', '', tweet.lower())
        words.extend(re.findall(r'\b[a-z]{3,}\b', clean_text))
        
    word_counts = defaultdict(int)
    for word in words:
        word_counts[word] += 1
        
    stop_words = {"the", "and", "for", "that", "this", "with", "from", "was", "are", "you", "have", "your"}
    top_words = [(word, count) for word, count in 
                 sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                 if word not in stop_words][:10]
    
    print(f"Région: {current_region}")
    print(f"Nombre de tweets: {tweet_count}")
    
    print("Top hashtags:")
    for hashtag, count in top_hashtags:
        print(f"  #{hashtag}: {count}")
        
    print("Top mots-clés:")
    for word, count in top_words:
        print(f"  {word}: {count}")
        
    print("---")

def process_reducer():
    region_tweets = defaultdict(list)
    region_hashtags = defaultdict(lambda: defaultdict(int))
    current_region = None
    
    for line in sys.stdin:
        try:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue
                
            region, text, hashtags_str = parts
            hashtags = hashtags_str.split(',') if hashtags_str else []
            
            if current_region is not None and region != current_region:
                output_region_analysis(current_region, region_tweets, region_hashtags)
                region_tweets = defaultdict(list)
                region_hashtags = defaultdict(lambda: defaultdict(int))
            
            current_region = region
            
            region_tweets[region].append(text)
            
            for hashtag in hashtags:
                if hashtag:
                    hashtag = hashtag.lower().strip()
                    if hashtag.startswith('#'):
                        hashtag = hashtag[1:]
                    if hashtag:
                        region_hashtags[region][hashtag] += 1
                
        except Exception as e:
            sys.stderr.write(f"Error reducing line: {e}\n")
    
    if current_region is not None:
        output_region_analysis(current_region, region_tweets, region_hashtags)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mapper":
        for line in sys.stdin:
            process_mapper_line(line)
    else:
        process_reducer()
