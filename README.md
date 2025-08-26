# Projet d'Analyse de Tweets avec Hadoop

Ce projet implémente une analyse de tweets en utilisant Hadoop et le paradigme MapReduce.

## Structure du projet

### Fichiers principaux
- `docker-compose.yml` : Configuration Docker pour le cluster Hadoop
- `hadoop.env` : Variables d'environnement pour le cluster Hadoop
- `analyze_tweets.py` : Script principal d'analyse des tweets
- `analyze_tweets_with_sentiment.py` : Script d'analyse des tweets avec analyse de sentiment

### Dossiers
- `data/` : Contient les données brutes des tweets
- `scripts/` : Scripts utilitaires pour préparer et exécuter les analyses
- `mapreduce/` : Implémentations MapReduce pour les différentes analyses
- `tweets_by_month/` : Organisation des tweets par année/mois

## Comment exécuter le projet

1. **Démarrer le cluster Hadoop**
   ```
   docker-compose up -d
   ```

2. **Préparer les données pour HDFS**
   ```
   python scripts/prepare_tweets.py
   ```

3. **Exécuter les analyses**
   ```
   python analyze_tweets_with_sentiment.py
   ```
   ou
   ```
   powershell -ExecutionPolicy Bypass -File scripts/run_analyses.ps1
   ```

4. **Tester les analyses MapReduce**
   ```
   python mapreduce/mapreduce_hashtag_simulation.py
   python mapreduce/mapreduce_sentiment_simulation.py
   ```

## Résultats des analyses

1. **Analyse des tendances de hashtags** : Identifie les 10 hashtags les plus populaires par mois.
2. **Analyse de sentiments** : Calcule le score moyen de sentiment pour chaque jour et par région.
3. **Distribution géographique** : Analyse la répartition des tweets par pays/région et les différences thématiques par région.
