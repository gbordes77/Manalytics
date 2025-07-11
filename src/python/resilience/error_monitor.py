"""
Moniteur d'erreurs pour collecter et analyser les statistiques.
Permet de détecter les patterns d'erreurs et déclencher des alertes.
"""

import time
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class ErrorEvent:
    """Représente un événement d'erreur"""
    timestamp: float
    error_type: str
    error_message: str
    component: str
    severity: str = "ERROR"
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convertit l'événement en dictionnaire"""
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'error_type': self.error_type,
            'error_message': self.error_message,
            'component': self.component,
            'severity': self.severity,
            'context': self.context
        }


@dataclass
class ErrorStats:
    """Statistiques d'erreurs pour un composant"""
    component: str
    total_errors: int = 0
    error_rate: float = 0.0
    most_common_error: Optional[str] = None
    last_error_time: Optional[float] = None
    error_types: Dict[str, int] = field(default_factory=dict)
    recent_errors: List[ErrorEvent] = field(default_factory=list)


class ErrorMonitor:
    """
    Moniteur d'erreurs centralisé pour le pipeline.
    
    Fonctionnalités :
    - Collecte d'événements d'erreur
    - Calcul de statistiques en temps réel
    - Détection de patterns d'erreurs
    - Alertes automatiques
    - Historique des erreurs
    """
    
    def __init__(
        self,
        max_events_per_component: int = 1000,
        time_window_minutes: int = 60,
        error_rate_threshold: float = 0.1,
        burst_threshold: int = 10,
        name: str = "ErrorMonitor"
    ):
        self.max_events_per_component = max_events_per_component
        self.time_window_minutes = time_window_minutes
        self.error_rate_threshold = error_rate_threshold
        self.burst_threshold = burst_threshold
        self.name = name
        
        # Stockage des événements par composant
        self.events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_events_per_component))
        
        # Compteurs globaux
        self.total_events = 0
        self.components_stats: Dict[str, ErrorStats] = {}
        
        # Alertes
        self.alert_callbacks: List[callable] = []
        self.suppressed_alerts: Dict[str, float] = {}
        self.alert_suppression_time = 300  # 5 minutes
        
        logger.info(f"Error Monitor '{name}' initialisé")
    
    def record_error(
        self,
        error: Exception,
        component: str,
        severity: str = "ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Enregistre un événement d'erreur.
        
        Args:
            error: Exception capturée
            component: Nom du composant source
            severity: Niveau de sévérité (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            context: Contexte additionnel
        """
        event = ErrorEvent(
            timestamp=time.time(),
            error_type=type(error).__name__,
            error_message=str(error),
            component=component,
            severity=severity,
            context=context or {}
        )
        
        self._add_event(event)
        
        # Vérifier si une alerte doit être déclenchée
        self._check_alert_conditions(component)
    
    def record_custom_error(
        self,
        error_type: str,
        error_message: str,
        component: str,
        severity: str = "ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Enregistre un événement d'erreur personnalisé.
        
        Args:
            error_type: Type d'erreur
            error_message: Message d'erreur
            component: Nom du composant source
            severity: Niveau de sévérité
            context: Contexte additionnel
        """
        event = ErrorEvent(
            timestamp=time.time(),
            error_type=error_type,
            error_message=error_message,
            component=component,
            severity=severity,
            context=context or {}
        )
        
        self._add_event(event)
        self._check_alert_conditions(component)
    
    def _add_event(self, event: ErrorEvent):
        """Ajoute un événement à l'historique"""
        self.events[event.component].append(event)
        self.total_events += 1
        
        # Mettre à jour les statistiques
        self._update_stats(event.component)
        
        logger.debug(f"Error Monitor: {event.component} - {event.error_type}: {event.error_message}")
    
    def _update_stats(self, component: str):
        """Met à jour les statistiques pour un composant"""
        events = list(self.events[component])
        
        if not events:
            return
        
        # Filtrer les événements récents
        cutoff_time = time.time() - (self.time_window_minutes * 60)
        recent_events = [e for e in events if e.timestamp >= cutoff_time]
        
        # Calculer les statistiques
        error_types = defaultdict(int)
        for event in recent_events:
            error_types[event.error_type] += 1
        
        most_common_error = max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        
        # Calculer le taux d'erreur (erreurs par minute)
        error_rate = len(recent_events) / self.time_window_minutes if self.time_window_minutes > 0 else 0
        
        # Mettre à jour les stats
        self.components_stats[component] = ErrorStats(
            component=component,
            total_errors=len(events),
            error_rate=error_rate,
            most_common_error=most_common_error,
            last_error_time=events[-1].timestamp if events else None,
            error_types=dict(error_types),
            recent_errors=recent_events[-10:]  # Garder les 10 dernières erreurs
        )
    
    def _check_alert_conditions(self, component: str):
        """Vérifie si des conditions d'alerte sont remplies"""
        stats = self.components_stats.get(component)
        if not stats:
            return
        
        current_time = time.time()
        alert_key = f"{component}_error_rate"
        
        # Vérifier si l'alerte est supprimée
        if alert_key in self.suppressed_alerts:
            if current_time - self.suppressed_alerts[alert_key] < self.alert_suppression_time:
                return
        
        # Condition 1: Taux d'erreur élevé
        if stats.error_rate > self.error_rate_threshold:
            self._trigger_alert(
                alert_type="HIGH_ERROR_RATE",
                component=component,
                message=f"Taux d'erreur élevé: {stats.error_rate:.2f} erreurs/min (seuil: {self.error_rate_threshold})",
                severity="WARNING"
            )
            self.suppressed_alerts[alert_key] = current_time
        
        # Condition 2: Burst d'erreurs
        recent_events = [e for e in self.events[component] if current_time - e.timestamp < 60]  # 1 minute
        if len(recent_events) >= self.burst_threshold:
            burst_key = f"{component}_burst"
            if burst_key not in self.suppressed_alerts or current_time - self.suppressed_alerts[burst_key] >= self.alert_suppression_time:
                self._trigger_alert(
                    alert_type="ERROR_BURST",
                    component=component,
                    message=f"Burst d'erreurs détecté: {len(recent_events)} erreurs en 1 minute",
                    severity="ERROR"
                )
                self.suppressed_alerts[burst_key] = current_time
    
    def _trigger_alert(self, alert_type: str, component: str, message: str, severity: str):
        """Déclenche une alerte"""
        alert_data = {
            'timestamp': time.time(),
            'alert_type': alert_type,
            'component': component,
            'message': message,
            'severity': severity,
            'monitor': self.name
        }
        
        logger.warning(f"ALERT [{alert_type}] {component}: {message}")
        
        # Appeler les callbacks d'alerte
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"Erreur dans callback d'alerte: {e}")
    
    def add_alert_callback(self, callback: callable):
        """Ajoute un callback d'alerte"""
        self.alert_callbacks.append(callback)
        logger.info(f"Callback d'alerte ajouté: {callback.__name__}")
    
    def get_component_stats(self, component: str) -> Optional[ErrorStats]:
        """Retourne les statistiques pour un composant"""
        return self.components_stats.get(component)
    
    def get_all_stats(self) -> Dict[str, ErrorStats]:
        """Retourne toutes les statistiques"""
        return self.components_stats.copy()
    
    def get_recent_errors(self, component: str, limit: int = 10) -> List[ErrorEvent]:
        """Retourne les erreurs récentes pour un composant"""
        events = list(self.events[component])
        return events[-limit:] if events else []
    
    def get_error_summary(self) -> dict:
        """Retourne un résumé global des erreurs"""
        total_components = len(self.components_stats)
        active_components = sum(1 for stats in self.components_stats.values() 
                              if stats.last_error_time and time.time() - stats.last_error_time < 3600)
        
        total_recent_errors = sum(len(stats.recent_errors) for stats in self.components_stats.values())
        
        return {
            'monitor_name': self.name,
            'total_events': self.total_events,
            'total_components': total_components,
            'active_components': active_components,
            'total_recent_errors': total_recent_errors,
            'time_window_minutes': self.time_window_minutes,
            'error_rate_threshold': self.error_rate_threshold,
            'components': {name: stats.total_errors for name, stats in self.components_stats.items()}
        }
    
    def export_errors(self, component: Optional[str] = None, format: str = "json") -> str:
        """Exporte les erreurs au format spécifié"""
        if component:
            events = [event.to_dict() for event in self.events[component]]
        else:
            events = []
            for comp_events in self.events.values():
                events.extend([event.to_dict() for event in comp_events])
        
        if format == "json":
            return json.dumps(events, indent=2)
        else:
            raise ValueError(f"Format non supporté: {format}")
    
    def clear_history(self, component: Optional[str] = None):
        """Efface l'historique des erreurs"""
        if component:
            if component in self.events:
                self.events[component].clear()
                if component in self.components_stats:
                    del self.components_stats[component]
                logger.info(f"Historique effacé pour {component}")
        else:
            self.events.clear()
            self.components_stats.clear()
            self.total_events = 0
            logger.info("Historique complet effacé")
    
    def __repr__(self) -> str:
        return f"ErrorMonitor(name='{self.name}', components={len(self.components_stats)}, events={self.total_events})" 