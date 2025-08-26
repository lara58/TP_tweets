# Projet d'Analyse de Tweets avec Hadoop

Ce projet implémente une analyse de tweets en utilisant Hadoop et le paradigme MapReduce.

## Structure du projet

### Fichiers principaux
- `docker-compose.yml` : Configuration Docker pour le cluster Hadoop
- `hadoop.env` : Variables d'environnement pour le cluster Hadoop
- `analyze_tweets_with_sentiment.py` : Script d'analyse des tweets avec analyse de sentiment

### Dossiers
- `data/` : Contient les données brutes des tweets
- `scripts/` : Scripts utilitaires pour préparer et exécuter les analyses
  - `prepare_tweets.py` : Prétraite les tweets et ajoute des informations de géolocalisation
  - `run_analyses.ps1` : Exécute les analyses MapReduce dans l'environnement Hadoop
  - `init_hadoop_env.ps1` : Configure l'environnement Python dans le conteneur Docker
  - `fix_docker_env.sh` : Corrige les dépôts Debian et installe Python dans le conteneur
  - `json_converter.py` : Convertit le format JSON des tweets pour le traitement
- `mapreduce/` : Implémentations MapReduce pour les différentes analyses
  - `hashtag_mapper.py` & `hashtag_reducer.py` : Analyse des hashtags populaires par mois
  - `geo_sentiment_mapper.py` & `geo_sentiment_reducer.py` : Analyse des sentiments par région
  - `mapreduce_hashtag_simulation.py` & `mapreduce_sentiment_simulation.py` : Simulations locales
- `tweets_by_month/` : Organisation des tweets par année/mois

## Comment exécuter le projet

1. **Démarrer le cluster Hadoop et configurer l'environnement**
   ```
   docker-compose up -d
   powershell -ExecutionPolicy Bypass -File scripts/init_hadoop_env.ps1
   ```

2. **Préparer les données pour HDFS**
   ```
   # Prétraiter les tweets
   python scripts/prepare_tweets.py
   
   # Stocker les résultats dans HDFS
   docker exec namenode hdfs dfs -mkdir -p /results/hashtags /results/sentiment /results/geo
   
   # Obtenir la date actuelle au format YYYY-MM
   $datestamp = Get-Date -Format "yyyy-MM"
   
   # Stocker les fichiers de résultats dans HDFS (si disponibles)
   Get-Content hashtag_results.txt -Raw | docker exec -i namenode hdfs dfs -put -f - /results/hashtags/${datestamp}_hashtags.txt
   Get-Content sentiment_results.txt -Raw | docker exec -i namenode hdfs dfs -put -f - /results/sentiment/${datestamp}_sentiment.txt
   Get-Content geo_results.txt -Raw | docker exec -i namenode hdfs dfs -put -f - /results/geo/${datestamp}_geo.txt
   ```

3. **Exécuter les analyses MapReduce**
   ```
   powershell -ExecutionPolicy Bypass -File scripts/run_analyses.ps1
   ```

4. **Tester les analyses MapReduce localement (sans Hadoop)**
   ```
   python mapreduce/mapreduce_hashtag_simulation.py
   python mapreduce/mapreduce_sentiment_simulation.py
   ```

## Vérifier le fonctionnement de la partie 2 (MapReduce)

Pour vérifier si l'analyse MapReduce fonctionne correctement, vous pouvez utiliser les commandes suivantes :

### Tester les simulations MapReduce locales
Ces commandes exécutent les simulations MapReduce sur votre machine locale, sans nécessiter Hadoop :
```powershell
# Simulation de l'analyse des hashtags
python mapreduce/mapreduce_hashtag_simulation.py

# Simulation de l'analyse des sentiments par région
python mapreduce/mapreduce_sentiment_simulation.py
```

### Vérifier le format des données dans HDFS
Pour vérifier si les données sont au format correct pour les mappeurs :
```powershell
docker exec -it namenode bash
bash /scripts/check_json_format.sh
```

### Exécuter l'analyse MapReduce complète
Pour exécuter l'analyse MapReduce complète sur le cluster Hadoop avec conversion automatique du format JSON :
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_analyses.ps1
```

### Vérifier les résultats
Pour voir les résultats des analyses :
```powershell
# Résultats de l'analyse des hashtags
Get-Content hashtag_results.txt

# Résultats de l'analyse des sentiments par région
Get-Content geo_sentiment_results.txt

# Vérifier les résultats stockés dans HDFS
docker exec namenode hdfs dfs -ls -R /results
docker exec namenode hdfs dfs -cat /results/hashtags/2025-08_hashtags.txt
docker exec namenode hdfs dfs -cat /results/geo/2025-08_geo.txt
docker exec namenode hdfs dfs -cat /results/sentiment/2025-08_sentiment.txt
```

### Test et dépannage avancés
Pour des informations détaillées sur la résolution des problèmes courants, consultez [le guide de dépannage](TROUBLESHOOTING.md).

Vous pouvez également tester chaque composant du pipeline individuellement :

```powershell
# Tester le convertisseur JSON et les mappeurs
docker exec -it namenode bash
bash /scripts/test_converter.sh

# Tester les mappeurs directement avec des données de test simples
docker exec -it namenode bash
bash /scripts/test_json_format.sh
```

## Résultats des analyses

1. **Analyse des tendances de hashtags** : Identifie les 10 hashtags les plus populaires par mois.
2. **Analyse de sentiments** : Calcule le score moyen de sentiment pour chaque jour et par région.
3. **Distribution géographique** : Analyse la répartition des tweets par pays/région et les différences thématiques par région.

### Exemples de résultats obtenus

#### Analyse des sentiments par région
```
Berlin: 0.0958 (neutre) - 85 tweets
Dubai: 0.1054 (positif) - 104 tweets
London: 0.1224 (positif) - 99 tweets
Mumbai: 0.0993 (neutre) - 90 tweets
New York: 0.1475 (positif) - 113 tweets
Paris: 0.1022 (positif) - 102 tweets
San Francisco: 0.1360 (positif) - 95 tweets
Sydney: 0.1377 (positif) - 106 tweets
São Paulo: 0.1147 (positif) - 107 tweets
Tokyo: 0.1153 (positif) - 99 tweets
```

## Vérification finale du projet

Pour vous assurer que le projet est correctement configuré et fonctionne comme prévu :

1. **Vérifier l'environnement**
   ```powershell
   # Vérifier que les conteneurs Docker sont en cours d'exécution
   docker ps
   
   # Vérifier que Python et TextBlob sont installés dans le conteneur
   docker exec namenode python3 -c "import textblob; print('TextBlob disponible')"
   ```

2. **Nettoyer les fichiers temporaires avant de soumettre le projet**
   ```powershell
   # Exécuter le script de nettoyage
   powershell -ExecutionPolicy Bypass -File scripts/cleanup.ps1
   ```

## Commandes HDFS utiles

### Explorer la structure HDFS
```powershell
# Lister le contenu d'un répertoire HDFS
docker exec namenode hdfs dfs -ls -R /

# Lister spécifiquement le dossier des tweets
docker exec namenode hdfs dfs -ls -R /tweets

# Afficher le contenu d'un fichier HDFS
docker exec namenode hdfs dfs -cat /tweets/2024/04/tweets.json | Select-Object -First 5
```

### Gérer les données dans HDFS
```powershell
# Créer un répertoire dans HDFS
docker exec namenode hdfs dfs -mkdir -p /results/hashtags

# Copier un fichier local vers HDFS
Get-Content hashtag_results.txt -Raw | docker exec -i namenode hdfs dfs -put -f - /results/hashtags/hashtags.txt

# Télécharger un fichier depuis HDFS
docker exec namenode hdfs dfs -get /tweets/2024/04/tweets.json ./downloaded_tweets.json

# Supprimer un fichier ou répertoire
docker exec namenode hdfs dfs -rm -r /results/old_data
```

### Stocker les résultats d'analyse dans HDFS
```powershell
# Stocker les résultats d'analyse dans HDFS
docker exec namenode hdfs dfs -mkdir -p /results/hashtags /results/sentiment /results/geo

# Obtenir la date actuelle au format YYYY-MM
$datestamp = Get-Date -Format "yyyy-MM"

# Stocker les fichiers de résultats dans HDFS
Get-Content hashtag_results.txt -Raw | docker exec -i namenode hdfs dfs -put -f - /results/hashtags/${datestamp}_hashtags.txt
Get-Content geo_sentiment_results.txt -Raw | docker exec -i namenode hdfs dfs -put -f - /results/geo/${datestamp}_geo.txt
```
