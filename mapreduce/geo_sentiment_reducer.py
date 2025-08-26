#!/usr/bin/env python3

import sys

def output_city_sentiment(city, sentiment_sum, sentiment_count):
    average_sentiment = sentiment_sum / sentiment_count if sentiment_count > 0 else 0
    
    sentiment_label = "neutre"
    if average_sentiment > 0.1:
        sentiment_label = "positif"
    elif average_sentiment < -0.1:
        sentiment_label = "négatif"
    
    print("{0}\t{1:.4f}\t{2}\t{3}".format(city, average_sentiment, sentiment_label, sentiment_count))

def process_cities():
    current_city = None
    sentiment_sum = 0.0
    sentiment_count = 0
    
    for line in sys.stdin:
        try:
            city, sentiment = line.strip().split('\t')
            sentiment = float(sentiment)
            
            if current_city is not None and city != current_city:
                output_city_sentiment(current_city, sentiment_sum, sentiment_count)
                sentiment_sum = 0.0
                sentiment_count = 0
            
            current_city = city
            sentiment_sum += sentiment
            sentiment_count += 1
                
        except Exception as e:
            sys.stderr.write("Error reducing line: {0}\n".format(e))
    
    if current_city is not None:
        output_city_sentiment(current_city, sentiment_sum, sentiment_count)

if __name__ == "__main__":
    process_cities()
