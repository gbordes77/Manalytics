# 📖 Guide des Opérations - Manalytics

Ce guide couvre toutes les opérations quotidiennes pour maintenir et opérer la plateforme Manalytics.

## 📋 Table des Matières

1. [Démarrage quotidien](#démarrage-quotidien)
2. [Monitoring](#monitoring)
3. [Scraping de données](#scraping-de-données)
4. [Gestion des utilisateurs](#gestion-des-utilisateurs)
5. [Maintenance de la base de données](#maintenance-de-la-base-de-données)
6. [Backup et restauration](#backup-et-restauration)
7. [Mise à jour des règles](#mise-à-jour-des-règles)
8. [Logs et debugging](#logs-et-debugging)

## 🌅 Démarrage Quotidien

### Vérification système complète

```bash
# 1. Vérifier tous les conteneurs
docker-compose ps

# 2. Vérifier la santé du système
curl http://localhost:8000/health

# 3. Tester l'intégration complète
docker exec manalytics-api-1 python scripts/final_integration_test.py

# 4. Vérifier l'espace disque
df -h /var/lib/docker
```

### Dashboard de monitoring

```bash
# Nombre de tournois et decks
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT 
  (SELECT COUNT(*) FROM manalytics.tournaments) as tournaments,
  (SELECT COUNT(*) FROM manalytics.decklists) as decks,
  (SELECT COUNT(DISTINCT archetype_id) FROM manalytics.decklists WHERE archetype_id IS NOT NULL) as archetypes_detected,
  (SELECT COUNT(*) FROM manalytics.archetype_rules) as rules;"
```

## 📊 Monitoring

### Métriques en temps réel

```bash
# CPU et mémoire des conteneurs
docker stats

# Taille de la base de données
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size 
FROM pg_database 
WHERE datname = 'manalytics';"

# Connexions actives
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT count(*) FROM pg_stat_activity WHERE datname = 'manalytics';"
```

### Alertes recommandées

- CPU > 80% pendant 5 minutes
- Mémoire > 90%
- Espace disque < 10GB
- API response time > 2s
- Échecs de scraping consécutifs > 3

## 🔄 Scraping de Données

### Scraping manuel

```bash
# Un format spécifique
docker exec manalytics-worker-1 python scripts/run_pipeline.py --format modern --days 3

# Tous les formats
docker exec manalytics-worker-1 python scripts/run_pipeline.py --format all --days 1

# Mode debug
docker exec manalytics-worker-1 python scripts/run_pipeline.py --format standard --days 1 --debug
```

### Scraping automatique (cron)

```bash
# Ajouter au crontab de l'hôte
crontab -e

# Scraping quotidien à 2h du matin
0 2 * * * cd /path/to/manalytics && docker exec manalytics-worker-1 python scripts/run_pipeline.py --format all --days 1 >> /var/log/manalytics-scraping.log 2>&1

# Scraping hebdomadaire complet le dimanche
0 3 * * 0 cd /path/to/manalytics && docker exec manalytics-worker-1 python scripts/run_pipeline.py --format all --days 7 >> /var/log/manalytics-weekly.log 2>&1
```

### Vérification post-scraping

```bash
# Derniers tournois scrapés
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT s.name as source, f.name as format, COUNT(*) as count, MAX(t.date) as last_date
FROM manalytics.tournaments t
JOIN manalytics.sources s ON t.source_id = s.id
JOIN manalytics.formats f ON t.format_id = f.id
WHERE t.created_at > NOW() - INTERVAL '24 hours'
GROUP BY s.name, f.name
ORDER BY count DESC;"
```

## 👥 Gestion des Utilisateurs

### Créer un nouvel utilisateur

```python
# Script: scripts/create_user.py
docker exec -it manalytics-api-1 python -c "
from src.api.auth import create_user, UserCreate
user = UserCreate(
    username='nouveau_user',
    email='user@example.com',
    password='motdepasse_secure',
    full_name='Nom Complet'
)
created = create_user(user)
print(f'User created: {created.username} (ID: {created.id})')
"
```

### Gérer les droits admin

```bash
# Promouvoir en admin
docker exec manalytics-db-1 psql -U manalytics -c "
UPDATE manalytics.users SET is_admin = true WHERE username = 'nouveau_user';"

# Lister les admins
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT username, email, is_admin, is_active FROM manalytics.users WHERE is_admin = true;"
```

### Réinitialiser un mot de passe

```python
docker exec -it manalytics-api-1 python -c "
from src.api.auth import get_password_hash
new_hash = get_password_hash('nouveau_mot_de_passe')
print(f'New hash: {new_hash}')
# Puis update dans la DB avec ce hash
"
```

## 🗄️ Maintenance de la Base de Données

### Nettoyage régulier

```bash
# Vacuum et analyse (hebdomadaire)
docker exec manalytics-db-1 psql -U manalytics -c "VACUUM ANALYZE;"

# Nettoyer les vieux logs (mensuel)
docker exec manalytics-db-1 psql -U manalytics -c "
DELETE FROM manalytics.user_sessions WHERE created_at < NOW() - INTERVAL '90 days';
DELETE FROM manalytics.audit_logs WHERE created_at < NOW() - INTERVAL '180 days';"

# Réindexer si performances dégradées
docker exec manalytics-db-1 psql -U manalytics -c "REINDEX DATABASE manalytics;"
```

### Statistiques de tables

```bash
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
  n_live_tup AS row_count
FROM pg_stat_user_tables 
WHERE schemaname = 'manalytics'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

## 💾 Backup et Restauration

### Backup manuel

```bash
# Backup complet
docker exec manalytics-db-1 pg_dump -U manalytics manalytics | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup des données uniquement (sans schema)
docker exec manalytics-db-1 pg_dump -U manalytics --data-only manalytics | gzip > data_$(date +%Y%m%d).sql.gz
```

### Backup automatique

```bash
# Script backup quotidien
cat > /opt/manalytics/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/manalytics"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# Backup DB
docker exec manalytics-db-1 pg_dump -U manalytics manalytics | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup archetype rules  
docker exec manalytics-api-1 tar czf - database/seed_data/rules > $BACKUP_DIR/rules_$DATE.tar.gz

# Garde seulement 7 jours
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/manalytics/backup.sh

# Ajouter au cron
echo "0 4 * * * /opt/manalytics/backup.sh >> /var/log/manalytics-backup.log 2>&1" | crontab -
```

### Restauration

```bash
# Restaurer depuis un backup
gunzip -c backup_20250724_120000.sql.gz | docker exec -i manalytics-db-1 psql -U manalytics manalytics

# Restaurer seulement certaines tables
gunzip -c backup.sql.gz | grep -E "(tournaments|decklists)" | docker exec -i manalytics-db-1 psql -U manalytics
```

## 🔄 Mise à Jour des Règles

### Mettre à jour depuis GitHub

```bash
# 1. Fetch les dernières règles
docker exec manalytics-api-1 python scripts/fetch_archetype_rules.py

# 2. Backup les règles actuelles
docker exec manalytics-db-1 pg_dump -U manalytics -t manalytics.archetype_rules --data-only manalytics > rules_backup.sql

# 3. Migrer les nouvelles règles
docker exec manalytics-api-1 python scripts/migrate_rules.py

# 4. Vérifier
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT f.name, COUNT(*) FROM manalytics.archetype_rules r 
JOIN manalytics.archetypes a ON r.archetype_id = a.id 
JOIN manalytics.formats f ON a.format_id = f.id 
GROUP BY f.name;"
```

### Ajouter des règles custom

```sql
-- Exemple : Ajouter une règle pour un nouvel archetype
INSERT INTO manalytics.archetypes (format_id, name, display_name)
VALUES (
  (SELECT id FROM manalytics.formats WHERE name = 'modern'),
  'CustomDeck',
  'My Custom Deck'
);

INSERT INTO manalytics.archetype_rules (archetype_id, rule_type, rule_data)
VALUES (
  (SELECT id FROM manalytics.archetypes WHERE name = 'CustomDeck'),
  'detection',
  '{"include": [{"name": "Lightning Bolt", "min": 4}]}'::jsonb
);
```

## 📋 Logs et Debugging

### Consulter les logs

```bash
# Logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f api --tail 100

# Logs avec timestamps
docker-compose logs -t api | grep ERROR

# Sauvegarder les logs
docker-compose logs > logs_$(date +%Y%m%d).txt
```

### Debug avancé

```bash
# Activer le mode debug FastAPI
docker exec manalytics-api-1 bash -c "export DEBUG=true && uvicorn src.api.app:app --reload"

# Requête SQL lente
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT query, calls, mean_exec_time, max_exec_time 
FROM pg_stat_statements 
WHERE mean_exec_time > 100 
ORDER BY mean_exec_time DESC 
LIMIT 10;"

# Analyse d'un deck spécifique
docker exec -it manalytics-api-1 python -c "
from src.analyzers.archetype_detector import ArchetypeDetector
detector = ArchetypeDetector()
deck = [{'name': 'Lightning Bolt', 'quantity': 4}, {'name': 'Goblin Guide', 'quantity': 4}]
result = detector.detect_archetype(deck, 'modern')
print(f'Detected: {result}')
"
```

### Problèmes courants

| Symptôme | Vérification | Solution |
|----------|--------------|----------|
| API lente | `docker stats` | Augmenter RAM/CPU |
| Scraping échoue | Logs worker | Vérifier credentials |
| DB full | `df -h` | Nettoyer vieux data |
| Auth fails | Logs API | Vérifier JWT secret |

## 🚀 Scripts Utiles

### Rapport quotidien

```bash
cat > /opt/manalytics/daily_report.sh << 'EOF'
#!/bin/bash
echo "=== MANALYTICS DAILY REPORT $(date) ==="
echo ""
echo "System Status:"
docker-compose ps
echo ""
echo "Database Stats:"
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT 
  (SELECT COUNT(*) FROM manalytics.tournaments WHERE date >= CURRENT_DATE - 1) as new_tournaments,
  (SELECT COUNT(*) FROM manalytics.decklists WHERE created_at >= NOW() - INTERVAL '24 hours') as new_decks,
  (SELECT COUNT(DISTINCT player_id) FROM manalytics.decklists WHERE created_at >= NOW() - INTERVAL '24 hours') as active_players;"
echo ""
echo "Top Archetypes (Last 7 days):"
docker exec manalytics-db-1 psql -U manalytics -c "
SELECT a.name, f.name as format, COUNT(*) as decks
FROM manalytics.decklists d
JOIN manalytics.archetypes a ON d.archetype_id = a.id
JOIN manalytics.formats f ON a.format_id = f.id
JOIN manalytics.tournaments t ON d.tournament_id = t.id
WHERE t.date >= CURRENT_DATE - 7
GROUP BY a.name, f.name
ORDER BY decks DESC
LIMIT 10;"
EOF

chmod +x /opt/manalytics/daily_report.sh
```

---

Pour plus d'informations sur la résolution de problèmes, voir [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).