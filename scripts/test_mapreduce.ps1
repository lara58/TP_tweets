# Script PowerShell pour tester les analyses MapReduce sur Hadoop
# Ce script doit être exécuté depuis une machine Windows avec Docker

# Vérifier que le cluster Hadoop est en cours d'exécution
Write-Host "Vérification de l'état du cluster Hadoop..."
docker ps | Select-String "namenode"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Le cluster Hadoop n'est pas en cours d'exécution. Démarrez-le avec 'docker-compose up -d'."
    exit 1
}

# Copier les scripts MapReduce dans le conteneur namenode
Write-Host "`nCopie des scripts MapReduce dans le conteneur namenode..."
docker cp hashtag_mapper.py namenode:/hashtag_mapper.py
docker cp hashtag_reducer.py namenode:/hashtag_reducer.py
docker cp geo_sentiment_mapper.py namenode:/geo_sentiment_mapper.py
docker cp geo_sentiment_reducer.py namenode:/geo_sentiment_reducer.py

# Rendre les scripts exécutables
Write-Host "`nConfiguration des permissions..."
docker exec namenode chmod +x /hashtag_mapper.py
docker exec namenode chmod +x /hashtag_reducer.py
docker exec namenode chmod +x /geo_sentiment_mapper.py
docker exec namenode chmod +x /geo_sentiment_reducer.py

# Installer les dépendances Python
Write-Host "`nInstallation des dépendances Python dans le conteneur namenode..."
docker exec namenode apt-get update -qq
docker exec namenode apt-get install -y -qq python3 python3-pip
docker exec namenode pip3 install -q textblob

# Test 1: Analyse des tendances de hashtags
Write-Host "`n=== TEST 1: ANALYSE DES TENDANCES DE HASHTAGS ==="
Write-Host "Exécution du MapReduce pour l'analyse des hashtags..."
docker exec namenode hdfs dfs -cat /tweets/2024/04/2024_04_tweets.json | docker exec -i namenode python3 /hashtag_mapper.py | docker exec -i namenode sort | docker exec -i namenode python3 /hashtag_reducer.py > hashtag_mapreduce_results.txt

# Afficher les résultats
Write-Host "`nRésultats de l'analyse des hashtags:"
Get-Content -Path hashtag_mapreduce_results.txt

# Test 2: Analyse des sentiments par région
Write-Host "`n=== TEST 2: ANALYSE DES SENTIMENTS PAR RÉGION ==="
Write-Host "Exécution du MapReduce pour l'analyse des sentiments par région..."
docker exec namenode hdfs dfs -cat /tweets/2024/04/2024_04_tweets.json | docker exec -i namenode python3 /geo_sentiment_mapper.py | docker exec -i namenode sort | docker exec -i namenode python3 /geo_sentiment_reducer.py > geo_sentiment_mapreduce_results.txt

# Afficher les résultats
Write-Host "`nRésultats de l'analyse des sentiments par région:"
Get-Content -Path geo_sentiment_mapreduce_results.txt

Write-Host "`nTests MapReduce terminés! Les résultats complets sont disponibles dans les fichiers:"
Write-Host "- hashtag_mapreduce_results.txt"
Write-Host "- geo_sentiment_mapreduce_results.txt"
