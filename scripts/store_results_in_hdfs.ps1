# Script PowerShell pour stocker les résultats dans HDFS

# Créer les répertoires de résultats
docker exec namenode hdfs dfs -mkdir -p /results/hashtags /results/sentiment /results/geo

# Obtenir le horodatage au format YYYY-MM
$datestamp = Get-Date -Format "yyyy-MM"

# Mapper les fichiers locaux aux chemins HDFS
$files = @{
    "hashtag_results.txt"   = "/results/hashtags/${datestamp}_hashtags.txt"
    "sentiment_results.txt" = "/results/sentiment/${datestamp}_sentiment.txt"
    "geo_results.txt"       = "/results/geo/${datestamp}_geo.txt"
}

# Transférer chaque fichier
foreach ($file in $files.Keys) {
    if (Test-Path $file) {
        Write-Host "Stockage: $file -> $($files[$file])"
        Get-Content $file -Raw | docker exec -i namenode hdfs dfs -put -f - $($files[$file])
    } else {
        Write-Host "Ignoré: $file (non trouvé)"
    }
}

Write-Host "`nTerminé. Pour vérifier: docker exec namenode hdfs dfs -ls -R /results"
