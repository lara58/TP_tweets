#!/usr/bin/env python3

import sys
import json
import datetime

def process_tweet(tweet):
    """
    Traite un objet tweet et émet les paires (mois-hashtag, 1)
    """
    timestamp = tweet.get("timestamp")
    if not timestamp:
        return
        
    date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    month_key = "{0}-{1:02d}".format(date.year, date.month)
    
    for hashtag in tweet.get("hashtags", []):
        hashtag = hashtag.lower().strip()
        if hashtag.startswith('#'):
            hashtag = hashtag[1:]
            
        if hashtag:
            print("{0}\t{1}\t1".format(month_key, hashtag))

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
