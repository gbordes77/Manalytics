# Dépendances MTG Analytics Pipeline

## Vue d'Ensemble

Ce document détaille toutes les dépendances requises pour faire fonctionner le pipeline MTG Analytics, organisées par composant et technologie.

## Dépendances Système

### Prérequis Globaux

#### Git
```bash
# Installation
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Windows
# Télécharger depuis https://git-scm.com/
```

#### Python
```bash
# Version requise : Python 3.8+
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# macOS
brew install python3

# Windows
# Télécharger depuis https://www.python.org/
```

#### .NET Runtime
```bash
# Version requise : .NET 8.0
# Ubuntu/Debian
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-runtime-8.0

# macOS
brew install dotnet

# Windows
# Télécharger depuis https://dotnet.microsoft.com/download
```

#### R
```bash
# Version requise : R 4.0+
# Ubuntu/Debian
sudo apt-get install r-base r-base-dev

# macOS
brew install r

# Windows
# Télécharger depuis https://cran.r-project.org/
```

## Dépendances Python

### Étape 1 : Collecte de Données

#### mtg_decklist_scrapper
```txt
# requirements.txt
beautifulsoup4>=4.9.0
numpy>=1.19.0
pytest>=6.0.0
python_dateutil>=2.8.0
requests>=2.25.0
```

#### Installation
```bash
cd data-collection/scraper/mtgo
pip install -r requirements.txt
```

#### Dépendances Optionnelles
```txt
# Pour le développement et les tests
pytest-cov>=2.10.0
black>=21.0.0
flake8>=3.8.0
mypy>=0.800
```

### Étape 2 : Traitement de Données

#### MTGOArchetypeParser (Adaptateur Python)
```txt
# requirements.txt
subprocess32>=3.5.0  # Pour l'appel des processus .NET
json5>=0.9.0         # Pour le parsing JSON avancé
pathlib2>=2.3.0      # Pour la gestion des chemins
```

#### Installation
```bash
cd data-treatment/parser
pip install -r requirements.txt
```

### Dépendances Globales Python

#### Pipeline Principal
```txt
# requirements.txt (racine du projet)
# Collecte
beautifulsoup4>=4.9.0
requests>=2.25.0
numpy>=1.19.0
python_dateutil>=2.8.0

# Traitement
subprocess32>=3.5.0
json5>=0.9.0
pathlib2>=2.3.0

# Utilitaires
click>=8.0.0
rich>=10.0.0
tqdm>=4.60.0
pyyaml>=5.4.0

# Tests
pytest>=6.0.0
pytest-cov>=2.10.0
pytest-mock>=3.6.0

# Développement
black>=21.0.0
flake8>=3.8.0
isort>=5.9.0
mypy>=0.800
pre-commit>=2.15.0
```

#### Installation Globale
```bash
# Depuis la racine du projet
pip install -r requirements.txt
```

## Dépendances R

### Étape 3 : Visualisation

#### R-Meta-Analysis
```r
# packages.R
required_packages <- c(
  "tidyverse",      # Manipulation et visualisation de données
  "ggplot2",        # Graphiques
  "reshape2",       # Restructuration de données
  "gridExtra",      # Arrangement de graphiques
  "scales",         # Échelles pour graphiques
  "dplyr",          # Manipulation de données
  "tidyr",          # Nettoyage de données
  "readr",          # Lecture de fichiers
  "stringr",        # Manipulation de chaînes
  "lubridate",      # Dates et heures
  "knitr",          # Génération de rapports
  "rmarkdown"       # Markdown pour R
)
```

#### Installation
```r
# Depuis R ou RStudio
install.packages(required_packages, repos = "https://cloud.r-project.org/")

# Ou via script
Rscript install_dependencies.R
```

#### Script d'Installation R
```r
# install_dependencies.R
required_packages <- c(
  "tidyverse", "ggplot2", "reshape2", "gridExtra", "scales",
  "dplyr", "tidyr", "readr", "stringr", "lubridate", "knitr", "rmarkdown"
)

for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    cat(paste("Installing package:", pkg, "\n"))
    install.packages(pkg, repos = "https://cloud.r-project.org/")
  } else {
    cat(paste("Package", pkg, "already installed\n"))
  }
}

cat("All R dependencies installed successfully!\n")
```

## Dépendances .NET

### MTGOArchetypeParser

#### Prérequis
- .NET Runtime 8.0
- Visual Studio 2022 ou .NET CLI

#### Installation
```bash
# Vérifier la version .NET
dotnet --version

# Compiler le projet
cd data-treatment/parser/MTGOArchetypeParser.App
dotnet build

# Exécuter
dotnet run -- detect format=Modern filter=modern-preliminary-2021-01-21
```

#### Dépendances du Projet
```xml
<!-- MTGOArchetypeParser.App.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
    <PackageReference Include="System.Text.Json" Version="8.0.0" />
  </ItemGroup>
</Project>
```

## Dépendances par Plateforme

### Ubuntu/Debian
```bash
# Mise à jour du système
sudo apt-get update
sudo apt-get upgrade

# Installation des prérequis
sudo apt-get install -y \
  git \
  python3 \
  python3-pip \
  python3-venv \
  r-base \
  r-base-dev \
  build-essential \
  curl \
  wget

# Installation .NET
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-runtime-8.0
```

### macOS
```bash
# Installation Homebrew (si pas déjà installé)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installation des prérequis
brew install \
  git \
  python3 \
  r \
  dotnet

# Création d'un environnement virtuel Python
python3 -m venv venv
source venv/bin/activate
```

### Windows
```powershell
# Installation Chocolatey (si pas déjà installé)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Installation des prérequis
choco install -y \
  git \
  python3 \
  r.project \
  dotnet-runtime

# Création d'un environnement virtuel Python
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## Scripts d'Installation

### Script Bash (Linux/macOS)
```bash
#!/bin/bash
# install_dependencies.sh

set -e

echo "Installing MTG Analytics Pipeline dependencies..."

# Vérifier les prérequis
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    else
        echo "✅ $1 is installed"
    fi
}

check_command git
check_command python3
check_command dotnet
check_command R

# Créer l'environnement virtuel Python
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Installer les dépendances R
echo "Installing R dependencies..."
Rscript install_dependencies.R

echo "✅ All dependencies installed successfully!"
```

### Script PowerShell (Windows)
```powershell
# install_dependencies.ps1

Write-Host "Installing MTG Analytics Pipeline dependencies..." -ForegroundColor Green

# Vérifier les prérequis
function Test-Command {
    param($Command)
    if (Get-Command $Command -ErrorAction SilentlyContinue) {
        Write-Host "✅ $Command is installed" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $Command is not installed. Please install it first." -ForegroundColor Red
        return $false
    }
}

$prereqs = @("git", "python", "dotnet", "R")
$allInstalled = $true

foreach ($prereq in $prereqs) {
    if (-not (Test-Command $prereq)) {
        $allInstalled = $false
    }
}

if (-not $allInstalled) {
    exit 1
}

# Créer l'environnement virtuel Python
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installer les dépendances Python
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# Installer les dépendances R
Write-Host "Installing R dependencies..." -ForegroundColor Yellow
Rscript install_dependencies.R

Write-Host "✅ All dependencies installed successfully!" -ForegroundColor Green
```

## Vérification de l'Installation

### Script de Test
```python
# test_dependencies.py
#!/usr/bin/env python3

import sys
import subprocess
import importlib

def test_python_package(package_name):
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name}")
        return False

def test_command(command, version_flag="--version"):
    try:
        result = subprocess.run([command, version_flag], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {command}: {version}")
            return True
        else:
            print(f"❌ {command}")
            return False
    except Exception:
        print(f"❌ {command}")
        return False

def main():
    print("Testing MTG Analytics Pipeline dependencies...\n")
    
    # Test des commandes système
    print("System Commands:")
    test_command("git")
    test_command("python3", "--version")
    test_command("dotnet", "--version")
    test_command("R", "--version")
    
    print("\nPython Packages:")
    python_packages = [
        "requests", "beautifulsoup4", "numpy", "pandas",
        "click", "rich", "tqdm", "pyyaml"
    ]
    
    all_ok = True
    for package in python_packages:
        if not test_python_package(package):
            all_ok = False
    
    if all_ok:
        print("\n✅ All dependencies are properly installed!")
        return 0
    else:
        print("\n❌ Some dependencies are missing. Please install them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Résolution de Problèmes

### Problèmes Courants

#### Python
```bash
# Erreur : ModuleNotFoundError
pip install --upgrade pip
pip install -r requirements.txt

# Erreur : Permission denied
pip install --user -r requirements.txt
```

#### R
```r
# Erreur : Package not found
install.packages("package_name", repos = "https://cloud.r-project.org/")

# Erreur : Version incompatible
update.packages(ask = FALSE)
```

#### .NET
```bash
# Erreur : .NET not found
# Ubuntu/Debian
sudo apt-get install dotnet-runtime-8.0

# macOS
brew install dotnet

# Windows
# Télécharger depuis https://dotnet.microsoft.com/download
```

### Logs d'Installation
```bash
# Activer les logs détaillés
pip install -v -r requirements.txt
dotnet build --verbosity detailed
R CMD INSTALL --debug package_name
```

## Maintenance

### Mise à Jour des Dépendances
```bash
# Python
pip list --outdated
pip install --upgrade package_name

# R
update.packages(ask = FALSE)

# .NET
dotnet tool update -g dotnet-ef
```

### Nettoyage
```bash
# Supprimer les caches
pip cache purge
R -e "remove.packages(installed.packages()[,'Package'])"
dotnet clean
``` 