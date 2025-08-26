import json
import re
from collections import defaultdict
from textblob import TextBlob

# Constantes
STOP_WORDS = {"the", "and", "for", "that", "this", "with", "from", "was", "are", "you", "have", "your"}
DATA_PATH = "data/tweets_with_locations.json"
SENTIMENT_THRESHOLD = 0.1

def normalize_hashtag(hashtag):
    """Normalise un hashtag en le mettant en minuscules et en supprimant le # initial."""
    hashtag = hashtag.lower().strip()
    return hashtag[1:] if hashtag.startswith('#') else hashtag

def analyze_hashtags(tweets):
    """Analyse les tendances des hashtags dans les tweets."""
    hashtag_counts = defaultdict(int)
    
    for tweet in tweets:
        for hashtag in tweet.get("hashtags", []):
            hashtag = normalize_hashtag(hashtag)
            if hashtag:
                hashtag_counts[hashtag] += 1
    
    # Top 10 hashtags
    top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("Top 10 hashtags:")
    for hashtag, count in top_hashtags:
        print(f"#{hashtag}: {count}")
    
    return top_hashtags

def get_sentiment_label(score):
    """Détermine le label du sentiment basé sur le score."""
    if score > SENTIMENT_THRESHOLD:
        return "positif"
    elif score < -SENTIMENT_THRESHOLD:
        return "négatif"
    return "neutre"

def analyze_sentiment(tweets):
    """Analyse le sentiment des tweets et calcule le score moyen par jour."""
    daily_sentiment = defaultdict(list)
    
    print("\nAnalyse des sentiments des tweets...")
    for tweet in tweets:
        text, timestamp = tweet.get("tweet_text", ""), tweet.get("timestamp", "")
        if not text or not timestamp:
            continue
            
        # Extraction de la date et calcul du sentiment
        date = timestamp.split()[0]
        sentiment_score = TextBlob(text).sentiment.polarity
        daily_sentiment[date].append(sentiment_score)
    
    # Calcul et affichage des moyennes
    daily_averages = {day: sum(scores)/len(scores) for day, scores in daily_sentiment.items()}
    
    print("\nScore de sentiment moyen par jour:")
    for day, score in sorted(daily_averages.items()):
        print(f"{day}: {score:.4f} ({get_sentiment_label(score)})")
    
    return daily_averages

def extract_keywords(text):
    """Extrait les mots-clés d'un texte en supprimant les hashtags et liens."""
    clean_text = re.sub(r'#\w+|http\S+', '', text.lower())
    return [word for word in re.findall(r'\b[a-z]{3,}\b', clean_text) 
            if word not in STOP_WORDS]

def analyze_geo_distribution(tweets):
    """Analyse la distribution géographique des tweets et les thèmes par région."""
    regions = defaultdict(list)
    region_hashtags = defaultdict(lambda: defaultdict(int))
    
    # Classification par région
    for tweet in tweets:
        city = tweet.get("location", {}).get("city", "unknown")
        if city == "unknown":
            continue
            
        regions[city].append(tweet)
        
        # Comptage des hashtags par région
        for hashtag in tweet.get("hashtags", []):
            hashtag = normalize_hashtag(hashtag)
            if hashtag:
                region_hashtags[city][hashtag] += 1
    
    # Analyse des régions
    print("\nDistribution géographique des tweets:")
    for city, city_tweets in regions.items():
        print(f"\nRégion: {city}")
        print(f"Nombre de tweets: {len(city_tweets)}")
        
        # Top hashtags
        top_hashtags = sorted(region_hashtags[city].items(), 
                            key=lambda x: x[1], reverse=True)[:5]
        print("Top hashtags:")
        for hashtag, count in top_hashtags:
            print(f"  #{hashtag}: {count}")
        
        # Extraction des mots-clés fréquents
        all_keywords = []
        for tweet in city_tweets:
            all_keywords.extend(extract_keywords(tweet.get("tweet_text", "")))
            
        # Comptage et affichage des top mots-clés
        word_counts = defaultdict(int)
        for word in all_keywords:
            word_counts[word] += 1
            
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Top mots-clés:")
        for word, count in top_words:
            print(f"  {word}: {count}")
    
    return regions

def load_tweets(file_path):
    """Charge les tweets depuis un fichier JSON."""
    print(f"Lecture des tweets depuis {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as file:
        tweets = json.load(file)
    print(f"Nombre de tweets: {len(tweets)}")
    return tweets

def main():
    # Chargement des données
    tweets = load_tweets(DATA_PATH)
    
    # Analyses
    print("\n=== ANALYSE DES TENDANCES DE HASHTAGS ===")
    analyze_hashtags(tweets)
    
    print("\n=== ANALYSE DES SENTIMENTS ===")
    analyze_sentiment(tweets)
    
    print("\n=== ANALYSE DE LA DISTRIBUTION GÉOGRAPHIQUE ===")
    analyze_geo_distribution(tweets)
    
    print("\nAnalyses terminées !")

if __name__ == "__main__":
    main()
