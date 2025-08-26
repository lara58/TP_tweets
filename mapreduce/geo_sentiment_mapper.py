#!/usr/bin/env python3

import sys
import json
from textblob import TextBlob

def process_tweet(tweet):
    """
    Traite un objet tweet et émet les paires (ville, sentiment)
    """
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
    
    print("{0}\t{1}".format(city, sentiment))

if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line or line == '[' or line == ']':
            continue
            
        # Supprimer les virgules à la fin (pour les éléments du tableau)
        if line.endswith(','):
            line = line[:-1]
            
        try:
            # Essayer de parser la ligne comme un objet JSON
            tweet = json.loads(line)
            process_tweet(tweet)
        except Exception as e:
            sys.stderr.write("Error processing line: {0}\nError: {1}\n".format(line[:50], str(e)))
