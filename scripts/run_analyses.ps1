# Script PowerShell pour exécuter les analyses MapReduce dans Hadoop

function Setup-Environment {
    # Vérifier si l'environnement est déjà configuré
    $pythonCheck = docker exec namenode which python3 2>$null
    
    if (-not $pythonCheck) {
        Write-Host "L'environnement Python n'est pas configuré. Exécutez d'abord .\scripts\init_hadoop_env.ps1" -ForegroundColor Red
        exit 1
    }
    
    # Définir le répertoire du projet
    $projectDir = $PWD.Path
    
    # Copie des scripts MapReduce
    Write-Host "Configuration des scripts d'analyse..."
    $scripts = @(
        "$projectDir\mapreduce\hashtag_mapper.py:/hashtag_mapper.py",
        "$projectDir\mapreduce\hashtag_reducer.py:/hashtag_reducer.py", 
        "$projectDir\mapreduce\geo_sentiment_mapper.py:/geo_sentiment_mapper.py",
        "$projectDir\mapreduce\geo_sentiment_reducer.py:/geo_sentiment_reducer.py"
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
