# Script PowerShell pour exécuter les analyses MapReduce dans Hadoop

function Setup-Environment {
    # Vérifier si l'environnement est déjà configuré
    $pythonCheck = docker exec namenode which python3 2>$null
    
    if (-not $pythonCheck) {
        Write-Host "L'environnement Python n'est pas configuré. Exécutez d'abord .\scripts\init_hadoop_env.ps1" -ForegroundColor Red
        exit 1
    }
    
    # Copie des scripts MapReduce et utilitaires
    Write-Host "Configuration des scripts d'analyse..."
    
    # Utiliser des chemins qui fonctionnent avec Docker CP
    $scriptDir = Join-Path $PWD.Path "mapreduce"
    $utilsDir = Join-Path $PWD.Path "scripts"
    
    # Mapper les fichiers locaux aux chemins dans le conteneur
    $files = @(
        @{src = "$scriptDir/hashtag_mapper.py"; dest = "/hashtag_mapper.py"},
        @{src = "$scriptDir/hashtag_reducer.py"; dest = "/hashtag_reducer.py"},
        @{src = "$scriptDir/geo_sentiment_mapper.py"; dest = "/geo_sentiment_mapper.py"},
        @{src = "$scriptDir/geo_sentiment_reducer.py"; dest = "/geo_sentiment_reducer.py"},
        @{src = "$utilsDir/json_converter.py"; dest = "/json_converter.py"}
    )
    
    foreach ($file in $files) {
        # Convertir les chemins au format Docker (utiliser des slashes avant)
        $sourcePath = $file.src -replace '\\', '/'
        Write-Host "Copie de $sourcePath vers le conteneur..."
        
        # Copier le fichier dans le conteneur
        docker cp "$sourcePath" "namenode:$($file.dest)"
        
        # Rendre le fichier exécutable
        docker exec namenode chmod +x $file.dest
    }
}

function Run-MapReduce($name, $mapper, $reducer, $outputFile) {
    Write-Host "Exécution de l'analyse $name..."
    
    # Vérifier que les fichiers sont présents dans le conteneur
    Write-Host "Vérification des scripts dans le conteneur..."
    docker exec namenode ls -l $mapper $reducer /json_converter.py
    
    # Afficher les premières lignes des tweets pour vérifier le format
    Write-Host "Aperçu des données d'entrée:"
    docker exec namenode hdfs dfs -cat /tweets/2024/04/tweets.json | docker exec -i namenode head -n 5
    
    # Construction du pipeline MapReduce avec redirection de la sortie
    Write-Host "Exécution du pipeline MapReduce..."
    $tempOutput = "temp_output_$name.txt"
    
    # Exécuter chaque étape séparément pour un meilleur diagnostic
    Write-Host "Étape 1: Extraction des données depuis HDFS"
    docker exec namenode hdfs dfs -cat /tweets/2024/04/tweets.json > $tempOutput
    
    Write-Host "Étape 2: Conversion du format JSON"
    Get-Content $tempOutput | docker exec -i namenode python3 /json_converter.py > "converted_$name.txt"
    
    Write-Host "Étape 3: Exécution du mappeur"
    Get-Content "converted_$name.txt" | docker exec -i namenode python3 $mapper > "mapper_output_$name.txt"
    
    Write-Host "Étape 4: Tri des résultats"
    Get-Content "mapper_output_$name.txt" | docker exec -i namenode sort > "sorted_output_$name.txt"
    
    Write-Host "Étape 5: Exécution du réducteur"
    Get-Content "sorted_output_$name.txt" | docker exec -i namenode python3 $reducer > $outputFile
    
    # Nettoyage des fichiers temporaires
    Remove-Item $tempOutput, "mapper_output_$name.txt", "sorted_output_$name.txt" -ErrorAction SilentlyContinue
    
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

Write-Host "`nAnalyses terminées ! Pour stocker les résultats dans HDFS, utilisez les commandes suivantes :"
Write-Host "  docker exec namenode hdfs dfs -mkdir -p /results/hashtags /results/sentiment /results/geo"
Write-Host "  `$datestamp = Get-Date -Format `"yyyy-MM`""
Write-Host "  Get-Content hashtag_results.txt -Raw | docker exec -i namenode hdfs dfs -put -f - /results/hashtags/`${datestamp}_hashtags.txt"
Write-Host "  Get-Content geo_sentiment_results.txt -Raw | docker exec -i namenode hdfs dfs -put -f - /results/geo/`${datestamp}_geo.txt"
