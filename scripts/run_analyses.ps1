# Script PowerShell pour exécuter les analyses MapReduce dans Hadoop

function Setup-Environment {
    # Installation des dépendances
    Write-Host "Installation des dépendances..."
    docker exec namenode apt-get update -qq
    docker exec namenode apt-get install -y python3 python3-pip -qq
    docker exec namenode pip3 install textblob -q
    docker exec namenode python3 -m textblob.download_corpora lite
    
    # Copie des scripts MapReduce
    Write-Host "Configuration des scripts d'analyse..."
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
}

function Run-MapReduce($name, $mapper, $reducer, $outputFile) {
    Write-Host "Exécution de l'analyse $name..."
    
    # Construction du pipeline MapReduce
    docker exec namenode hdfs dfs -cat /tweets/2024/04/tweets.json | 
        docker exec -i namenode python3 $mapper | 
        docker exec -i namenode sort | 
        docker exec -i namenode python3 $reducer > $outputFile
        
    Write-Host "Résultats de $name disponibles dans: $outputFile"
}

# Initialisation de l'environnement
Setup-Environment

# Exécution des analyses MapReduce
$analyses = @(
    @{name="Hashtag"; mapper="/hashtag_mapper.py"; reducer="/hashtag_reducer.py"; output="hashtag_results.txt"},
    @{name="Sentiment"; mapper="/geo_sentiment_mapper.py"; reducer="/geo_sentiment_reducer.py"; output="geo_sentiment_results.txt"}
)

foreach ($analysis in $analyses) {
    Run-MapReduce $analysis.name $analysis.mapper $analysis.reducer $analysis.output
}

Write-Host "`nAnalyses terminées ! Stockez les résultats dans HDFS avec :"
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts/store_results_in_hdfs.ps1"
