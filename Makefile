# Makefile for Manalytics Project

.PHONY: help setup install dev prod test clean logs shell db-shell check-env

# Default target
help:
	@echo "Manalytics - MTG Meta Analysis Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup      - Complete initial setup (fetch rules, build, migrate)"
	@echo "  make dev        - Start development environment"
	@echo "  make prod       - Start production environment"
	@echo "  make test       - Run test suite"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make logs       - Show logs for all services"
	@echo "  make shell      - Open shell in API container"
	@echo "  make db-shell   - Open PostgreSQL shell"
	@echo "  make pipeline   - Run the scraping pipeline manually"

# Check if .env exists
check-env:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env with your credentials before continuing!"; \
		exit 1; \
	fi

# Complete setup from scratch
setup: check-env
	@echo "🚀 Starting Manalytics setup..."
	
	# Step 1: Fetch archetype rules
	@echo "📥 Fetching latest archetype rules..."
	@python scripts/fetch_archetype_rules.py
	
	# Step 2: Build Docker images
	@echo "🏗️  Building Docker images..."
	@docker-compose build
	
	# Step 3: Start database
	@echo "🗄️  Starting database..."
	@docker-compose up -d db
	@echo "⏳ Waiting for database to be ready..."
	@sleep 10
	
	# Step 4: Run migrations
	@echo "📊 Running database migrations..."
	@docker-compose run --rm api python scripts/migrate_rules.py
	
	# Step 5: Start all services
	@echo "🎯 Starting all services..."
	@docker-compose up -d
	
	@echo "✅ Setup complete! Services are running."
	@echo "📱 API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/api/docs"

# Development environment
dev: check-env
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production environment (detached)
prod: check-env
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run tests
test:
	docker-compose run --rm api pytest tests/ -v

# Run the pipeline manually
pipeline: check-env
	@read -p "Enter format (standard/modern/legacy/pioneer/pauper/vintage): " format; \
	read -p "Enter days to scrape (default 7): " days; \
	days=$${days:-7}; \
	docker-compose run --rm worker python scripts/run_pipeline.py --format $$format --days $$days

# View logs
logs:
	docker-compose logs -f

# Specific service logs
logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f worker

logs-db:
	docker-compose logs -f db

# Shell access
shell:
	docker-compose exec api /bin/bash

db-shell:
	docker-compose exec db psql -U manalytics -d manalytics

# Cleanup
clean:
	docker-compose down -v
	rm -rf data/raw/*
	rm -rf data/processed/*
	rm -rf data/cache/*
	rm -rf data/output/*

# Restart services
restart:
	docker-compose restart

# Check service health
health:
	@echo "🏥 Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "🔍 Database status:"
	@docker-compose exec db pg_isready -U manalytics || echo "Database not ready"
	@echo ""
	@echo "🔍 Redis status:"
	@docker-compose exec redis redis-cli ping || echo "Redis not ready"
	@echo ""
	@echo "🔍 API status:"
	@curl -s http://localhost:8000/api/health | jq . || echo "API not ready"

# Run comprehensive health check
health-check:
	@python scripts/healthcheck.py

# Run continuous health monitoring
health-monitor:
	@python scripts/healthcheck.py --continuous

# Health check with JSON output (for CI/CD)
health-json:
	@python scripts/healthcheck.py --json

# Update dependencies
update-deps:
	@echo "📦 Updating dependencies..."
	pip-compile requirements.in -o requirements.txt --upgrade

# Database backup
backup-db:
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	docker-compose exec db pg_dump -U manalytics manalytics > backups/manalytics_$$timestamp.sql; \
	echo "✅ Database backed up to backups/manalytics_$$timestamp.sql"

# Restore database from backup
restore-db:
	@read -p "Enter backup filename (in backups/ directory): " filename; \
	docker-compose exec -T db psql -U manalytics manalytics < backups/$$filename; \
	echo "✅ Database restored from backups/$$filename"