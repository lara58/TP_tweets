# Script PowerShell pour exécuter les analyses MapReduce dans Hadoop

# Installer Python et TextBlob pour l'analyse de sentiment
Write-Host "Installation des dépendances..."
docker exec namenode apt-get update
docker exec namenode apt-get install -y python3 python3-pip
docker exec namenode pip3 install textblob
docker exec namenode python3 -m textblob.download_corpora

# Copier les scripts dans le conteneur namenode
Write-Host "Copie des scripts dans le conteneur namenode..."
docker cp hashtag_analyzer.py namenode:/hashtag_analyzer.py
docker cp sentiment_analyzer.py namenode:/sentiment_analyzer.py
docker cp geo_analyzer.py namenode:/geo_analyzer.py

# Rendre les scripts exécutables
Write-Host "Configuration des permissions..."
docker exec namenode chmod +x /hashtag_analyzer.py
docker exec namenode chmod +x /sentiment_analyzer.py
docker exec namenode chmod +x /geo_analyzer.py

# 1. Analyse des hashtags
Write-Host "Exécution de l'analyse des hashtags..."
Write-Host "Préparation des données d'entrée..."
docker exec namenode hdfs dfs -cat /tweets/2024/04/2024_04_tweets.json | docker exec -i namenode python3 /hashtag_analyzer.py mapper | docker exec -i namenode sort | docker exec -i namenode python3 /hashtag_analyzer.py > hashtag_results.txt

# 2. Analyse des sentiments (nécessite textblob)
Write-Host "Exécution de l'analyse des sentiments..."
docker exec namenode hdfs dfs -cat /tweets/2024/04/2024_04_tweets.json | docker exec -i namenode python3 /sentiment_analyzer.py mapper | docker exec -i namenode sort | docker exec -i namenode python3 /sentiment_analyzer.py > sentiment_results.txt

# 3. Analyse géographique
Write-Host "Exécution de l'analyse géographique..."
docker exec namenode hdfs dfs -cat /tweets/2024/04/2024_04_tweets.json | docker exec -i namenode python3 /geo_analyzer.py mapper | docker exec -i namenode sort | docker exec -i namenode python3 /geo_analyzer.py > geo_results.txt

Write-Host "Analyses terminées ! Résultats disponibles dans:"
Write-Host "- hashtag_results.txt"
Write-Host "- sentiment_results.txt"
Write-Host "- geo_results.txt"
