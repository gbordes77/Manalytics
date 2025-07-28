"""
FastAPI application for Manalytics API.

Provides endpoints for:
- Matchup data and matrices
- Metagame distribution
- Tournament insights and recommendations
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from ..listener.tournament_matcher import TournamentMatcher
from ..listener.matchup_enricher import MatchupEnricher
from ..analyzers.matchup_calculator import MatchupCalculator
from ..cache.reader import CacheReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Manalytics API",
    description="MTG Tournament Analysis Platform API",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
tournament_matcher = TournamentMatcher()
matchup_enricher = MatchupEnricher()
cache_reader = CacheReader()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Manalytics API",
        "version": "3.0.0",
        "endpoints": {
            "/api/matchups": "Get matchup matrix",
            "/api/meta": "Get metagame distribution",
            "/api/insights": "Get competitive insights",
            "/api/performance": "Get archetype performance stats"
        }
    }


@app.get("/api/matchups")
async def get_matchups(
    format: str = Query("standard", description="Tournament format"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_matches: int = Query(10, description="Minimum matches for significance")
) -> Dict:
    """
    Get matchup matrix with win rates between archetypes.
    
    Returns data like:
    - "Dimir vs Izzet: 65% win rate over 47 matches"
    - Confidence intervals for statistical significance
    """
    try:
        # Default date range: July 1-21, 2025
        if not start_date:
            start_date = "2025-07-01"
        if not end_date:
            end_date = "2025-07-21"
            
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get matches from listener data
        tournament_matches = tournament_matcher.match_all_listener_data((start, end))
        
        if not tournament_matches:
            # Create sample data for demonstration
            logger.info("No listener data found, creating sample data...")
            tournament_matcher.create_sample_listener_data()
            tournament_matches = tournament_matcher.match_all_listener_data((start, end))
        
        # Enrich with archetype data
        enriched_data = matchup_enricher.enrich_all_matches(tournament_matches)
        
        # Calculate matchup statistics
        calculator = MatchupCalculator()
        calculator.process_matches(enriched_data)
        
        # Get results
        matrix = calculator.get_matchup_matrix()
        significant = calculator.get_significant_matchups(min_matches)
        summary = calculator.get_summary_stats()
        
        return {
            "format": format,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "summary": summary,
            "matchup_matrix": matrix,
            "significant_matchups": significant
        }
        
    except Exception as e:
        logger.error(f"Error getting matchups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meta")
async def get_meta_distribution(
    format: str = Query("standard", description="Tournament format"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> Dict:
    """
    Get current metagame distribution.
    
    Returns percentage of each archetype in the meta.
    """
    try:
        # Default to current date if not specified
        if not end_date:
            end_date = "2025-07-21"
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get meta snapshot from cache
        meta_snapshot = cache_reader.get_meta_snapshot(format, end)
        
        # Calculate percentages
        total_decks = meta_snapshot.get('total_decks', 0)
        archetypes = meta_snapshot.get('archetypes', {})
        
        distribution = {}
        for archetype, count in archetypes.items():
            percentage = (count / total_decks * 100) if total_decks > 0 else 0
            distribution[archetype] = {
                "count": count,
                "percentage": round(percentage, 1)
            }
        
        # Sort by percentage
        sorted_distribution = dict(sorted(
            distribution.items(),
            key=lambda x: x[1]['percentage'],
            reverse=True
        ))
        
        return {
            "format": format,
            "date": end_date,
            "total_decks": total_decks,
            "total_archetypes": len(archetypes),
            "distribution": sorted_distribution
        }
        
    except Exception as e:
        logger.error(f"Error getting meta distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights")
async def get_insights(
    format: str = Query("standard", description="Tournament format")
) -> Dict:
    """
    Get competitive insights and recommendations.
    
    Returns actionable insights based on current meta and matchup data.
    """
    try:
        # Get current meta
        meta_response = await get_meta_distribution(format=format)
        distribution = meta_response['distribution']
        
        # Get matchup data
        matchup_response = await get_matchups(format=format)
        performance = MatchupCalculator().get_archetype_performance()
        
        insights = []
        
        # Top meta share insight
        top_archetypes = list(distribution.keys())[:3]
        insights.append({
            "type": "meta_dominance",
            "title": "Dominant Archetypes",
            "description": f"The top 3 archetypes ({', '.join(top_archetypes)}) make up "
                          f"{sum(distribution[a]['percentage'] for a in top_archetypes):.1f}% of the meta",
            "recommendation": "Consider playing one of these or a deck that beats them"
        })
        
        # Best performer insight
        if performance:
            best_performer = list(performance.keys())[0]
            best_stats = performance[best_performer]
            insights.append({
                "type": "best_performer",
                "title": "Highest Win Rate",
                "description": f"{best_performer} has {best_stats['overall_win_rate']}% win rate "
                               f"over {best_stats['total_matches']} matches",
                "recommendation": f"Strong choice if you can pilot {best_performer} well"
            })
        
        # Under-the-radar insight
        for archetype, stats in performance.items():
            meta_share = distribution.get(archetype, {}).get('percentage', 0)
            if meta_share < 5 and stats['overall_win_rate'] > 52:
                insights.append({
                    "type": "hidden_gem",
                    "title": "Under-the-Radar Performer",
                    "description": f"{archetype} has {stats['overall_win_rate']}% win rate "
                                  f"but only {meta_share}% meta share",
                    "recommendation": "Could be a great meta choice with surprise factor"
                })
                break
        
        return {
            "format": format,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/performance")
async def get_archetype_performance(
    format: str = Query("standard", description="Tournament format"),
    min_matches: int = Query(20, description="Minimum matches for inclusion")
) -> Dict:
    """
    Get performance statistics for all archetypes.
    
    Returns win rates with confidence intervals.
    """
    try:
        # Get matchup data
        matchup_response = await get_matchups(format=format)
        
        # Get calculator and process data
        calculator = MatchupCalculator()
        
        # Re-process if needed (normally would be cached)
        start = datetime(2025, 7, 1)
        end = datetime(2025, 7, 21)
        tournament_matches = tournament_matcher.match_all_listener_data((start, end))
        
        if tournament_matches:
            enriched_data = matchup_enricher.enrich_all_matches(tournament_matches)
            calculator.process_matches(enriched_data)
        
        # Get performance stats
        performance = calculator.get_archetype_performance()
        
        # Filter by minimum matches
        filtered_performance = {
            archetype: stats
            for archetype, stats in performance.items()
            if stats['total_matches'] >= min_matches
        }
        
        return {
            "format": format,
            "min_matches": min_matches,
            "archetypes": filtered_performance
        }
        
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)