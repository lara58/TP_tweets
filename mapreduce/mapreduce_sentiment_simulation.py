#!/usr/bin/env python3

import json
import sys
from collections import defaultdict
from textblob import TextBlob

def map_phase(tweets):
    """Phase Map : extrait les sentiments des tweets par région."""
    result = []
    for tweet in tweets:
        location = tweet.get("location", {})
        city = location.get("city", "unknown")
        
        if city == "unknown":
            continue
            
        text = tweet.get("tweet_text", "")
        
        # Analyse du sentiment avec TextBlob
        sentiment = 0.0
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
        except:
            pass
        
        # Émettre (ville, sentiment)
        result.append((city, sentiment))
    
    return result

def shuffle_sort_phase(mapped_data):
    """Phase Shuffle & Sort : regroupe les sentiments par région."""
    regions = defaultdict(list)
    for city, sentiment in mapped_data:
        regions[city].append(sentiment)
    return regions

def reduce_phase(shuffled_data):
    """Phase Reduce : calcule le sentiment moyen par région."""
    result = {}
    for city, sentiments in shuffled_data.items():
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Déterminer le sentiment global
        sentiment_label = "neutre"
        if avg_sentiment > 0.1:
            sentiment_label = "positif"
        elif avg_sentiment < -0.1:
            sentiment_label = "négatif"
            
        result[city] = (avg_sentiment, sentiment_label, len(sentiments))
    
    return result

def main():
    """Exécute le processus MapReduce complet pour l'analyse des sentiments par région."""
    print("Simulation de MapReduce pour l'analyse des sentiments par région")
    print("==============================================================")
    
    # Charger les tweets
    print("Chargement des tweets...")
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_path = os.path.join(project_dir, "data", "tweets_with_locations.json")
    with open(data_path, 'r', encoding='utf-8') as file:
        tweets = json.load(file)
    
    print(f"Nombre de tweets chargés : {len(tweets)}")
    
    # Phase Map
    print("\nPhase Map : extraction des sentiments...")
    mapped_data = map_phase(tweets)
    print(f"Paires (clé, valeur) émises : {len(mapped_data)}")
    
    # Phase Shuffle & Sort
    print("\nPhase Shuffle & Sort : regroupement par région...")
    shuffled_data = shuffle_sort_phase(mapped_data)
    print(f"Régions uniques après regroupement : {len(shuffled_data)}")
    
    # Phase Reduce
    print("\nPhase Reduce : calcul du sentiment moyen par région...")
    reduced_data = reduce_phase(shuffled_data)
    
    # Afficher les résultats
    print("\nRésultats de l'analyse :")
    for city, (sentiment, label, count) in sorted(reduced_data.items()):
        print(f"{city}: {sentiment:.4f} ({label}) - {count} tweets")
    
    print("\nSimulation MapReduce terminée !")

if __name__ == "__main__":
    main()
