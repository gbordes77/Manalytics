#!/usr/bin/env Rscript

# Script d'analyse R - Reproduction de Jiliac/R-Meta-Analysis
# Analyse statistique des données de métagame MTG

# Charger les librairies nécessaires
suppressMessages({
  library(jsonlite)
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(stringr)
})

# Fonction principale d'analyse
analyze_metagame <- function(input_dir, output_file, format_name) {
  cat("🔍 Démarrage de l'analyse R-Meta-Analysis\n")
  cat("📁 Dossier d'entrée:", input_dir, "\n")
  cat("📄 Fichier de sortie:", output_file, "\n")
  cat("🎯 Format:", format_name, "\n")
  
  # Charger tous les tournois
  cat("📚 Chargement des données...\n")
  all_tournaments <- load_all_tournaments(input_dir)
  
  if (length(all_tournaments) == 0) {
    cat("❌ Aucun tournoi trouvé dans", input_dir, "\n")
    return(FALSE)
  }
  
  cat("✅ Chargé", length(all_tournaments), "tournois\n")
  
  # Agréger les données
  cat("🔄 Agrégation des données...\n")
  aggregated_data <- aggregate_tournament_data(all_tournaments)
  
  # Calculer les statistiques d'archétypes
  cat("📊 Calcul des statistiques d'archétypes...\n")
  archetype_stats <- calculate_archetype_stats(aggregated_data)
  
  # Calculer la matrice de matchups
  cat("⚔️ Calcul de la matrice de matchups...\n")
  matchup_matrix <- calculate_matchup_matrix(aggregated_data)
  
  # Calculer les intervalles de confiance
  cat("📈 Calcul des intervalles de confiance...\n")
  confidence_intervals <- calculate_confidence_intervals(archetype_stats)
  
  # Classification par tiers
  cat("🏆 Classification par tiers...\n")
  tier_classification <- classify_tiers(confidence_intervals)
  
  # Créer le résultat final
  result <- list(
    metadata = list(
      generated_at = Sys.time(),
      format = format_name,
      total_tournaments = length(all_tournaments),
      total_decks = nrow(aggregated_data),
      analysis_version = "R-Meta-Analysis v1.0"
    ),
    archetype_performance = archetype_stats,
    confidence_intervals = confidence_intervals,
    tier_classification = tier_classification,
    matchup_matrix = matchup_matrix,
    raw_data_summary = summarize_raw_data(aggregated_data)
  )
  
  # Sauvegarder le résultat
  cat("💾 Sauvegarde des résultats...\n")
  write_json(result, output_file, pretty = TRUE, auto_unbox = TRUE)
  
  cat("✅ Analyse terminée avec succès!\n")
  cat("📄 Résultats sauvegardés dans:", output_file, "\n")
  
  return(TRUE)
}

# Charger tous les tournois depuis un dossier
load_all_tournaments <- function(input_dir) {
  tournament_files <- list.files(input_dir, pattern = "*.json", 
                                recursive = TRUE, full.names = TRUE)
  
  all_tournaments <- list()
  
  for (file in tournament_files) {
    tryCatch({
      tournament_data <- fromJSON(file)
      
      # Vérifier la structure (supporter les deux formats)
      if (is.null(tournament_data$Tournament) && is.null(tournament_data$tournament)) {
        next
      }
      if (is.null(tournament_data$Standings) && is.null(tournament_data$decks)) {
        next
      }
      
      all_tournaments <- append(all_tournaments, list(tournament_data))
    }, error = function(e) {
      cat("⚠️ Erreur lors du chargement de", file, ":", e$message, "\n")
    })
  }
  
  return(all_tournaments)
}

# Agréger les données de tous les tournois
aggregate_tournament_data <- function(tournaments) {
  all_decks <- data.frame()
  
  for (tournament in tournaments) {
    # Supporter les deux formats de données
    tournament_info <- tournament$Tournament %||% tournament$tournament
    standings <- tournament$Standings %||% tournament$decks
    
    if (is.null(standings) || length(standings) == 0) {
      next
    }
    
    # Convertir les standings en data frame
    tournament_decks <- data.frame(
      tournament_id = tournament_info$ID %||% tournament_info$id,
      tournament_name = tournament_info$Name %||% tournament_info$name,
      tournament_date = tournament_info$Date %||% tournament_info$date,
      tournament_format = tournament_info$Format %||% tournament_info$format,
      player = sapply(standings, function(s) {
        if (is.list(s)) {
          s$Player %||% s$player %||% "Unknown"
        } else {
          "Unknown"
        }
      }),
      rank = sapply(standings, function(s) {
        if (is.list(s)) {
          s$Rank %||% s$rank %||% 0
        } else {
          0
        }
      }),
      wins = sapply(standings, function(s) {
        if (is.list(s)) {
          s$Wins %||% s$wins %||% 0
        } else {
          0
        }
      }),
      losses = sapply(standings, function(s) {
        if (is.list(s)) {
          s$Losses %||% s$losses %||% 0
        } else {
          0
        }
      }),
      draws = sapply(standings, function(s) {
        if (is.list(s)) {
          s$Draws %||% s$draws %||% 0
        } else {
          0
        }
      }),
      points = sapply(standings, function(s) {
        if (is.list(s)) {
          s$Points %||% s$points %||% 0
        } else {
          0
        }
      }),
      archetype = sapply(standings, function(s) {
        if (is.list(s)) {
          if (!is.null(s$Deck) && is.list(s$Deck)) {
            s$Deck$Archetype %||% s$archetype %||% "Unknown"
          } else {
            s$archetype %||% "Unknown"
          }
        } else {
          "Unknown"
        }
      }),
      stringsAsFactors = FALSE
    )
    
    all_decks <- rbind(all_decks, tournament_decks)
  }
  
  return(all_decks)
}

# Calculer les statistiques d'archétypes
calculate_archetype_stats <- function(data) {
  archetype_stats <- data %>%
    filter(!is.na(archetype) & archetype != "") %>%
    group_by(archetype) %>%
    summarise(
      count = n(),
      total_wins = sum(wins, na.rm = TRUE),
      total_losses = sum(losses, na.rm = TRUE),
      total_draws = sum(draws, na.rm = TRUE),
      total_matches = total_wins + total_losses + total_draws,
      win_rate = ifelse(total_matches > 0, total_wins / total_matches, 0),
      meta_share = count / nrow(data),
      avg_rank = mean(rank, na.rm = TRUE),
      tournaments_played = n_distinct(tournament_id),
      .groups = 'drop'
    ) %>%
    arrange(desc(meta_share))
  
  return(as.data.frame(archetype_stats))
}

# Calculer les intervalles de confiance Wilson
calculate_confidence_intervals <- function(archetype_stats) {
  confidence_level <- 0.95
  z_score <- qnorm((1 + confidence_level) / 2)
  
  ci_data <- archetype_stats %>%
    mutate(
      # Intervalle de confiance Wilson pour le winrate
      n_matches = total_matches,
      p_hat = win_rate,
      wilson_center = (p_hat + z_score^2 / (2 * n_matches)) / (1 + z_score^2 / n_matches),
      wilson_width = z_score * sqrt(p_hat * (1 - p_hat) / n_matches + z_score^2 / (4 * n_matches^2)) / (1 + z_score^2 / n_matches),
      ci_lower = pmax(0, wilson_center - wilson_width),
      ci_upper = pmin(1, wilson_center + wilson_width),
      
      # Intervalle de confiance pour la meta share
      meta_n = nrow(archetype_stats),
      meta_p = meta_share,
      meta_ci_lower = pmax(0, meta_p - z_score * sqrt(meta_p * (1 - meta_p) / meta_n)),
      meta_ci_upper = pmin(1, meta_p + z_score * sqrt(meta_p * (1 - meta_p) / meta_n))
    ) %>%
    select(archetype, count, meta_share, win_rate, 
           ci_lower, ci_upper, meta_ci_lower, meta_ci_upper,
           total_matches, tournaments_played)
  
  return(as.data.frame(ci_data))
}

# Classification par tiers basée sur les intervalles de confiance
classify_tiers <- function(ci_data) {
  # Filtrer les archétypes avec assez de données
  min_matches <- 20
  significant_archetypes <- ci_data %>%
    filter(total_matches >= min_matches)
  
  if (nrow(significant_archetypes) == 0) {
    return(data.frame(archetype = character(), tier = character(), 
                     tier_reason = character(), stringsAsFactors = FALSE))
  }
  
  # Classification basée sur la borne inférieure de l'IC du winrate
  tier_classification <- significant_archetypes %>%
    mutate(
      tier = case_when(
        ci_lower >= 0.55 ~ "Tier 1",
        ci_lower >= 0.50 ~ "Tier 2", 
        ci_lower >= 0.45 ~ "Tier 3",
        TRUE ~ "Tier 4"
      ),
      tier_reason = case_when(
        ci_lower >= 0.55 ~ "Excellent winrate (CI lower >= 55%)",
        ci_lower >= 0.50 ~ "Good winrate (CI lower >= 50%)",
        ci_lower >= 0.45 ~ "Average winrate (CI lower >= 45%)",
        TRUE ~ "Below average winrate (CI lower < 45%)"
      )
    ) %>%
    arrange(desc(ci_lower), desc(meta_share)) %>%
    select(archetype, tier, tier_reason, win_rate, ci_lower, ci_upper, 
           meta_share, count, total_matches)
  
  return(as.data.frame(tier_classification))
}

# Calculer la matrice de matchups
calculate_matchup_matrix <- function(data) {
  # Pour cette implémentation simplifiée, nous créons une matrice basée sur les performances relatives
  # Dans un vrai système, nous aurions besoin des données de matchs directs
  
  archetypes <- unique(data$archetype[data$archetype != "Unknown" & !is.na(data$archetype)])
  
  if (length(archetypes) < 2) {
    return(data.frame())
  }
  
  # Créer une matrice de matchups simulée basée sur les winrates
  archetype_winrates <- data %>%
    filter(archetype %in% archetypes) %>%
    group_by(archetype) %>%
    summarise(
      overall_winrate = sum(wins, na.rm = TRUE) / (sum(wins, na.rm = TRUE) + sum(losses, na.rm = TRUE)),
      .groups = 'drop'
    )
  
  matchup_matrix <- expand.grid(
    archetype_a = archetypes,
    archetype_b = archetypes,
    stringsAsFactors = FALSE
  ) %>%
    left_join(archetype_winrates, by = c("archetype_a" = "archetype")) %>%
    rename(winrate_a = overall_winrate) %>%
    left_join(archetype_winrates, by = c("archetype_b" = "archetype")) %>%
    rename(winrate_b = overall_winrate) %>%
    mutate(
      # Estimation du matchup basée sur les winrates relatifs
      estimated_winrate = pmax(0.1, pmin(0.9, 0.5 + (winrate_a - winrate_b) * 0.5)),
      matches_played = 0,  # Pas de données de matchs directs
      confidence = "Low"   # Confiance faible car basé sur estimation
    ) %>%
    select(archetype_a, archetype_b, estimated_winrate, matches_played, confidence)
  
  return(as.data.frame(matchup_matrix))
}

# Résumer les données brutes
summarize_raw_data <- function(data) {
  summary_stats <- list(
    total_decks = nrow(data),
    unique_archetypes = length(unique(data$archetype[data$archetype != "Unknown"])),
    tournaments_analyzed = length(unique(data$tournament_id)),
    date_range = list(
      earliest = min(data$tournament_date, na.rm = TRUE),
      latest = max(data$tournament_date, na.rm = TRUE)
    ),
    average_tournament_size = mean(table(data$tournament_id)),
    total_matches = sum(data$wins + data$losses + data$draws, na.rm = TRUE) / 2
  )
  
  return(summary_stats)
}

# Opérateur null-coalescing
`%||%` <- function(x, y) {
  if (is.null(x) || length(x) == 0 || (is.character(x) && x == "")) y else x
}

# Point d'entrée principal
main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  
  if (length(args) < 3) {
    cat("Usage: Rscript run_analysis.R <input_dir> <output_file> <format_name>\n")
    cat("Example: Rscript run_analysis.R ./data/processed ./output/results.json modern\n")
    quit(status = 1)
  }
  
  input_dir <- args[1]
  output_file <- args[2]
  format_name <- args[3]
  
  # Vérifier que le dossier d'entrée existe
  if (!dir.exists(input_dir)) {
    cat("❌ Erreur: Le dossier d'entrée n'existe pas:", input_dir, "\n")
    quit(status = 1)
  }
  
  # Créer le dossier de sortie si nécessaire
  output_dir <- dirname(output_file)
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }
  
  # Exécuter l'analyse
  success <- analyze_metagame(input_dir, output_file, format_name)
  
  if (!success) {
    cat("❌ Échec de l'analyse\n")
    quit(status = 1)
  }
  
  cat("🎉 Analyse R-Meta-Analysis terminée avec succès!\n")
}

# Exécuter si appelé directement
if (!interactive()) {
  main()
} 