# MTG Analytics Pipeline - Installation script for Windows
# This script clones the 6 required GitHub repositories and places them in the appropriate structure

# Function to display colored messages
function Write-ColoredMessage {
    param (
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    switch ($Type) {
        "INFO" { 
            Write-Host "[INFO] $Message" -ForegroundColor Cyan 
        }
        "SUCCESS" { 
            Write-Host "[SUCCESS] $Message" -ForegroundColor Green 
        }
        "WARNING" { 
            Write-Host "[WARNING] $Message" -ForegroundColor Yellow 
        }
        "ERROR" { 
            Write-Host "[ERROR] $Message" -ForegroundColor Red 
        }
    }
}

# Function to clone a repository
function Clone-Repository {
    param (
        [string]$RepoUrl,
        [string]$TargetDir
    )
    
    $repoName = [System.IO.Path]::GetFileNameWithoutExtension($RepoUrl)
    
    Write-ColoredMessage "Cloning $repoName to $TargetDir..." "INFO"
    
    if (Test-Path $TargetDir) {
        Write-ColoredMessage "Directory $TargetDir already exists. Checking if it's a git repo..." "WARNING"
        if (Test-Path "$TargetDir\.git") {
            Write-ColoredMessage "Git repository found. Updating..." "INFO"
            Push-Location $TargetDir
            git pull
            $result = $?
            Pop-Location
            return $result
        } else {
            Write-ColoredMessage "Directory exists but is not a git repo. Backing up and recloning..." "WARNING"
            $timestamp = Get-Date -Format "yyyyMMddHHmmss"
            Rename-Item -Path $TargetDir -NewName "${TargetDir}_backup_$timestamp"
        }
    }
    
    $parentDir = Split-Path -Parent $TargetDir
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
    
    git clone $RepoUrl $TargetDir
    return $?
}

# Check that git is installed
try {
    $gitVersion = git --version
    Write-ColoredMessage "Git detected: $gitVersion" "INFO"
} catch {
    Write-ColoredMessage "Git is not installed or not in PATH. Please install git and try again." "ERROR"
    exit 1
}

# Base directory
$baseDir = Get-Location
Write-ColoredMessage "Base directory: $baseDir" "INFO"

# Create installation report
$reportFile = Join-Path $baseDir "manalytics\installation_report.md"
$reportDir = Split-Path -Parent $reportFile
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

# Initialize report
@"
# MTG Analytics Pipeline Installation Report

Date: $(Get-Date)

## Repository Status

| Repository | Status | Path |
|------------|--------|--------|
"@ | Out-File -FilePath $reportFile -Encoding utf8

# List of repositories to clone with their target paths
$repos = @{
    "https://github.com/fbettega/mtg_decklist_scrapper.git" = "manalytics\data-collection\scraper\mtgo"
    "https://github.com/fbettega/MTG_decklistcache.git" = "manalytics\data-collection\raw-cache"
    "https://github.com/Jiliac/MTGODecklistCache.git" = "manalytics\data-collection\processed-cache"
    "https://github.com/Badaro/MTGOArchetypeParser.git" = "manalytics\data-treatment\parser"
    "https://github.com/Badaro/MTGOFormatData.git" = "manalytics\data-treatment\format-rules"
    "https://github.com/Jiliac/R-Meta-Analysis.git" = "manalytics\visualization\r-analysis"
}

# Clone each repository
$successCount = 0
$failureCount = 0

foreach ($repoUrl in $repos.Keys) {
    $targetDir = Join-Path $baseDir $repos[$repoUrl]
    $repoName = [System.IO.Path]::GetFileNameWithoutExtension($repoUrl)
    
    if (Clone-Repository -RepoUrl $repoUrl -TargetDir $targetDir) {
        Write-ColoredMessage "Repository $repoName successfully cloned to $targetDir" "SUCCESS"
        "| $repoName | ✅ Success | $targetDir |" | Out-File -FilePath $reportFile -Append -Encoding utf8
        $successCount++
    } else {
        Write-ColoredMessage "Failed to clone $repoName" "ERROR"
        "| $repoName | ❌ Failed | $targetDir |" | Out-File -FilePath $reportFile -Append -Encoding utf8
        $failureCount++
    }
}

# Create additional directories if needed
$additionalDirs = @(
    "manalytics\data-collection\scraper\mtgmelee",
    "manalytics\config",
    "manalytics\data",
    "manalytics\docs"
)

foreach ($dir in $additionalDirs) {
    $fullPath = Join-Path $baseDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-ColoredMessage "Directory created: $fullPath" "INFO"
    }
}

# Get directory structure
$folderStructure = Get-ChildItem -Path (Join-Path $baseDir "manalytics") -Directory -Recurse | 
                   Select-Object -ExpandProperty FullName | 
                   ForEach-Object { $_.Replace($baseDir.ToString() + "\", "") } | 
                   Sort-Object

# Finalize report
@"

## Summary

- Successfully cloned repositories: $successCount
- Failures: $failureCount
- Total: $($successCount + $failureCount)

## Directory Structure

```
  $($folderStructure -join "`n  ")
```

## Next Steps

1. Configure data sources in `config/sources.json`
2. Run connectivity tests with `python test_connections.py`
3. Check documentation in the `docs/` folder
"@ | Out-File -FilePath $reportFile -Append -Encoding utf8

# Display summary
Write-ColoredMessage "Installation completed!" "INFO"
Write-ColoredMessage "Successfully cloned repositories: $successCount" "INFO"
Write-ColoredMessage "Failures: $failureCount" "INFO"
Write-ColoredMessage "Installation report generated: $reportFile" "INFO"

if ($failureCount -eq 0) {
    Write-ColoredMessage "All repositories were successfully cloned!" "SUCCESS"
} else {
    Write-ColoredMessage "Some repositories could not be cloned. Check the report for details." "WARNING"
}

exit 0