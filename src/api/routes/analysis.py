from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from src.api.auth import get_current_user
from src.analyzers.meta_analyzer import MetaAnalyzer
from src.analyzers.tournament_analyzer import TournamentAnalyzer
from database.db_pool import get_db_connection
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ================================================================================
# META DISTRIBUTION ENDPOINTS
# ================================================================================

@router.get("/meta/{format_name}")
async def get_meta_distribution(
    format_name: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    min_presence: float = Query(0.5, ge=0, le=100, description="Minimum % presence to include")
):
    """
    Get the metagame breakdown for a specific format.
    
    Returns:
        List of archetypes with their meta share, sorted by popularity
    """
    with get_db_connection() as conn:
        analyzer = MetaAnalyzer(conn)
        meta_data = analyzer.get_meta_breakdown(format_name, days)
        
        # Si pas de données, retourner une réponse vide mais valide
        if not meta_data:
            return {
                "format": format_name,
                "period_days": days,
                "total_decks": 0,
                "unique_archetypes": 0,
                "data": [],
                "generated_at": datetime.utcnow().isoformat(),
                "message": "No data available. Please run the scraper to collect tournament data."
            }
        
        # Filter by minimum presence
        filtered_meta = [
            arch for arch in meta_data 
            if arch['meta_share'] >= min_presence
        ]
        
        # Add additional calculated fields
        total_decks = sum(arch['deck_count'] for arch in filtered_meta)
        for arch in filtered_meta:
            arch['rank'] = filtered_meta.index(arch) + 1
            arch['tier'] = _calculate_tier(arch['meta_share'])
        
        return {
            "format": format_name,
            "period_days": days,
            "total_decks": total_decks,
            "unique_archetypes": len(meta_data),
            "data": filtered_meta,
            "generated_at": datetime.utcnow().isoformat()
        }

@router.get("/meta/{format_name}/trends")
async def get_meta_trends(
    format_name: str,
    days: int = Query(30, ge=7, le=365),
    interval: str = Query("daily", enum=["daily", "weekly"])
):
    """
    Get metagame trends over time showing the rise and fall of archetypes.
    """
    with get_db_connection() as conn:
        analyzer = MetaAnalyzer(conn)
        trends = analyzer.get_meta_trends(format_name, days, interval)
        
        return {
            "format": format_name,
            "period_days": days,
            "interval": interval,
            "trends": trends,
            "generated_at": datetime.utcnow().isoformat()
        }

@router.get("/meta/{format_name}/diversity")
async def get_meta_diversity(
    format_name: str,
    days: int = Query(30, ge=1, le=365)
):
    """
    Calculate diversity metrics for the metagame.
    
    Returns:
        - Herfindahl-Hirschman Index (HHI)
        - Number of viable archetypes (>2% meta share)
        - Top 8 concentration
    """
    with get_db_connection() as conn:
        analyzer = MetaAnalyzer(conn)
        meta_data = analyzer.get_meta_breakdown(format_name, days)
        
        if not meta_data:
            raise HTTPException(status_code=404, detail="No data found for this format/period")
        
        # Calculate HHI (sum of squared market shares)
        hhi = sum((arch['meta_share'] ** 2) for arch in meta_data)
        
        # Count viable archetypes
        viable_archetypes = len([a for a in meta_data if a['meta_share'] >= 2.0])
        
        # Top 8 concentration
        top_8_share = sum(a['meta_share'] for a in meta_data[:8])
        
        return {
            "format": format_name,
            "period_days": days,
            "metrics": {
                "herfindahl_index": round(hhi, 2),
                "viable_archetypes": viable_archetypes,
                "total_archetypes": len(meta_data),
                "top_8_concentration": round(top_8_share, 2),
                "diversity_rating": _calculate_diversity_rating(hhi)
            },
            "generated_at": datetime.utcnow().isoformat()
        }

# ================================================================================
# ARCHETYPE SPECIFIC ENDPOINTS
# ================================================================================

@router.get("/archetype/{format_name}/{archetype_name}")
async def get_archetype_details(
    format_name: str,
    archetype_name: str,
    days: int = Query(30, ge=1, le=365)
):
    """
    Get detailed statistics for a specific archetype.
    """
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        details = analyzer.get_archetype_performance(format_name, archetype_name, days)
        
        if not details:
            raise HTTPException(status_code=404, detail="Archetype not found")
        
        return {
            "format": format_name,
            "archetype": archetype_name,
            "period_days": days,
            "statistics": details,
            "generated_at": datetime.utcnow().isoformat()
        }

@router.get("/archetype/{format_name}/{archetype_name}/decklists")
async def get_archetype_decklists(
    format_name: str,
    archetype_name: str,
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    min_wins: Optional[int] = Query(None, ge=0, le=5)
):
    """
    Get recent successful decklists for an archetype.
    """
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        decklists = analyzer.get_archetype_decklists(
            format_name, archetype_name, limit, days, min_wins
        )
        
        return {
            "format": format_name,
            "archetype": archetype_name,
            "count": len(decklists),
            "decklists": decklists
        }

@router.get("/archetype/{format_name}/{archetype_name}/cards")
async def get_archetype_card_stats(
    format_name: str,
    archetype_name: str,
    days: int = Query(30, ge=1, le=365),
    card_type: str = Query("all", enum=["all", "mainboard", "sideboard"])
):
    """
    Get card frequency statistics for an archetype.
    Shows most played cards and average quantities.
    """
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        card_stats = analyzer.get_archetype_card_stats(
            format_name, archetype_name, days, card_type
        )
        
        return {
            "format": format_name,
            "archetype": archetype_name,
            "period_days": days,
            "card_type": card_type,
            "cards": card_stats
        }

# ================================================================================
# TOURNAMENT ENDPOINTS
# ================================================================================

@router.get("/tournaments/{format_name}")
async def get_recent_tournaments(
    format_name: str,
    limit: int = Query(20, ge=1, le=100),
    source: Optional[str] = Query(None, enum=["mtgo", "melee"])
):
    """
    Get recent tournaments for a format.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    t.id, t.name, t.date, t.players_count,
                    s.name as source, t.url
                FROM manalytics.tournaments t
                JOIN manalytics.formats f ON t.format_id = f.id
                JOIN manalytics.sources s ON t.source_id = s.id
                WHERE f.name = %s
                {source_filter}
                ORDER BY t.date DESC
                LIMIT %s
            """
            
            params = [format_name]
            source_filter = ""
            
            if source:
                source_filter = "AND s.name = %s"
                params.append(source)
            
            query = query.format(source_filter=source_filter)
            params.append(limit)
            
            cursor.execute(query, params)
            
            tournaments = []
            for row in cursor.fetchall():
                tournaments.append({
                    "id": str(row[0]),
                    "name": row[1],
                    "date": row[2].isoformat(),
                    "players_count": row[3],
                    "source": row[4],
                    "url": row[5]
                })
            
            return {
                "format": format_name,
                "count": len(tournaments),
                "tournaments": tournaments
            }

@router.get("/tournaments/{tournament_id}/results")
async def get_tournament_results(tournament_id: str):
    """
    Get detailed results for a specific tournament.
    """
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        results = analyzer.get_tournament_details(tournament_id)
        
        if not results:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        return results

# ================================================================================
# MATCHUP ENDPOINTS
# ================================================================================

@router.get("/matchups/{format_name}")
async def get_matchup_matrix(
    format_name: str,
    days: int = Query(60, ge=7, le=365),
    min_matches: int = Query(20, ge=5, le=100)
):
    """
    Get matchup win rates between archetypes.
    Only includes matchups with sufficient data.
    """
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        matchups = analyzer.calculate_matchup_matrix(format_name, days, min_matches)
        
        return {
            "format": format_name,
            "period_days": days,
            "min_matches": min_matches,
            "matchups": matchups,
            "generated_at": datetime.utcnow().isoformat()
        }

@router.get("/matchups/{format_name}/{archetype_name}")
async def get_archetype_matchups(
    format_name: str,
    archetype_name: str,
    days: int = Query(60, ge=7, le=365)
):
    """
    Get all matchup data for a specific archetype.
    """
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        matchups = analyzer.get_archetype_matchups(format_name, archetype_name, days)
        
        if not matchups:
            raise HTTPException(status_code=404, detail="No matchup data found")
        
        return {
            "format": format_name,
            "archetype": archetype_name,
            "period_days": days,
            "matchups": matchups,
            "generated_at": datetime.utcnow().isoformat()
        }

# ================================================================================
# COMPARISON ENDPOINTS
# ================================================================================

@router.post("/compare/archetypes")
async def compare_archetypes(
    format_name: str,
    archetypes: List[str],
    days: int = Query(30, ge=1, le=365)
):
    """
    Compare multiple archetypes across various metrics.
    """
    if len(archetypes) < 2 or len(archetypes) > 10:
        raise HTTPException(status_code=400, detail="Please provide 2-10 archetypes to compare")
    
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        comparison = analyzer.compare_archetypes(format_name, archetypes, days)
        
        return {
            "format": format_name,
            "archetypes": archetypes,
            "period_days": days,
            "comparison": comparison,
            "generated_at": datetime.utcnow().isoformat()
        }

# ================================================================================
# EXPORT ENDPOINTS
# ================================================================================

@router.get("/export/{format_name}/csv")
async def export_meta_csv(
    format_name: str,
    days: int = Query(30, ge=1, le=365),
    current_user = Depends(get_current_user)  # Require auth for exports
):
    """
    Export meta data as CSV (requires authentication).
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    with get_db_connection() as conn:
        analyzer = MetaAnalyzer(conn)
        meta_data = analyzer.get_meta_breakdown(format_name, days)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['rank', 'archetype', 'deck_count', 'meta_share'])
        writer.writeheader()
        
        for i, arch in enumerate(meta_data):
            writer.writerow({
                'rank': i + 1,
                'archetype': arch['archetype'],
                'deck_count': arch['deck_count'],
                'meta_share': f"{arch['meta_share']:.2f}%"
            })
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=meta_{format_name}_{days}d.csv"
            }
        )

# ================================================================================
# HELPER FUNCTIONS
# ================================================================================

def _calculate_tier(meta_share: float) -> str:
    """Calculate tier based on meta share percentage."""
    if meta_share >= 15:
        return "Tier 0"
    elif meta_share >= 10:
        return "Tier 1"
    elif meta_share >= 5:
        return "Tier 2"
    elif meta_share >= 2:
        return "Tier 3"
    else:
        return "Tier 4"

def _calculate_diversity_rating(hhi: float) -> str:
    """Rate diversity based on HHI."""
    if hhi < 1000:
        return "Highly Diverse"
    elif hhi < 1500:
        return "Diverse"
    elif hhi < 2500:
        return "Moderately Concentrated"
    else:
        return "Highly Concentrated"