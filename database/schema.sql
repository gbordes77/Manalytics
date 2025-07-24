-- Manalytics Database Schema (Version Révisée)

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schema
CREATE SCHEMA IF NOT EXISTS manalytics;
SET search_path TO manalytics, public;

-- Tables
CREATE TABLE formats (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    base_url VARCHAR(255),
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tournaments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id INTEGER REFERENCES sources(id),
    format_id INTEGER REFERENCES formats(id),
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    players_count INTEGER,
    url VARCHAR(500),
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, name, date)
);

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    mtgo_username VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, mtgo_username)
);

CREATE TABLE archetypes (
    id SERIAL PRIMARY KEY,
    format_id INTEGER REFERENCES formats(id),
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    color_identity VARCHAR(10),
    macro_archetype VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(format_id, name)
);

CREATE TABLE decklists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tournament_id UUID REFERENCES tournaments(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(id),
    archetype_id INTEGER REFERENCES archetypes(id),
    position INTEGER,
    wins INTEGER,
    losses INTEGER,
    draws INTEGER,
    mainboard JSONB NOT NULL,
    sideboard JSONB,
    original_archetype VARCHAR(100),
    detection_method VARCHAR(50),
    confidence_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tournament_id, player_id)
);

CREATE TABLE matchups (
    id SERIAL PRIMARY KEY,
    format_id INTEGER REFERENCES formats(id),
    archetype1_id INTEGER REFERENCES archetypes(id),
    archetype2_id INTEGER REFERENCES archetypes(id),
    matches_count INTEGER DEFAULT 0,
    archetype1_wins INTEGER DEFAULT 0,
    archetype2_wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    win_rate DECIMAL(5,4),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(format_id, archetype1_id, archetype2_id),
    CHECK (archetype1_id < archetype2_id)
);

CREATE TABLE archetype_rules (
    id SERIAL PRIMARY KEY,
    archetype_id INTEGER REFERENCES archetypes(id),
    rule_type VARCHAR(50) NOT NULL,
    rule_data JSONB NOT NULL,
    priority INTEGER DEFAULT 100,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tournaments_date ON tournaments(date);
CREATE INDEX idx_decklists_archetype ON decklists(archetype_id);
CREATE INDEX idx_decklists_tournament ON decklists(tournament_id);
CREATE INDEX idx_tournaments_format_date ON tournaments(format_id, date DESC);

-- Initial Data
INSERT INTO formats (name, display_name) VALUES
    ('standard', 'Standard'), ('modern', 'Modern'), ('legacy', 'Legacy'),
    ('vintage', 'Vintage'), ('pioneer', 'Pioneer'), ('pauper', 'Pauper');

INSERT INTO sources (name, base_url) VALUES
    ('mtgo', 'https://magic.wizards.com'), ('melee', 'https://melee.gg');