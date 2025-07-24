"""
API endpoints for generating and serving visualizations.
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import asyncio
from pathlib import Path

from src.visualizers.matchup_matrix import MetaVisualizer
from src.analyzers.meta_analyzer import MetaAnalyzer
from src.analyzers.tournament_analyzer import TournamentAnalyzer
from database.db_pool import get_db_connection

router = APIRouter(prefix="/api/visualizations", tags=["visualizations"])

@router.get("/matchup-matrix/{format_name}")
async def generate_matchup_matrix(
    format_name: str,
    days: int = Query(60, ge=7, le=365),
    min_matches: int = Query(20, ge=5, le=100)
):
    """
    Generate and return a matchup matrix heatmap.
    """
    visualizer = MetaVisualizer()
    
    # Get matchup data
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        matchup_data = analyzer.calculate_matchup_matrix(format_name, days, min_matches)
    
    if not matchup_data:
        raise HTTPException(status_code=404, detail="No matchup data available")
    
    # Generate visualization
    loop = asyncio.get_event_loop()
    filepath = await loop.run_in_executor(
        None, 
        visualizer.create_matchup_heatmap,
        matchup_data,
        format_name
    )
    
    if not filepath or not filepath.exists():
        raise HTTPException(status_code=500, detail="Failed to generate visualization")
    
    return FileResponse(
        filepath,
        media_type="image/png",
        filename=filepath.name
    )

@router.get("/meta-distribution/{format_name}")
async def generate_meta_distribution(
    format_name: str,
    days: int = Query(30, ge=1, le=365),
    top_n: int = Query(8, ge=5, le=15)
):
    """
    Generate and return a meta distribution pie chart.
    """
    visualizer = MetaVisualizer()
    
    # Get meta data
    with get_db_connection() as conn:
        analyzer = MetaAnalyzer(conn)
        meta_data = analyzer.get_meta_breakdown(format_name, days)
    
    if not meta_data:
        raise HTTPException(status_code=404, detail="No meta data available")
    
    # Generate visualization
    loop = asyncio.get_event_loop()
    filepath = await loop.run_in_executor(
        None,
        visualizer.create_meta_pie_chart,
        meta_data,
        format_name,
        top_n
    )
    
    if not filepath or not filepath.exists():
        raise HTTPException(status_code=500, detail="Failed to generate visualization")
    
    return FileResponse(
        filepath,
        media_type="image/png",
        filename=filepath.name
    )

@router.get("/trends/{format_name}")
async def generate_trend_chart(
    format_name: str,
    days: int = Query(30, ge=7, le=365),
    interval: str = Query("daily", enum=["daily", "weekly"]),
    top_n: int = Query(6, ge=3, le=10)
):
    """
    Generate and return a trend chart showing archetype evolution.
    """
    visualizer = MetaVisualizer()
    
    # Get trend data
    with get_db_connection() as conn:
        analyzer = MetaAnalyzer(conn)
        trend_data = analyzer.get_meta_trends(format_name, days, interval)
    
    if not trend_data:
        raise HTTPException(status_code=404, detail="No trend data available")
    
    # Generate visualization
    loop = asyncio.get_event_loop()
    filepath = await loop.run_in_executor(
        None,
        visualizer.create_trend_chart,
        trend_data,
        format_name,
        top_n
    )
    
    if not filepath or not filepath.exists():
        raise HTTPException(status_code=500, detail="Failed to generate visualization")
    
    return FileResponse(
        filepath,
        media_type="image/png",
        filename=filepath.name
    )

@router.get("/performance-radar/{format_name}")
async def generate_performance_radar(
    format_name: str,
    days: int = Query(30, ge=1, le=365),
    archetypes: Optional[str] = Query(None, description="Comma-separated list of archetypes")
):
    """
    Generate a radar chart comparing archetype performance.
    """
    visualizer = MetaVisualizer()
    
    # Get performance data
    with get_db_connection() as conn:
        analyzer = TournamentAnalyzer(conn)
        
        if archetypes:
            archetype_list = [a.strip() for a in archetypes.split(',')]
        else:
            # Get top archetypes by presence
            meta_analyzer = MetaAnalyzer(conn)
            meta_data = analyzer.get_meta_breakdown(format_name, days)
            archetype_list = [d['archetype'] for d in meta_data[:6]]
        
        # Get stats for each archetype
        archetype_stats = {}
        for arch in archetype_list:
            stats = analyzer.get_archetype_performance(format_name, arch, days)
            if stats:
                archetype_stats[arch] = stats
    
    if not archetype_stats:
        raise HTTPException(status_code=404, detail="No performance data available")
    
    # Generate visualization
    loop = asyncio.get_event_loop()
    filepath = await loop.run_in_executor(
        None,
        visualizer.create_performance_radar,
        archetype_stats,
        format_name
    )
    
    if not filepath or not filepath.exists():
        raise HTTPException(status_code=500, detail="Failed to generate visualization")
    
    return FileResponse(
        filepath,
        media_type="image/png",
        filename=filepath.name
    )