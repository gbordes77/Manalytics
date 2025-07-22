#!/bin/bash

# Cache cleanup script for Manalytics

set -e

echo "🧹 Cleaning Manalytics cache..."

# Default cache directory
CACHE_DIR="/tmp/manalytics_cache"

# Clean cache directory
if [ -d "$CACHE_DIR" ]; then
    echo "Cleaning cache directory: $CACHE_DIR"
    rm -rf "$CACHE_DIR"
    echo "✅ Cache directory cleaned"
else
    echo "ℹ️  Cache directory not found: $CACHE_DIR"
fi

# Clean Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✅ Python cache cleaned"

# Clean logs older than 7 days
if [ -d "logs" ]; then
    echo "Cleaning old logs..."
    find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    echo "✅ Old logs cleaned"
fi

# Clean temporary analysis files
echo "Cleaning temporary analysis files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
echo "✅ Temporary files cleaned"

echo "🎉 Cache cleanup complete!"
