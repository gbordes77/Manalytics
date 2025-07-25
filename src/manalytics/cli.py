#!/usr/bin/env python3
"""
Manalytics CLI - Main entry point for all operations
"""
import click
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manalytics.orchestrator import Orchestrator
from manalytics.config import LOG_LEVEL, ENABLED_FORMATS

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.pass_context
def cli(ctx, debug):
    """Manalytics - MTG Tournament Analysis Platform"""
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)

@cli.command()
@click.option('--format', 'format_name', required=True, 
              type=click.Choice(ENABLED_FORMATS),
              help='Tournament format to scrape')
@click.option('--days', default=7, help='Number of days to scrape')
@click.option('--platform', type=click.Choice(['all', 'mtgo', 'melee']), 
              default='all', help='Platform(s) to scrape')
@click.pass_context
def scrape(ctx, format_name, days, platform):
    """Scrape tournament data from MTGO and/or Melee"""
    orchestrator = Orchestrator()
    click.echo(f"🔍 Scraping {format_name} tournaments from last {days} days...")
    
    results = orchestrator.scrape_tournaments(
        format_name=format_name,
        days=days,
        platforms=[platform] if platform != 'all' else ['mtgo', 'melee']
    )
    
    total = sum(len(r.get('tournaments', [])) for r in results.values())
    click.echo(f"✅ Scraped {total} tournaments successfully!")

@cli.command()
@click.option('--format', 'format_name', required=True,
              type=click.Choice(ENABLED_FORMATS),
              help='Tournament format to analyze')
@click.pass_context
def analyze(ctx, format_name):
    """Analyze tournament data and generate reports"""
    orchestrator = Orchestrator()
    click.echo(f"📊 Analyzing {format_name} metagame...")
    
    results = orchestrator.analyze_metagame(format_name)
    
    if results:
        click.echo(f"✅ Analysis complete!")
        click.echo(f"📈 Top archetypes:")
        for arch in results.get('top_archetypes', [])[:5]:
            click.echo(f"  - {arch['name']}: {arch['percentage']:.1f}%")

@cli.command()
@click.option('--format', 'format_name', required=True,
              type=click.Choice(ENABLED_FORMATS),
              help='Tournament format to process')
@click.option('--days', default=7, help='Number of days to process')
@click.pass_context
def pipeline(ctx, format_name, days):
    """Run complete pipeline: scrape -> parse -> analyze -> visualize"""
    orchestrator = Orchestrator()
    
    click.echo(f"🚀 Running complete pipeline for {format_name}...")
    click.echo("=" * 50)
    
    # Step 1: Scrape
    click.echo("\n📥 Step 1/4: Scraping tournaments...")
    scrape_results = orchestrator.scrape_tournaments(format_name, days)
    total_tournaments = sum(len(r.get('tournaments', [])) for r in scrape_results.values())
    click.echo(f"✓ Found {total_tournaments} tournaments")
    
    # Step 2: Parse & Detect Archetypes
    click.echo("\n🔍 Step 2/4: Parsing decks and detecting archetypes...")
    parse_results = orchestrator.parse_and_detect(scrape_results, format_name)
    click.echo(f"✓ Processed {parse_results['total_decks']} decks")
    
    # Step 3: Analyze
    click.echo("\n📊 Step 3/4: Analyzing metagame...")
    analysis = orchestrator.analyze_metagame(format_name)
    click.echo(f"✓ Identified {len(analysis['archetypes'])} archetypes")
    
    # Step 4: Visualize
    click.echo("\n📈 Step 4/4: Generating visualizations...")
    viz_results = orchestrator.generate_visualizations(analysis, format_name)
    click.echo(f"✓ Generated {len(viz_results['files'])} visualization files")
    
    click.echo("\n" + "=" * 50)
    click.echo(f"✅ Pipeline complete! Check data/output/ for results.")

@cli.command()
@click.pass_context
def status(ctx):
    """Check system status and recent data"""
    orchestrator = Orchestrator()
    status = orchestrator.get_system_status()
    
    click.echo("📊 Manalytics System Status")
    click.echo("=" * 50)
    click.echo(f"🗄️  Database: {status['database']}")
    click.echo(f"📁 Data directory: {status['data_dir']}")
    click.echo(f"📈 Recent tournaments: {status['recent_tournaments']}")
    click.echo(f"🎯 Archetypes loaded: {status['archetypes_count']}")

@cli.command()
@click.option('--host', default='0.0.0.0', help='API host')
@click.option('--port', default=8000, help='API port')
@click.pass_context
def serve(ctx, host, port):
    """Start the API server"""
    click.echo(f"🚀 Starting Manalytics API on {host}:{port}...")
    import uvicorn
    uvicorn.run("manalytics.api.app:app", host=host, port=port, reload=True)

if __name__ == '__main__':
    cli()