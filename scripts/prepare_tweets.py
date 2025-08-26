import json
import datetime
import os
import subprocess
from collections import defaultdict

# Chemin vers le fichier JSON des tweets
input_file = "tweets_with_locations.json"

# Créer un répertoire temporaire pour stocker les fichiers organisés par mois
os.makedirs("tweets_by_month", exist_ok=True)

# Dictionnaire pour stocker les tweets par année/mois
tweets_by_month = defaultdict(list)

# Lire le fichier JSON
print("Lecture du fichier de tweets...")
with open(input_file, 'r', encoding='utf-8') as file:
    try:
        # Essayer de charger le fichier comme une liste de tweets
        tweets = json.load(file)
        is_list = True
    except json.JSONDecodeError:
        # Si échec, essayer de lire ligne par ligne (format JSONL)
        file.seek(0)
        tweets = []
        for line in file:
            try:
                tweet = json.loads(line.strip())
                tweets.append(tweet)
            except json.JSONDecodeError:
                continue
        is_list = True

print(f"Nombre de tweets chargés: {len(tweets)}")

# Organiser les tweets par mois et année
print("Organisation des tweets par mois...")
for tweet in tweets:
    # Vérifier la structure du tweet pour trouver la date
    created_at = None
    
    # Format des tweets dans notre dataset: "timestamp": "2024-04-03 10:24:53"
    if "timestamp" in tweet:
        try:
            created_at = datetime.datetime.strptime(tweet["timestamp"], "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Erreur de parsing de date: {e}")
            continue
    
    if created_at:
        year_month = f"{created_at.year}/{created_at.month:02d}"
        tweets_by_month[year_month].append(tweet)

# Écrire les tweets dans des fichiers organisés par mois
print("Écriture des tweets dans des fichiers par mois...")
for year_month, month_tweets in tweets_by_month.items():
    year, month = year_month.split('/')
    directory = f"tweets_by_month/{year}/{month}"
    os.makedirs(directory, exist_ok=True)
    
    with open(f"{directory}/tweets.json", 'w', encoding='utf-8') as file:
        json.dump(month_tweets, file, ensure_ascii=False, indent=2)
    
    print(f"Écrit {len(month_tweets)} tweets pour {year_month}")

# Créer le répertoire /tweets dans HDFS
print("Création du répertoire /tweets dans HDFS...")
subprocess.run(["docker", "exec", "namenode", "hdfs", "dfs", "-mkdir", "-p", "/tweets"])

# Copier les fichiers vers HDFS
print("Copie des tweets vers HDFS...")
for year_month in tweets_by_month.keys():
    year, month = year_month.split('/')
    
    # Créer la structure de dossiers dans HDFS
    subprocess.run(["docker", "exec", "namenode", "hdfs", "dfs", "-mkdir", "-p", f"/tweets/{year}/{month}"])
    
    # Copier le fichier local vers le conteneur namenode
    local_path = f"tweets_by_month/{year}/{month}/tweets.json"
    container_path = f"/tmp/{year}_{month}_tweets.json"
    subprocess.run(["docker", "cp", local_path, f"namenode:{container_path}"])
    
    # Déplacer le fichier du conteneur namenode vers HDFS
    subprocess.run(["docker", "exec", "namenode", "hdfs", "dfs", "-put", container_path, f"/tweets/{year}/{month}/"])
    
    print(f"Tweets pour {year_month} copiés vers HDFS")

print("Préparation des données terminée !")
print("Vous pouvez maintenant vérifier la structure sur l'interface HDFS: http://localhost:9870")
