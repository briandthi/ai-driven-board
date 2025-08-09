# Board AI-driven avec MCP - Spécifications Projet

## Vue d'ensemble

Système de board de gestion intelligent piloté principalement par IA, avec capacité d'émergence de structures et métadonnées dynamiques. L'objectif est de créer un outil qui s'adapte organiquement aux besoins plutôt que d'imposer une structure rigide.

## Philosophie du projet

- **AI-native** : L'IA n'est pas un add-on mais le cœur du système
- **Émergence structurelle** : Les catégories et métadonnées émergent de l'usage plutôt que d'être prédéfinies
- **Continuum IA-humain** : L'IA propose et agit, l'humain garde le contrôle éditorial
- **Flexibilité adaptative** : Le système s'adapte aux patterns d'usage detectés

## Stack Technique

### Frontend
- **ReactJS** avec TanStack Query pour la gestion d'état et synchronisation serveur
- **shadcn/ui** + **Tailwind CSS** pour l'interface
- Interface dynamique capable d'afficher des champs non anticipés selon les métadonnées

### Backend
- **Python** + **FastAPI** pour l'API REST
- **LangGraph** pour l'orchestration des workflows IA
- Serveur **MCP (Model Context Protocol)** pour exposer les tools aux LLM
- **SQLite** initialement, avec migration possible vers MongoDB

### Base de données
- **MongoDB** (Docker) pour le MVP
  - Schéma flexible pour métadonnées dynamiques
  - Stockage JSON natif
  - Bonne intégration Python (pymongo, motor, beanie)
- Alternative future : PostgreSQL + JSONB pour scalabilité

### Intégrations IA
- LLM pour analyse contextuelle et génération d'items
- Assistants de développement (ex: Claude Code) pour exécution automatique des tâches
- Système de validation et normalisation des métadonnées émergentes

## Architecture fonctionnelle

### Boards
- **Multi-boards indépendants** : Regroupement contextuel des items
- Création automatique de nouveaux boards par l'IA selon le contexte
- Gestion manuelle possible pour réorganisation

### Items
Structure flexible avec champs de base :

#### Champs Core
- `id` : Identifiant unique
- `title` : Titre de l'item
- `type` : Type d'item (idée, bug, feature, projet, task, specs...)
- `board_id` : Référence au board parent
- `status` : Statut évolutif (à faire, en cours, terminé, etc.)
- `creation_date` : Date de création
- `last_updated` : Dernière modification

#### Descriptions
- `functional_description` : Description orientée besoin métier (texte libre)
- `technical_description` : Description orientée implémentation (texte libre)

#### Checklists
- `checklist` : Liste de sous-tâches avec statut (array d'objets)
  ```json
  [
    {"task": "Définir API", "completed": false},
    {"task": "Implémenter endpoint", "completed": true}
  ]
  ```

#### Métadonnées dynamiques
- Champs générés automatiquement par l'IA selon le contexte
- Validation et normalisation automatique des noms de champs
- Versioning des formats pour items du même type

### Workflows IA

#### Création d'items
1. Utilisateur soumet une demande sommaire
2. LLM analyse le contexte et détermine :
   - Le board approprié (existant ou nouveau)
   - Le type d'item
   - Les métadonnées pertinentes
3. Création via tools MCP
4. Validation et normalisation des métadonnées

#### Gestion des catégories émergentes
- Détection automatique de catégories similaires
- Consolidation des noms de champs (ex: `creat_dt` → `creation_date`)
- Historisation des évolutions de schema
- Outils d'administration pour nettoyage

#### Liaison contextuelle
- Détection automatique de liens entre items existants
- Propagation rétroactive de métadonnées utiles (fonctionnalité optionnelle)
- Suggestions de regroupement ou réorganisation

## API MCP

### Tools exposés
- `create_item` : Création d'un nouvel item
- `update_item` : Modification d'item existant
- `delete_item` : Suppression d'item
- `list_items` : Liste des items avec filtres
- `create_board` : Création d'un nouveau board
- `update_item_status` : Mise à jour de statut
- `update_checklist` : Gestion des sous-tâches
- `validate_metadata` : Validation des métadonnées émergentes

### Endpoints REST (pour le frontend)
- `GET /boards` : Liste des boards
- `GET /boards/{id}/items` : Items d'un board
- `POST/PUT/DELETE /items/{id}` : CRUD items
- `GET /metadata/schemas` : Schémas actuels par type d'item
- `POST /ai/process` : Soumission de demandes à l'IA

## Stratégie MVP

### Phase 1 : Auto-construction
- **Objectif** : Créer un board pour gérer la construction du projet lui-même
- **Features prioritaires** :
  1. Création d'items par IA via interface de chat simple
  2. Board basique avec affichage des items
  3. Gestion des statuts
  4. Interface d'édition manuelle

### Phase 2 : Raffinement
- Validation avancée des métadonnées
- Liaison contextuelle entre items
- Interface dynamique complète
- Intégration assistants de code

### Phase 3 : Évolution
- Multi-utilisateurs
- Collaboration temps réel
- Analytics et insights
- API publique

## Considérations techniques

### Gestion des schemas évolutifs
- **TanStack Query** : Stratégie de cache adaptée aux schemas changeants
- **React** : Composants générés dynamiquement selon métadonnées
- **Validation** : Middleware de normalisation des champs

### Performance et scalabilité
- Index MongoDB sur champs fréquemment requêtés
- Cache des schemas pour éviter recalculs
- Optimisation des requêtes avec agrégation

### Sécurité et intégrité
- Validation côté serveur des métadonnées IA
- Audit trail des actions automatiques
- Rollback possible des modifications IA

## Extensions futures

### Fonctionnalités avancées
- **Templates intelligents** : Génération de templates basée sur l'historique
- **Workflows automatiques** : Déclenchement d'actions selon règles apprises
- **Insights comportementaux** : Analyse des patterns d'usage
- **Intégration ecosystem** : Connexion avec outils externes (GitHub, Slack...)

### Architecture technique
- Migration vers PostgreSQL pour fonctionnalités collaboratives
- Microservices pour scalabilité
- Event sourcing pour audit complet
- API GraphQL pour requêtes complexes

## Points de vigilance

1. **Explosion de métadonnées** : Surveiller la prolifération de champs similaires
2. **Performance requêtes** : Optimiser avec l'augmentation du volume
3. **UX cohérence** : Maintenir utilisabilité malgré la flexibilité
4. **Gouvernance IA** : Équilibrer automatisation et contrôle utilisateur

## Métriques de succès

- Temps moyen de création d'item < 30 secondes
- Taux d'acceptation des suggestions IA > 80%
- Réduction du temps de gestion administrative > 50%
- Émergence naturelle de structures organisationnelles utiles