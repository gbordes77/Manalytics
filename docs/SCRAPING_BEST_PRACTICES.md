# Best Practices for MTG Tournament Scraping

## MTGO Scraping

### ⚠️ Critical Lesson: Never Guess Tournament IDs

**Problem encountered on 2025-07-25:**
When trying to recover missing duplicate tournaments, we attempted to guess tournament IDs based on existing ones. This failed because MTGO IDs are not sequential.

**Example:**
```
Date: July 19, 2025
- Tournament 1: ID 12803693
- Tournament 2: ID 12803688 (found)
- We guessed: ID 12803689 ❌ WRONG
- Actual ID: 12803671 ✅

Date: July 12, 2025  
- We guessed: ID 12802790 ❌ WRONG
- Actual IDs: 12802811, 12802816 ✅
```

### Why This Happened
1. MTGO assigns IDs from their internal system
2. IDs can have gaps of 5, 10, 17, or any number
3. Multiple tournaments on the same day don't have consecutive IDs

### Correct Approach
```python
# ALWAYS parse the listing page
tournaments = scraper._get_tournament_list(start_date, end_date)

# NEVER construct URLs manually like this:
# url = f"https://www.mtgo.com/decklist/standard-challenge-32-2025-07-19{guessed_id}"
```

### How Our Scraper Handles Duplicates
The enhanced scraper now includes tournament IDs in filenames:
- Before: `20250719_Standard_Challenge_32.json` (overwrites duplicates!)
- After: `20250719_Standard_Challenge_32_12803693.json` (unique!)

## Melee Scraping

### API Slowness
- Melee.gg API is inherently slow (30+ seconds per request)
- This is normal and expected
- Don't interrupt the scraper thinking it's stuck

### Authentication
- Credentials stored in `api_credentials/melee_login.json`
- Format: `{"login": "email", "mdp": "password"}`
- Cookies are persisted to reduce re-authentication

## General Best Practices

1. **Always verify tournament counts** against official websites
2. **Use force-redownload carefully** - it bypasses the tracking system
3. **Run scrapers in background** with output logs for long operations
4. **Check for duplicates** - some days have multiple tournaments
5. **Monitor progress** through log files, not console output

## Troubleshooting

### Missing tournaments?
1. Check the official listing page directly
2. Look for tournaments on the same date (duplicates)
3. Verify the scraper found all tournaments in logs
4. Never try to construct URLs manually

### Scraper seems stuck?
1. Check if it's actually making progress in the log file
2. Melee API calls can take 30+ seconds each
3. MTGO scraping ~27 tournaments takes 2-3 minutes total

### File naming conflicts?
The enhanced scrapers now use unique IDs in filenames to prevent overwrites.