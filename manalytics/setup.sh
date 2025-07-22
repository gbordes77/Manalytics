#!/bin/bash

# MTG Analytics Pipeline - Installation script for Unix/Linux/macOS
# This script clones the 6 required GitHub repositories and places them in the appropriate structure

# Colors for messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to clone a repository
clone_repo() {
    local repo_url=$1
    local target_dir=$2
    local repo_name=$(basename "$repo_url" .git)
    
    log_info "Cloning $repo_name to $target_dir..."
    
    if [ -d "$target_dir" ]; then
        log_warning "Directory $target_dir already exists. Checking if it's a git repo..."
        if [ -d "$target_dir/.git" ]; then
            log_info "Git repository found. Updating..."
            (cd "$target_dir" && git pull)
            return $?
        else
            log_warning "Directory exists but is not a git repo. Backing up and recloning..."
            mv "$target_dir" "${target_dir}_backup_$(date +%Y%m%d%H%M%S)"
        fi
    fi
    
    mkdir -p "$(dirname "$target_dir")"
    git clone "$repo_url" "$target_dir"
    return $?
}

# Check that git is installed
if ! command -v git &> /dev/null; then
    log_error "Git is not installed. Please install git and try again."
    exit 1
fi

# Base directory
BASE_DIR="$(pwd)"
log_info "Base directory: $BASE_DIR"

# Create installation report
REPORT_FILE="$BASE_DIR/installation_report.md"
mkdir -p "$(dirname "$REPORT_FILE")"

# Initialize report
cat > "$REPORT_FILE" << EOF
# MTG Analytics Pipeline Installation Report

Date: $(date)

## Repository Status

| Repository | Status | Path |
|------------|--------|--------|
EOF

# Clone each repository
success_count=0
failure_count=0

# Repository 1: mtg_decklist_scrapper
repo_url="https://github.com/fbettega/mtg_decklist_scrapper.git"
target_dir="data-collection/scraper/mtgo"
repo_name=$(basename "$repo_url" .git)

if clone_repo "$repo_url" "$target_dir"; then
    log_success "Repository $repo_name successfully cloned to $target_dir"
    echo "| $repo_name | ✅ Success | $target_dir |" >> "$REPORT_FILE"
    ((success_count++))
else
    log_error "Failed to clone $repo_name"
    echo "| $repo_name | ❌ Failed | $target_dir |" >> "$REPORT_FILE"
    ((failure_count++))
fi

# Repository 2: MTG_decklistcache
repo_url="https://github.com/fbettega/MTG_decklistcache.git"
target_dir="data-collection/raw-cache"
repo_name=$(basename "$repo_url" .git)

if clone_repo "$repo_url" "$target_dir"; then
    log_success "Repository $repo_name successfully cloned to $target_dir"
    echo "| $repo_name | ✅ Success | $target_dir |" >> "$REPORT_FILE"
    ((success_count++))
else
    log_error "Failed to clone $repo_name"
    echo "| $repo_name | ❌ Failed | $target_dir |" >> "$REPORT_FILE"
    ((failure_count++))
fi

# Repository 3: MTGODecklistCache
repo_url="https://github.com/Jiliac/MTGODecklistCache.git"
target_dir="data-collection/processed-cache"
repo_name=$(basename "$repo_url" .git)

if clone_repo "$repo_url" "$target_dir"; then
    log_success "Repository $repo_name successfully cloned to $target_dir"
    echo "| $repo_name | ✅ Success | $target_dir |" >> "$REPORT_FILE"
    ((success_count++))
else
    log_error "Failed to clone $repo_name"
    echo "| $repo_name | ❌ Failed | $target_dir |" >> "$REPORT_FILE"
    ((failure_count++))
fi

# Repository 4: MTGOArchetypeParser
repo_url="https://github.com/Badaro/MTGOArchetypeParser.git"
target_dir="data-treatment/parser"
repo_name=$(basename "$repo_url" .git)

if clone_repo "$repo_url" "$target_dir"; then
    log_success "Repository $repo_name successfully cloned to $target_dir"
    echo "| $repo_name | ✅ Success | $target_dir |" >> "$REPORT_FILE"
    ((success_count++))
else
    log_error "Failed to clone $repo_name"
    echo "| $repo_name | ❌ Failed | $target_dir |" >> "$REPORT_FILE"
    ((failure_count++))
fi

# Repository 5: MTGOFormatData
repo_url="https://github.com/Badaro/MTGOFormatData.git"
target_dir="data-treatment/format-rules"
repo_name=$(basename "$repo_url" .git)

if clone_repo "$repo_url" "$target_dir"; then
    log_success "Repository $repo_name successfully cloned to $target_dir"
    echo "| $repo_name | ✅ Success | $target_dir |" >> "$REPORT_FILE"
    ((success_count++))
else
    log_error "Failed to clone $repo_name"
    echo "| $repo_name | ❌ Failed | $target_dir |" >> "$REPORT_FILE"
    ((failure_count++))
fi

# Repository 6: R-Meta-Analysis
repo_url="https://github.com/Jiliac/R-Meta-Analysis.git"
target_dir="visualization/r-analysis"
repo_name=$(basename "$repo_url" .git)

if clone_repo "$repo_url" "$target_dir"; then
    log_success "Repository $repo_name successfully cloned to $target_dir"
    echo "| $repo_name | ✅ Success | $target_dir |" >> "$REPORT_FILE"
    ((success_count++))
else
    log_error "Failed to clone $repo_name"
    echo "| $repo_name | ❌ Failed | $target_dir |" >> "$REPORT_FILE"
    ((failure_count++))
fi

# Create additional directories if needed
mkdir -p data-collection/scraper/mtgmelee
mkdir -p config
mkdir -p data
mkdir -p docs

# Finalize report
cat >> "$REPORT_FILE" << EOF

## Summary

- Successfully cloned repositories: $success_count
- Failures: $failure_count
- Total: $((success_count + failure_count))

## Directory Structure

\`\`\`
$(find . -type d | sort | sed 's/^/  /')
\`\`\`

## Next Steps

1. Configure data sources in \`config/sources.json\`
2. Run connectivity tests with \`python3 test_connections.py\`
3. Check documentation in the \`docs/\` folder
EOF

# Display summary
log_info "Installation completed!"
log_info "Successfully cloned repositories: $success_count"
log_info "Failures: $failure_count"
log_info "Installation report generated: $REPORT_FILE"

if [ $failure_count -eq 0 ]; then
    log_success "All repositories were successfully cloned!"
else
    log_warning "Some repositories could not be cloned. Check the report for details."
fi

# Make script executable
chmod +x "$0"

exit 0