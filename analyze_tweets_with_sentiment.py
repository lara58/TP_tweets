import json
import re
from collections import defaultdict
from textblob import TextBlob

def analyze_hashtags(tweets):
    """Analyse les tendances des hashtags dans les tweets."""
    hashtag_counts = defaultdict(int)
    
    for tweet in tweets:
        hashtags = tweet.get("hashtags", [])
        for hashtag in hashtags:
            # Normaliser les hashtags
            hashtag = hashtag.lower().strip()
            if hashtag.startswith('#'):
                hashtag = hashtag[1:]
            if hashtag:
                hashtag_counts[hashtag] += 1
    
    # Trouver les 10 hashtags les plus populaires
    top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("Top 10 hashtags:")
    for hashtag, count in top_hashtags:
        print(f"#{hashtag}: {count}")
    
    return top_hashtags

def analyze_sentiment(tweets):
    """Analyse le sentiment des tweets et calcule le score moyen par jour."""
    daily_sentiment = defaultdict(list)
    
    print("\nAnalyse des sentiments des tweets...")
    for tweet in tweets:
        text = tweet.get("tweet_text", "")
        timestamp = tweet.get("timestamp", "")
        
        if not text or not timestamp:
            continue
            
        # Extraction de la date
        date = timestamp.split()[0]
        
        # Analyse du sentiment avec TextBlob
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity  # -1 (négatif) à +1 (positif)
        
        # Stockage du score par jour
        daily_sentiment[date].append(sentiment_score)
    
    # Calcul des moyennes quotidiennes
    daily_averages = {}
    for day, scores in daily_sentiment.items():
        average = sum(scores) / len(scores)
        daily_averages[day] = average
    
    # Affichage des résultats
    print("\nScore de sentiment moyen par jour:")
    for day, score in sorted(daily_averages.items()):
        sentiment_label = "neutre"
        if score > 0.1:
            sentiment_label = "positif"
        elif score < -0.1:
            sentiment_label = "négatif"
        print(f"{day}: {score:.4f} ({sentiment_label})")
    
    return daily_averages

def analyze_geo_distribution(tweets):
    """Analyse la distribution géographique des tweets et les thèmes par région."""
    regions = defaultdict(list)
    region_hashtags = defaultdict(lambda: defaultdict(int))
    
    for tweet in tweets:
        location = tweet.get("location", {})
        city = location.get("city", "unknown")
        
        if city == "unknown":
            continue
            
        # Stocker le tweet par région
        regions[city].append(tweet)
        
        # Compter les hashtags par région
        hashtags = tweet.get("hashtags", [])
        for hashtag in hashtags:
            hashtag = hashtag.lower().strip()
            if hashtag.startswith('#'):
                hashtag = hashtag[1:]
            if hashtag:
                region_hashtags[city][hashtag] += 1
    
    print("\nDistribution géographique des tweets:")
    for city, city_tweets in regions.items():
        print(f"\nRégion: {city}")
        print(f"Nombre de tweets: {len(city_tweets)}")
        
        # Top hashtags de la région
        top_hashtags = sorted(region_hashtags[city].items(), 
                            key=lambda x: x[1], reverse=True)[:5]
        
        print("Top hashtags:")
        for hashtag, count in top_hashtags:
            print(f"  #{hashtag}: {count}")
        
        # Extraction des mots-clés fréquents
        words = []
        for tweet in city_tweets:
            text = tweet.get("tweet_text", "")
            # Suppression des hashtags et des liens
            clean_text = re.sub(r'#\w+|http\S+', '', text.lower())
            words.extend(re.findall(r'\b[a-z]{3,}\b', clean_text))
            
        # Comptage des mots
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word] += 1
            
        # Top 5 mots-clés (en excluant les mots courants)
        stop_words = {"the", "and", "for", "that", "this", "with", "from", "was", "are", "you", "have", "your"}
        top_words = [(word, count) for word, count in 
                    sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                    if word not in stop_words][:5]
        
        print("Top mots-clés:")
        for word, count in top_words:
            print(f"  {word}: {count}")
    
    return regions

def main():
    # Charger le fichier de tweets
    print("Lecture du fichier de tweets...")
    with open("data/tweets_with_locations.json", 'r', encoding='utf-8') as file:
        tweets = json.load(file)
    
    print(f"Nombre de tweets: {len(tweets)}")
    
    # 1. Analyse des hashtags
    print("\n=== ANALYSE DES TENDANCES DE HASHTAGS ===")
    top_hashtags = analyze_hashtags(tweets)
    
    # 2. Analyse des sentiments
    print("\n=== ANALYSE DES SENTIMENTS ===")
    daily_sentiment = analyze_sentiment(tweets)
    
    # 3. Analyse de la distribution géographique
    print("\n=== ANALYSE DE LA DISTRIBUTION GÉOGRAPHIQUE ===")
    regions = analyze_geo_distribution(tweets)
    
    print("\nAnalyses terminées !")

if __name__ == "__main__":
    main()
