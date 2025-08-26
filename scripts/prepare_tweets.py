import json
import datetime
import os
import subprocess
from collections import defaultdict

def load_tweets(file_path="data/tweets_with_locations.json"):
    """Charge les tweets depuis un fichier JSON ou JSONL."""
    print("Lecture du fichier de tweets...")
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tweets = json.load(file)
        except json.JSONDecodeError:
            # Fallback pour format JSONL
            file.seek(0)
            tweets = [json.loads(line.strip()) for line in file if line.strip()]
    
    print(f"Nombre de tweets chargés: {len(tweets)}")
    return tweets

def organize_tweets_by_month(tweets):
    """Organise les tweets par année/mois."""
    print("Organisation des tweets par mois...")
    tweets_by_month = defaultdict(list)
    
    for tweet in tweets:
        if "timestamp" not in tweet:
            continue
            
        try:
            created_at = datetime.datetime.strptime(tweet["timestamp"], "%Y-%m-%d %H:%M:%S")
            year_month = f"{created_at.year}/{created_at.month:02d}"
            tweets_by_month[year_month].append(tweet)
        except Exception as e:
            print(f"Erreur de parsing de date: {e}")
    
    return tweets_by_month

def write_tweets_to_local_files(tweets_by_month):
    """Écrit les tweets dans des fichiers locaux organisés par mois."""
    print("Écriture des tweets dans des fichiers par mois...")
    os.makedirs("tweets_by_month", exist_ok=True)
    
    for year_month, month_tweets in tweets_by_month.items():
        year, month = year_month.split('/')
        directory = f"tweets_by_month/{year}/{month}"
        os.makedirs(directory, exist_ok=True)
        
        with open(f"{directory}/tweets.json", 'w', encoding='utf-8') as file:
            json.dump(month_tweets, file, ensure_ascii=False, indent=2)
        
        print(f"Écrit {len(month_tweets)} tweets pour {year_month}")

def upload_tweets_to_hdfs(tweets_by_month):
    """Upload les fichiers de tweets dans HDFS."""
    print("Création du répertoire /tweets dans HDFS...")
    subprocess.run(["docker", "exec", "namenode", "hdfs", "dfs", "-mkdir", "-p", "/tweets"])
    
    print("Copie des tweets vers HDFS...")
    for year_month in tweets_by_month.keys():
        year, month = year_month.split('/')
        
        # Créer la structure de dossiers dans HDFS
        subprocess.run(["docker", "exec", "namenode", "hdfs", "dfs", "-mkdir", "-p", f"/tweets/{year}/{month}"])
        
        # Chemin des fichiers
        local_path = f"tweets_by_month/{year}/{month}/tweets.json"
        
        # Utiliser la méthode directe pour transférer vers HDFS
        with open(local_path, 'rb') as f:
            hdfs_path = f"/tweets/{year}/{month}/tweets.json"
            cmd = ["docker", "exec", "-i", "namenode", "hdfs", "dfs", "-put", "-f", "-", hdfs_path]
            subprocess.run(cmd, input=f.read())
        
        print(f"Tweets pour {year_month} copiés vers HDFS")

def main():
    """Fonction principale pour préparer les tweets pour HDFS."""
    # Charger les tweets
    tweets = load_tweets("data/tweets_with_locations.json")
    
    # Organiser par mois
    tweets_by_month = organize_tweets_by_month(tweets)
    
    # Écrire dans des fichiers locaux
    write_tweets_to_local_files(tweets_by_month)
    
    # Uploader vers HDFS
    upload_tweets_to_hdfs(tweets_by_month)
    
    print("Préparation des données terminée !")
    print("Vous pouvez maintenant vérifier la structure sur l'interface HDFS: http://localhost:9870")

if __name__ == "__main__":
    main()
