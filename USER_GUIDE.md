# 📚 Manalytics User Guide

Welcome to Manalytics - Your MTG Meta Analysis Platform!

---

## 🚀 1. QUICK START

### Starting the System

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```bash
   docker-compose ps
   ```
   
   You should see:
   - `manalytics-api` - Running on port 8000
   - `manalytics-db` - PostgreSQL database
   - `manalytics-redis` - Cache server
   - `manalytics-worker` - Background processor

3. **Check system health:**
   ```bash
   curl http://localhost:8000/health
   ```

### First Scraping

1. **Initialize archetype rules:**
   ```bash
   docker-compose exec api python scripts/fetch_archetype_rules.py
   docker-compose exec api python scripts/migrate_rules.py
   ```

2. **Create your admin account:**
   ```bash
   docker-compose exec api python scripts/manage_users.py create-default-admin
   # Default: admin / changeme (CHANGE THIS!)
   ```

3. **Run your first scraping:**
   ```bash
   # Scrape last 7 days of Modern tournaments
   docker-compose exec worker python scripts/run_pipeline.py --format modern --days 7
   ```

### Viewing Results

1. **Via API (see section 2 for authentication):**
   ```bash
   # Get recent decks
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/decks
   
   # Get meta snapshot
   curl http://localhost:8000/api/analysis/meta/modern
   ```

2. **Via Database:**
   ```bash
   docker-compose exec db psql -U manalytics -c \
     "SELECT archetype_name, COUNT(*) FROM manalytics.decklists 
      GROUP BY archetype_name ORDER BY COUNT(*) DESC LIMIT 10;"
   ```

---

## 🔐 2. API USAGE

### Authentication

Manalytics uses JWT (JSON Web Tokens) for API authentication.

1. **Get an access token:**
   ```bash
   # Login with your credentials
   TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=changeme" | jq -r .access_token)
   
   echo "Your token: $TOKEN"
   ```

2. **Use the token in requests:**
   ```bash
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/decks
   ```

### Example API Requests

#### Get Tournament Results
```bash
# List recent tournaments
curl "http://localhost:8000/api/tournaments?format=modern&limit=10"

# Get specific tournament
curl "http://localhost:8000/api/tournaments/123"
```

#### Search Decks
```bash
# Search by archetype
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/decks?archetype=Burn&format=modern"

# Search by cards
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/decks/search?cards=Lightning+Bolt,Ragavan"

# Get deck details
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/decks/456"
```

#### Meta Analysis
```bash
# Get current meta breakdown
curl "http://localhost:8000/api/analysis/meta/modern?days=30"

# Response example:
{
  "format": "modern",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "total_decks": 1250,
  "archetypes": [
    {
      "name": "Ragavan Midrange",
      "count": 156,
      "percentage": 12.48,
      "avg_position": 3.2
    },
    {
      "name": "Amulet Titan",
      "count": 98,
      "percentage": 7.84,
      "avg_position": 5.1
    }
  ]
}
```

#### Matchup Data
```bash
# Get matchup grid
curl "http://localhost:8000/api/analysis/matchups/modern"

# Get specific matchup
curl "http://localhost:8000/api/analysis/matchup?deck1=Burn&deck2=Control"
```

### Typical Use Cases

#### 1. Track Deck Performance Over Time
```python
import httpx
import pandas as pd
from datetime import datetime, timedelta

# Get performance data
async with httpx.AsyncClient() as client:
    # Authenticate
    auth_resp = await client.post(
        "http://localhost:8000/api/auth/token",
        data={"username": "admin", "password": "changeme"}
    )
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get deck performance
    archetype = "Burn"
    resp = await client.get(
        f"http://localhost:8000/api/analysis/performance/{archetype}",
        headers=headers,
        params={"days": 30}
    )
    
    data = resp.json()
    df = pd.DataFrame(data["daily_performance"])
    print(f"{archetype} win rate: {data['overall_win_rate']}%")
```

#### 2. Find Decks with Specific Cards
```bash
# Find all decks playing Ragavan
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/decks/search?cards=Ragavan,+Nimble+Pilferer&format=modern"

# Find decks NOT playing Force of Negation
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/decks/search?exclude_cards=Force+of+Negation"
```

#### 3. Export Meta Report
```bash
# Get meta snapshot as CSV
curl "http://localhost:8000/api/analysis/meta/modern?format=csv" > meta_report.csv

# Get detailed matchup matrix
curl "http://localhost:8000/api/analysis/matchups/modern?format=json" > matchups.json
```

---

## ⚙️ 3. CONFIGURATION

### Supported Formats

Manalytics supports all major MTG formats:

- **modern** - Modern format
- **legacy** - Legacy format  
- **vintage** - Vintage format
- **pioneer** - Pioneer format
- **standard** - Standard format
- **pauper** - Pauper format

Configure in `run_pipeline.py`:
```python
SUPPORTED_FORMATS = ["modern", "legacy", "pioneer", "standard"]
```

### Scraping Frequency

Configure automated scraping via cron:

```bash
# Edit crontab
crontab -e

# Daily scraping at 2 AM for all formats
0 2 * * * /path/to/docker-compose exec worker python scripts/run_pipeline.py --format modern --days 1
0 3 * * * /path/to/docker-compose exec worker python scripts/run_pipeline.py --format legacy --days 1
```

Or use the scheduler script:
```bash
docker-compose exec worker python scripts/scheduler.py
```

### Customizing Archetype Rules

1. **View current rules:**
   ```bash
   docker-compose exec db psql -U manalytics -c \
     "SELECT name, format, key_cards FROM manalytics.archetype_rules;"
   ```

2. **Add custom rule:**
   ```sql
   INSERT INTO manalytics.archetype_rules (name, format, key_cards, rules)
   VALUES (
     'My Custom Deck',
     'modern',
     ARRAY['Card 1', 'Card 2'],
     '{"min_cards": 8, "required": ["Card 1"]}'::jsonb
   );
   ```

3. **Update existing rule:**
   ```bash
   docker-compose exec api python scripts/update_archetype_rule.py \
     --name "Burn" --add-card "Skewer the Critics"
   ```

### Environment Variables

Key configuration options in `.env`:

```bash
# API Settings
API_PORT=8000
API_WORKERS=4
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@host:5432/manalytics
DB_POOL_MIN=2
DB_POOL_MAX=10

# Redis Cache
REDIS_URL=redis://redis:6379
CACHE_TTL=3600

# Scraping
SCRAPE_DELAY=1.0
CONCURRENT_SCRAPERS=3
MTGO_TIMEOUT=30
MELEE_EMAIL=your@email.com
MELEE_PASSWORD=yourpassword

# Security
SECRET_KEY=your-secret-key
TOKEN_EXPIRE_HOURS=24
```

---

## 🔧 4. TROUBLESHOOTING

### Common Errors

#### "Connection refused" when accessing API
```bash
# Check if services are running
docker-compose ps

# Check API logs
docker-compose logs api

# Restart services
docker-compose restart api
```

#### "Authentication failed" during scraping
```bash
# Verify credentials
echo $MELEE_EMAIL
echo $MELEE_PASSWORD

# Test authentication manually
docker-compose exec api python -c "
from src.scrapers.melee_scraper import MeleeScraper
import asyncio
scraper = MeleeScraper()
print(asyncio.run(scraper.authenticate()))
"
```

#### "No archetype detected" for many decks
```bash
# Update archetype rules
docker-compose exec api python scripts/fetch_archetype_rules.py
docker-compose exec api python scripts/migrate_rules.py

# Check detection
docker-compose exec api python scripts/test_archetype_detection.py \
  --decklist-file test_deck.txt
```

#### Database connection errors
```bash
# Check database is running
docker-compose exec db pg_isready

# Check connections
docker-compose exec db psql -U manalytics -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Reset connections
docker-compose restart api worker
```

### Logs to Check

1. **API Logs:**
   ```bash
   docker-compose logs -f api
   # Look for: ERROR, WARNING, Failed request
   ```

2. **Worker Logs:**
   ```bash
   docker-compose logs -f worker
   # Look for: Scraping errors, Parse failures
   ```

3. **Database Logs:**
   ```bash
   docker-compose logs -f db
   # Look for: Connection limit, Lock timeouts
   ```

4. **Application Logs:**
   ```bash
   # Inside container
   docker-compose exec api tail -f /app/logs/manalytics.log
   ```

### Database Reset

**⚠️ WARNING: This will delete all data!**

```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Restart fresh
docker-compose up -d

# Re-initialize
docker-compose exec api python scripts/init_database.py
docker-compose exec api python scripts/fetch_archetype_rules.py
docker-compose exec api python scripts/migrate_rules.py
docker-compose exec api python scripts/manage_users.py create-default-admin
```

### Performance Issues

1. **Slow API responses:**
   ```bash
   # Check cache hit rate
   docker-compose exec redis redis-cli INFO stats
   
   # Check slow queries
   docker-compose exec db psql -U manalytics -c \
     "SELECT query, calls, mean_time FROM pg_stat_statements 
      ORDER BY mean_time DESC LIMIT 10;"
   ```

2. **Memory issues:**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   ```

3. **Scraping too slow:**
   ```bash
   # Increase concurrent scrapers
   export CONCURRENT_SCRAPERS=5
   
   # Decrease delay between requests
   export SCRAPE_DELAY=0.5
   ```

---

## 📊 5. ADVANCED USAGE

### Custom Visualizations

```python
from src.visualizations.matchup_heatmap import generate_matchup_heatmap

# Generate heatmap for specific date range
generate_matchup_heatmap(
    format_name="modern",
    start_date="2024-01-01",
    end_date="2024-01-31",
    min_matches=20,
    output_path="output/january_meta.png"
)
```

### Data Export

```bash
# Export all data as SQL dump
docker-compose exec db pg_dump -U manalytics manalytics > backup.sql

# Export specific data as CSV
docker-compose exec db psql -U manalytics -c \
  "COPY (SELECT * FROM manalytics.decklists WHERE format='modern') 
   TO STDOUT WITH CSV HEADER" > modern_decks.csv
```

### API Extensions

Create custom endpoints in `src/api/routes/custom.py`:

```python
from fastapi import APIRouter, Depends
from src.api.auth import get_current_active_user

router = APIRouter()

@router.get("/my-endpoint")
async def my_custom_endpoint(current_user = Depends(get_current_active_user)):
    # Your custom logic here
    return {"message": "Custom endpoint"}
```

---

## 🆘 6. GETTING HELP

### Resources

- **Documentation:** `/docs` (when API is running)
- **API Schema:** `/openapi.json`
- **Health Status:** `/health`
- **Metrics:** `/metrics`

### Contact

- **Issues:** GitHub Issues (when repository is public)
- **Email:** support@manalytics.com (when available)

### Community

- Join our Discord for discussions
- Check the FAQ for common questions
- Contribute to the project on GitHub

---

*Happy analyzing! May your meta reads be ever in your favor.* 🎴