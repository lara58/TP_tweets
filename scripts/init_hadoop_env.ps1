# Script PowerShell pour initialiser l'environnement Hadoop et Python dans le conteneur

Write-Host "Initialisation de l'environnement Docker pour les analyses MapReduce..." -ForegroundColor Cyan

# Vérifier que les conteneurs Docker sont en cours d'exécution
$containers = docker ps --format "{{.Names}}" | Where-Object { $_ -eq "namenode" }
if (-not $containers) {
    Write-Host "Démarrage des conteneurs Hadoop..." -ForegroundColor Yellow
    docker-compose up -d
    
    # Attendre que les conteneurs soient prêts
    Start-Sleep -Seconds 10
}

# Copier le script de correction de l'environnement dans le conteneur namenode
Write-Host "Copie du script d'initialisation dans le conteneur namenode..." -ForegroundColor Yellow
docker cp scripts/fix_docker_env.sh namenode:/tmp/fix_docker_env.sh
docker exec namenode chmod +x /tmp/fix_docker_env.sh

# Exécuter le script pour configurer l'environnement Python
Write-Host "Configuration de l'environnement Python dans le conteneur..." -ForegroundColor Yellow
docker exec namenode /tmp/fix_docker_env.sh

# Copier les scripts MapReduce
Write-Host "Copie des scripts MapReduce dans le conteneur..." -ForegroundColor Yellow
$scripts = @(
    "mapreduce/hashtag_mapper.py:/hashtag_mapper.py",
    "mapreduce/hashtag_reducer.py:/hashtag_reducer.py", 
    "mapreduce/geo_sentiment_mapper.py:/geo_sentiment_mapper.py",
    "mapreduce/geo_sentiment_reducer.py:/geo_sentiment_reducer.py"
)

foreach ($script in $scripts) {
    $parts = $script -split ":"
    docker cp $parts[0] namenode:$parts[1]
    docker exec namenode chmod +x $parts[1]
}

Write-Host "Vérification que les données sont disponibles dans HDFS..." -ForegroundColor Yellow
$hdfsFiles = docker exec namenode hdfs dfs -ls /tweets/2024/04/tweets.json

if (-not $hdfsFiles) {
    Write-Host "Stockage des données dans HDFS..." -ForegroundColor Yellow
    & .\scripts\store_results_in_hdfs.ps1
}

Write-Host "Environnement initialisé avec succès!" -ForegroundColor Green
Write-Host "Vous pouvez maintenant exécuter les analyses avec: .\scripts\run_analyses.ps1" -ForegroundColor Green
