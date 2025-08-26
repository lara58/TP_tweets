#!/usr/bin/env python3

import json
import sys
from collections import defaultdict
from operator import itemgetter

def map_phase(tweets):
    """Phase Map : extrait les hashtags des tweets."""
    result = []
    for tweet in tweets:
        timestamp = tweet.get("timestamp", "")
        if not timestamp:
            continue
            
        # Format : YYYY-MM
        month = timestamp[:7]
        
        hashtags = tweet.get("hashtags", [])
        for hashtag in hashtags:
            # Normaliser les hashtags
            hashtag = hashtag.lower().strip()
            if hashtag.startswith('#'):
                hashtag = hashtag[1:]
            if hashtag:
                # Émettre (mois-hashtag, 1)
                result.append((f"{month}-{hashtag}", 1))
    
    return result

def shuffle_sort_phase(mapped_data):
    """Phase Shuffle & Sort : regroupe les clés identiques."""
    result = defaultdict(int)
    for key, value in mapped_data:
        result[key] += value
    return result

def reduce_phase(shuffled_data):
    """Phase Reduce : compte les occurrences de hashtags par mois."""
    # Regrouper par mois
    months = defaultdict(dict)
    for key, count in shuffled_data.items():
        month, hashtag = key.split('-', 1)
        if hashtag in months[month]:
            months[month][hashtag] += count
        else:
            months[month][hashtag] = count
    
    # Calculer le top 10 pour chaque mois
    result = {}
    for month, hashtags in months.items():
        top_hashtags = sorted(hashtags.items(), key=itemgetter(1), reverse=True)[:10]
        result[month] = top_hashtags
    
    return result

def main():
    """Exécute le processus MapReduce complet."""
    print("Simulation de MapReduce pour l'analyse des hashtags")
    print("==================================================")
    
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
    print("\nPhase Map : extraction des hashtags...")
    mapped_data = map_phase(tweets)
    print(f"Paires (clé, valeur) émises : {len(mapped_data)}")
    
    # Phase Shuffle & Sort
    print("\nPhase Shuffle & Sort : regroupement par clé...")
    shuffled_data = shuffle_sort_phase(mapped_data)
    print(f"Clés uniques après regroupement : {len(shuffled_data)}")
    
    # Phase Reduce
    print("\nPhase Reduce : comptage des hashtags par mois...")
    reduced_data = reduce_phase(shuffled_data)
    
    # Afficher les résultats
    print("\nRésultats de l'analyse :")
    for month, top_hashtags in reduced_data.items():
        print(f"\nTop 10 hashtags pour {month} :")
        for hashtag, count in top_hashtags:
            print(f"  #{hashtag}: {count}")
    
    print("\nSimulation MapReduce terminée !")

if __name__ == "__main__":
    main()
