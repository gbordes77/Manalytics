import structlog
import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os

class ManalyticsLogger:
    """Logger structuré centralisé pour Manalytics
    
    🎯 OBJECTIFS PLAN EXPERT :
    - Éliminer tous les print() du code
    - Logging structuré avec metadata
    - Rotation automatique des logs
    - Logs métier spécifiques MTG
    - JSON en production, console en dev
    """
    
    def __init__(self, log_dir: str = "logs", enable_json: bool = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Auto-détection JSON basée sur environnement
        if enable_json is None:
            enable_json = os.getenv("ENVIRONMENT", "development") == "production"
        
        self.enable_json = enable_json
        
        # Configuration des processeurs
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        
        # JSON en production, console en dev
        if enable_json:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer(
                colors=True,
                pad_event=30,
                sort_keys=False
            ))
        
        # Configuration structlog
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Configuration logging standard
        self._setup_file_logging()
        
        self.logger = structlog.get_logger()
        
        # Logger initial
        self.logger.info("ManalyticsLogger initialized", 
                        log_dir=str(self.log_dir),
                        json_enabled=enable_json)
    
    def _setup_file_logging(self):
        """Configuration des logs fichiers avec rotation"""
        
        # Formatter JSON ou texte
        if self.enable_json:
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Handler pour logs généraux
        general_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "manalytics.log",
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(formatter)
        
        # Handler pour erreurs
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=10_000_000,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Handler pour sécurité
        security_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "security.log",
            maxBytes=10_000_000,
            backupCount=10  # Plus de backups pour sécurité
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(formatter)
        
        # Handler pour performance
        performance_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "performance.log",
            maxBytes=5_000_000,  # 5MB
            backupCount=3
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(formatter)
        
        # Configuration root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(general_handler)
        root_logger.addHandler(error_handler)
        
        # Logger sécurité séparé
        security_logger = logging.getLogger("security")
        security_logger.addHandler(security_handler)
        
        # Logger performance séparé
        performance_logger = logging.getLogger("performance")
        performance_logger.addHandler(performance_handler)
    
    # Méthodes métier spécifiques MTG
    
    def pipeline_started(
        self, 
        format_name: str, 
        date_range: str,
        pipeline_id: str,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """Log démarrage pipeline avec contexte"""
        self.logger.info(
            "🚀 Pipeline started",
            event_type="pipeline_started",
            format=format_name,
            date_range=date_range,
            pipeline_id=pipeline_id,
            user_id=user_id,
            component="orchestrator",
            **kwargs
        )
    
    def pipeline_completed(
        self,
        format_name: str,
        pipeline_id: str,
        total_time: float,
        tournament_count: int,
        deck_count: int,
        success: bool = True,
        **kwargs
    ):
        """Log fin pipeline avec résultats"""
        
        emoji = "✅" if success else "❌"
        event = "pipeline_completed" if success else "pipeline_failed"
        
        self.logger.info(
            f"{emoji} Pipeline completed",
            event_type=event,
            format=format_name,
            pipeline_id=pipeline_id,
            total_time_ms=int(total_time * 1000),
            tournament_count=tournament_count,
            deck_count=deck_count,
            success=success,
            component="orchestrator",
            **kwargs
        )
    
    def data_loaded(
        self,
        source: str,
        format_name: str,
        tournament_count: int,
        deck_count: int,
        load_time: float,
        cache_hit: bool = False,
        **kwargs
    ):
        """Log chargement données avec métriques"""
        
        emoji = "💾" if cache_hit else "📡"
        
        self.logger.info(
            f"{emoji} Data loaded from {source}",
            event_type="data_loaded",
            source=source,
            format=format_name,
            tournament_count=tournament_count,
            deck_count=deck_count,
            load_time_ms=int(load_time * 1000),
            cache_hit=cache_hit,
            component="data_loader",
            **kwargs
        )
    
    def classification_completed(
        self,
        format_name: str,
        total_decks: int,
        classified_count: int,
        unknown_count: int,
        classification_time: float,
        cache_hit: bool = False,
        **kwargs
    ):
        """Log classification avec statistiques"""
        
        success_rate = classified_count / max(1, total_decks) * 100
        emoji = "🎯" if success_rate > 80 else "🔍"
        
        self.logger.info(
            f"{emoji} Classification completed",
            event_type="classification_completed",
            format=format_name,
            total_decks=total_decks,
            classified_count=classified_count,
            unknown_count=unknown_count,
            success_rate=f"{success_rate:.1f}%",
            classification_time_ms=int(classification_time * 1000),
            cache_hit=cache_hit,
            component="classifier",
            **kwargs
        )
    
    def archetype_detected(
        self,
        deck_hash: str,
        archetype: str,
        confidence: float,
        format_name: str,
        cards_analyzed: int,
        **kwargs
    ):
        """Log détection archétype"""
        
        emoji = "🎯" if confidence > 0.8 else "🔍"
        
        self.logger.info(
            f"{emoji} Archetype detected: {archetype}",
            event_type="archetype_detected",
            deck_hash=deck_hash,
            archetype=archetype,
            confidence=f"{confidence:.2f}",
            format=format_name,
            cards_analyzed=cards_analyzed,
            component="classifier",
            **kwargs
        )
    
    def visualization_generated(
        self,
        chart_type: str,
        format_name: str,
        generation_time: float,
        data_points: int,
        file_size_kb: Optional[int] = None,
        **kwargs
    ):
        """Log génération visualisation"""
        
        self.logger.info(
            f"📊 Visualization generated: {chart_type}",
            event_type="visualization_generated",
            chart_type=chart_type,
            format=format_name,
            generation_time_ms=int(generation_time * 1000),
            data_points=data_points,
            file_size_kb=file_size_kb,
            component="visualization",
            **kwargs
        )
    
    def cache_operation(
        self,
        operation: str,  # get, set, invalidate, miss, hit
        key: str,
        cache_level: str,  # L1, L2
        operation_time: float,
        hit: bool = None,
        **kwargs
    ):
        """Log opération cache"""
        
        emoji = "💾" if hit else "🔍" if operation == "get" else "💿"
        
        self.logger.info(
            f"{emoji} Cache {operation}: {cache_level}",
            event_type="cache_operation",
            operation=operation,
            key=key[:50] + "..." if len(key) > 50 else key,
            cache_level=cache_level,
            operation_time_ms=int(operation_time * 1000),
            hit=hit,
            component="cache",
            **kwargs
        )
    
    def api_request(
        self,
        method: str,
        endpoint: str,
        user_id: Optional[str],
        ip_address: str,
        status_code: int,
        response_time: float,
        user_agent: Optional[str] = None,
        **kwargs
    ):
        """Log requête API avec contexte complet"""
        
        # Déterminer emoji et niveau
        if status_code < 400:
            emoji = "✅"
            level = "info"
        elif status_code < 500:
            emoji = "⚠️"
            level = "warning"
        else:
            emoji = "❌"
            level = "error"
        
        log_func = getattr(self.logger, level)
        
        log_func(
            f"{emoji} {method} {endpoint} - {status_code}",
            event_type="api_request",
            method=method,
            endpoint=endpoint,
            user_id=user_id or "anonymous",
            ip_address=ip_address,
            status_code=status_code,
            response_time_ms=int(response_time * 1000),
            user_agent=user_agent,
            component="api",
            **kwargs
        )
    
    def security_event(
        self,
        event_type: str,
        severity: str,
        ip_address: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None,
        **kwargs
    ):
        """Log événement sécurité"""
        
        security_logger = structlog.get_logger("security")
        
        severity_emoji = {
            "LOW": "🔵",
            "MEDIUM": "🟡", 
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }.get(severity, "⚪")
        
        level_map = {
            "LOW": "info",
            "MEDIUM": "warning",
            "HIGH": "error",
            "CRITICAL": "critical"
        }.get(severity, "warning")
        
        log_func = getattr(security_logger, level_map)
        
        log_func(
            f"{severity_emoji} Security event: {event_type}",
            event_type="security_event",
            security_event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            user_id=user_id,
            details=details,
            component="security",
            **kwargs
        )
    
    def performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        component: str,
        threshold: Optional[float] = None,
        **kwargs
    ):
        """Log métrique de performance"""
        
        performance_logger = structlog.get_logger("performance")
        
        # Alerte si dépassement de seuil
        if threshold and value > threshold:
            emoji = "🚨"
            level = "warning"
            message = f"Performance threshold exceeded: {metric_name}"
            extra_data = {
                "threshold_exceeded": True,
                "threshold": threshold,
                "exceeded_by": f"{(value - threshold) / threshold * 100:.1f}%"
            }
        else:
            emoji = "📊"
            level = "info"
            message = f"Performance metric: {metric_name}"
            extra_data = {}
        
        log_func = getattr(performance_logger, level)
        
        log_func(
            f"{emoji} {message}",
            event_type="performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            component=component,
            **extra_data,
            **kwargs
        )
    
    def mtg_tournament_processed(
        self,
        tournament_name: str,
        format_name: str,
        date: str,
        participants: int,
        source: str,
        processing_time: float,
        **kwargs
    ):
        """Log traitement tournoi MTG"""
        
        self.logger.info(
            f"🏆 Tournament processed: {tournament_name}",
            event_type="tournament_processed",
            tournament_name=tournament_name,
            format=format_name,
            date=date,
            participants=participants,
            source=source,
            processing_time_ms=int(processing_time * 1000),
            component="tournament_processor",
            **kwargs
        )
    
    def deck_analysis_completed(
        self,
        deck_hash: str,
        archetype: str,
        colors: list,
        format_name: str,
        card_count: int,
        analysis_time: float,
        **kwargs
    ):
        """Log analyse deck MTG"""
        
        color_emoji = {
            'W': '⚪', 'U': '🔵', 'B': '⚫', 'R': '🔴', 'G': '🟢'
        }
        
        color_str = ''.join(color_emoji.get(c, c) for c in colors)
        
        self.logger.info(
            f"🃏 Deck analyzed: {archetype} {color_str}",
            event_type="deck_analysis_completed",
            deck_hash=deck_hash,
            archetype=archetype,
            colors=colors,
            format=format_name,
            card_count=card_count,
            analysis_time_ms=int(analysis_time * 1000),
            component="deck_analyzer",
            **kwargs
        )
    
    def error(
        self,
        error: Exception,
        context: Dict[str, Any],
        user_impact: bool = False,
        component: str = "unknown",
        **kwargs
    ):
        """Log erreur avec contexte détaillé"""
        
        emoji = "💥" if user_impact else "⚠️"
        
        self.logger.error(
            f"{emoji} Error occurred: {type(error).__name__}",
            event_type="error_occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            user_impact=user_impact,
            context=context,
            component=component,
            exc_info=True,  # Inclure stack trace
            **kwargs
        )
    
    def startup_completed(
        self,
        service_name: str,
        startup_time: float,
        version: str,
        environment: str,
        **kwargs
    ):
        """Log démarrage service"""
        
        self.logger.info(
            f"🚀 Service started: {service_name}",
            event_type="startup_completed",
            service_name=service_name,
            startup_time_ms=int(startup_time * 1000),
            version=version,
            environment=environment,
            component="system",
            **kwargs
        )
    
    def shutdown_initiated(
        self,
        service_name: str,
        reason: str = "normal",
        **kwargs
    ):
        """Log arrêt service"""
        
        emoji = "🛑" if reason == "error" else "👋"
        
        self.logger.info(
            f"{emoji} Service shutdown: {service_name}",
            event_type="shutdown_initiated",
            service_name=service_name,
            reason=reason,
            component="system",
            **kwargs
        )
    
    def get_context_logger(self, **permanent_context):
        """Créer logger avec contexte permanent"""
        return self.logger.bind(**permanent_context)
    
    def get_performance_logger(self):
        """Obtenir logger performance spécialisé"""
        return structlog.get_logger("performance")
    
    def get_security_logger(self):
        """Obtenir logger sécurité spécialisé"""
        return structlog.get_logger("security")


# Instance globale avec configuration optimisée
manalytics_logger = ManalyticsLogger(
    log_dir="logs",
    enable_json=None  # Auto-détection basée sur ENVIRONMENT
) 