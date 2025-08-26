#!/usr/bin/env python3
import json
import sys

# Lire le tableau JSON
try:
    data = json.load(sys.stdin)
    
    # Vérifier si les données sont un tableau
    if isinstance(data, list):
        # Émettre chaque élément comme un objet JSON distinct
        for item in data:
            print(json.dumps(item))
    else:
        # Si c'est déjà un objet, le renvoyer tel quel
        print(json.dumps(data))
except json.JSONDecodeError:
    # Si le format n'est pas JSON valide, essayer de traiter chaque ligne
    # comme un objet JSON distinct (format JSONL)
    for line in sys.stdin:
        try:
            item = json.loads(line.strip())
            print(json.dumps(item))
        except json.JSONDecodeError:
            # Ignorer les lignes invalides
            pass
