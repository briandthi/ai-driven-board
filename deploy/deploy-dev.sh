#!/bin/bash
set -e

echo "🚀 Déploiement en mode DÉVELOPPEMENT (docker-compose.dev.yml, hot reload activé)"
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up

echo "✅ Stack développement lancée avec hot reload !"