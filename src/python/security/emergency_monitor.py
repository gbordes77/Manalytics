import time
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import asyncio
from enum import Enum

# Configuration logging sécurisé
security_logger = logging.getLogger('security')
security_handler = logging.FileHandler('logs/security_alerts.log')
security_handler.setLevel(logging.WARNING)
security_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
security_handler.setFormatter(security_formatter)
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.WARNING)

class ThreatLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class SecurityEvent:
    """Événement de sécurité"""
    timestamp: datetime
    event_type: str
    ip_address: str
    endpoint: str
    threat_level: ThreatLevel
    details: Dict
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class IPStats:
    """Statistiques par IP"""
    failed_attempts: deque = field(default_factory=deque)
    blocked_until: Optional[datetime] = None
    block_count: int = 0
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    threat_score: float = 0.0

class EmergencySecurityMonitor:
    """Monitoring sécurité d'urgence pour déploiement immédiat
    
    🚨 FONCTIONNALITÉS CRITIQUES :
    - Détection d'attaques en temps réel
    - Blocage automatique d'IPs malveillantes
    - Alertes immédiates sur événements suspects
    - Rate limiting intelligent
    - Analyse comportementale basique
    - Reporting automatique
    """
    
    def __init__(self, 
                 block_after_failures: int = 5,
                 window_seconds: int = 300,
                 max_requests_per_minute: int = 60):
        
        # Configuration de base
        self.block_threshold = block_after_failures
        self.window = window_seconds
        self.max_requests_per_minute = max_requests_per_minute
        
        # Stockage des données
        self.ip_stats: Dict[str, IPStats] = defaultdict(IPStats)
        self.blocked_ips: Set[str] = set()
        self.security_events: List[SecurityEvent] = []
        
        # Rate limiting
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        
        # Patterns suspects
        self.suspicious_patterns = [
            r'union\s+select',
            r'or\s+1\s*=\s*1',
            r'<script',
            r'javascript:',
            r'eval\(',
            r'exec\(',
            r'system\(',
            r'\.\./',
            r'admin',
            r'root',
            r'password',
            r'passwd'
        ]
        
        # Monitoring stats
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'security_events': 0,
            'start_time': datetime.utcnow(),
            'last_cleanup': datetime.utcnow()
        }
        
        # Logs
        self.logger = logging.getLogger(__name__)
        
        # Initialisation
        self._setup_logging()
        self._load_persistent_data()
        
        # Tâche de maintenance (sera démarrée lors de la première utilisation)
        self._maintenance_task = None
        
        security_logger.info("🛡️  Emergency Security Monitor initialized", extra={
            'block_threshold': block_after_failures,
            'window_seconds': window_seconds,
            'max_rpm': max_requests_per_minute
        })
    
    def _setup_logging(self):
        """Configuration logging sécurisé"""
        
        # Créer répertoire logs si nécessaire
        Path('logs').mkdir(exist_ok=True)
        
        # Handler pour événements sécurité
        if not security_logger.handlers:
            security_logger.addHandler(security_handler)
    
    def _load_persistent_data(self):
        """Charger les données persistantes (IPs bloquées, etc.)"""
        
        blocked_ips_file = Path('logs/blocked_ips.json')
        
        if blocked_ips_file.exists():
            try:
                with open(blocked_ips_file, 'r') as f:
                    data = json.load(f)
                    
                # Recharger IPs bloquées non expirées
                current_time = datetime.utcnow()
                for ip, block_until_str in data.items():
                    block_until = datetime.fromisoformat(block_until_str)
                    if block_until > current_time:
                        self.blocked_ips.add(ip)
                        self.ip_stats[ip].blocked_until = block_until
                        
                self.logger.info(f"Loaded {len(self.blocked_ips)} blocked IPs from persistence")
                
            except Exception as e:
                self.logger.error(f"Error loading persistent data: {e}")
    
    def _save_persistent_data(self):
        """Sauvegarder les données persistantes"""
        
        try:
            # Sauvegarder IPs bloquées
            blocked_data = {}
            for ip in self.blocked_ips:
                if ip in self.ip_stats and self.ip_stats[ip].blocked_until:
                    blocked_data[ip] = self.ip_stats[ip].blocked_until.isoformat()
            
            with open('logs/blocked_ips.json', 'w') as f:
                json.dump(blocked_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving persistent data: {e}")
    
    def _ensure_maintenance_task(self):
        """S'assurer que la tâche de maintenance est démarrée"""
        if self._maintenance_task is None:
            try:
                self._maintenance_task = asyncio.create_task(self._maintenance_loop())
            except RuntimeError:
                # Pas d'event loop, ce n'est pas grave
                pass

    def record_request(self, ip: str, endpoint: str, user_agent: str = None) -> bool:
        """Enregistrer une requête et vérifier rate limiting"""
        
        self._ensure_maintenance_task()
        self.stats['total_requests'] += 1
        
        # Vérifier si IP est bloquée
        if self.is_blocked(ip):
            self.stats['blocked_requests'] += 1
            return False
        
        # Rate limiting
        if self._check_rate_limit(ip):
            self._record_security_event(
                ip=ip,
                endpoint=endpoint,
                event_type="RATE_LIMIT_EXCEEDED",
                threat_level=ThreatLevel.MEDIUM,
                details={"requests_per_minute": len(self.request_counts[ip])},
                user_agent=user_agent
            )
            return False
        
        # Enregistrer la requête
        current_time = time.time()
        self.request_counts[ip].append(current_time)
        
        # Nettoyer anciennes requêtes
        cutoff = current_time - 60  # 1 minute
        while self.request_counts[ip] and self.request_counts[ip][0] < cutoff:
            self.request_counts[ip].popleft()
        
        # Mettre à jour stats IP
        self.ip_stats[ip].last_seen = datetime.utcnow()
        
        return True
    
    def record_failed_attempt(self, ip: str, endpoint: str, reason: str, 
                            user_agent: str = None, details: Dict = None):
        """Enregistrer une tentative échouée"""
        
        now = time.time()
        details = details or {}
        
        # Nettoyer anciennes tentatives
        self.ip_stats[ip].failed_attempts = deque(
            [t for t in self.ip_stats[ip].failed_attempts 
             if now - t < self.window]
        )
        
        # Ajouter nouvelle tentative
        self.ip_stats[ip].failed_attempts.append(now)
        
        # Calculer score de menace
        attempt_count = len(self.ip_stats[ip].failed_attempts)
        self.ip_stats[ip].threat_score = min(100, attempt_count * 10)
        
        # Déterminer niveau de menace
        if attempt_count >= self.block_threshold:
            threat_level = ThreatLevel.HIGH
        elif attempt_count >= self.block_threshold // 2:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW
        
        # Enregistrer événement
        self._record_security_event(
            ip=ip,
            endpoint=endpoint,
            event_type="FAILED_ATTEMPT",
            threat_level=threat_level,
            details={
                "reason": reason,
                "attempt_count": attempt_count,
                "threat_score": self.ip_stats[ip].threat_score,
                **details
            },
            user_agent=user_agent
        )
        
        # Bloquer si nécessaire
        if attempt_count >= self.block_threshold:
            self.block_ip(ip, f"Too many failed attempts: {reason}")
    
    def analyze_request_content(self, ip: str, endpoint: str, content: str,
                              user_agent: str = None) -> bool:
        """Analyser le contenu d'une requête pour détecter des attaques"""
        
        import re
        
        suspicious_found = []
        
        # Vérifier patterns suspects
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                suspicious_found.append(pattern)
        
        if suspicious_found:
            self._record_security_event(
                ip=ip,
                endpoint=endpoint,
                event_type="SUSPICIOUS_CONTENT",
                threat_level=ThreatLevel.HIGH,
                details={
                    "patterns_found": suspicious_found,
                    "content_sample": content[:200] + "..." if len(content) > 200 else content
                },
                user_agent=user_agent
            )
            
            # Bloquer immédiatement pour injection SQL/XSS
            if any(p in ['union\\s+select', 'or\\s+1\\s*=\\s*1', '<script'] 
                   for p in suspicious_found):
                self.block_ip(ip, "Injection attack detected")
                return False
        
        return True
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Vérifier rate limiting"""
        
        current_time = time.time()
        
        # Compter requêtes dans la dernière minute
        cutoff = current_time - 60
        recent_requests = [t for t in self.request_counts[ip] if t > cutoff]
        
        return len(recent_requests) >= self.max_requests_per_minute
    
    def block_ip(self, ip: str, reason: str, duration_minutes: int = 60):
        """Bloquer une IP suspecte"""
        
        if ip in self.blocked_ips:
            return  # Déjà bloquée
        
        block_until = datetime.utcnow().replace(microsecond=0) + \
                     timedelta(minutes=duration_minutes)
        
        self.blocked_ips.add(ip)
        self.ip_stats[ip].blocked_until = block_until
        self.ip_stats[ip].block_count += 1
        
        # Événement critique
        self._record_security_event(
            ip=ip,
            endpoint="SYSTEM",
            event_type="IP_BLOCKED",
            threat_level=ThreatLevel.CRITICAL,
            details={
                "reason": reason,
                "duration_minutes": duration_minutes,
                "blocked_until": block_until.isoformat(),
                "block_count": self.ip_stats[ip].block_count,
                "threat_score": self.ip_stats[ip].threat_score
            }
        )
        
        # Sauvegarder
        self._save_persistent_data()
        
        security_logger.critical(f"🚨 IP BLOCKED: {ip} - {reason}", extra={
            'ip': ip,
            'reason': reason,
            'duration_minutes': duration_minutes,
            'block_count': self.ip_stats[ip].block_count
        })
    
    def is_blocked(self, ip: str) -> bool:
        """Vérifier si IP est bloquée"""
        
        if ip not in self.blocked_ips:
            return False
        
        # Vérifier si le blocage a expiré
        if ip in self.ip_stats and self.ip_stats[ip].blocked_until:
            if datetime.utcnow() > self.ip_stats[ip].blocked_until:
                # Débloquer
                self.blocked_ips.remove(ip)
                self.ip_stats[ip].blocked_until = None
                
                security_logger.info(f"IP unblocked (expired): {ip}")
                return False
        
        return True
    
    def _record_security_event(self, ip: str, endpoint: str, event_type: str,
                             threat_level: ThreatLevel, details: Dict,
                             user_agent: str = None):
        """Enregistrer un événement de sécurité"""
        
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            ip_address=ip,
            endpoint=endpoint,
            threat_level=threat_level,
            details=details,
            user_agent=user_agent
        )
        
        self.security_events.append(event)
        self.stats['security_events'] += 1
        
        # Limiter historique
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-5000:]
        
        # Logger selon le niveau
        log_msg = f"{event_type} from {ip} on {endpoint}"
        
        if threat_level == ThreatLevel.CRITICAL:
            security_logger.critical(log_msg, extra=details)
        elif threat_level == ThreatLevel.HIGH:
            security_logger.error(log_msg, extra=details)
        elif threat_level == ThreatLevel.MEDIUM:
            security_logger.warning(log_msg, extra=details)
        else:
            security_logger.info(log_msg, extra=details)
    
    def get_security_status(self) -> Dict:
        """Obtenir status sécurité actuel"""
        
        current_time = datetime.utcnow()
        
        # Top IPs suspectes
        suspicious_ips = []
        for ip, stats in self.ip_stats.items():
            if len(stats.failed_attempts) >= self.block_threshold // 2:
                suspicious_ips.append({
                    'ip': ip,
                    'failed_attempts': len(stats.failed_attempts),
                    'threat_score': stats.threat_score,
                    'first_seen': stats.first_seen.isoformat(),
                    'last_seen': stats.last_seen.isoformat()
                })
        
        # Événements récents
        recent_events = []
        for event in self.security_events[-50:]:  # 50 derniers
            recent_events.append({
                'timestamp': event.timestamp.isoformat(),
                'type': event.event_type,
                'ip': event.ip_address,
                'endpoint': event.endpoint,
                'threat_level': event.threat_level.value,
                'details': event.details
            })
        
        return {
            "timestamp": current_time.isoformat(),
            "monitoring_since": self.stats['start_time'].isoformat(),
            "blocked_ips": list(self.blocked_ips),
            "total_blocked": len(self.blocked_ips),
            "suspicious_ips": suspicious_ips,
            "recent_events": recent_events,
            "statistics": {
                "total_requests": self.stats['total_requests'],
                "blocked_requests": self.stats['blocked_requests'],
                "security_events": self.stats['security_events'],
                "block_rate": f"{(self.stats['blocked_requests'] / max(1, self.stats['total_requests']) * 100):.1f}%"
            },
            "configuration": {
                "block_threshold": self.block_threshold,
                "window_seconds": self.window,
                "max_requests_per_minute": self.max_requests_per_minute
            }
        }
    
    def get_threat_report(self) -> Dict:
        """Générer rapport de menaces détaillé"""
        
        # Analyser les menaces par type
        threat_analysis = defaultdict(int)
        for event in self.security_events:
            threat_analysis[event.event_type] += 1
        
        # Top pays/régions (simulation basique)
        ip_origins = {}
        for ip in self.ip_stats.keys():
            # Simulation géolocalisation basique
            if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('127.'):
                ip_origins[ip] = "Local/Private"
            else:
                ip_origins[ip] = "Internet"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "threat_summary": {
                "total_threats": len(self.security_events),
                "unique_attackers": len(self.ip_stats),
                "blocked_ips": len(self.blocked_ips),
                "critical_events": len([e for e in self.security_events 
                                      if e.threat_level == ThreatLevel.CRITICAL])
            },
            "threat_types": dict(threat_analysis),
            "attack_origins": ip_origins,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Générer recommandations de sécurité"""
        
        recommendations = []
        
        # Analyse des patterns
        if len(self.blocked_ips) > 10:
            recommendations.append("Considérer un WAF plus robuste - nombreuses IPs bloquées")
        
        if self.stats['blocked_requests'] / max(1, self.stats['total_requests']) > 0.05:
            recommendations.append("Taux de blocage élevé - revoir la configuration")
        
        # Vérifier types d'attaques
        injection_events = [e for e in self.security_events 
                          if e.event_type == "SUSPICIOUS_CONTENT"]
        if len(injection_events) > 5:
            recommendations.append("Nombreuses tentatives d'injection - renforcer validation input")
        
        # Rate limiting
        rate_limit_events = [e for e in self.security_events 
                           if e.event_type == "RATE_LIMIT_EXCEEDED"]
        if len(rate_limit_events) > 20:
            recommendations.append("Nombreux dépassements rate limit - ajuster les seuils")
        
        return recommendations
    
    async def _maintenance_loop(self):
        """Boucle de maintenance en arrière-plan"""
        
        while True:
            try:
                await asyncio.sleep(60)  # Toutes les minutes
                
                # Nettoyer données expirées
                self._cleanup_expired_data()
                
                # Sauvegarder données
                self._save_persistent_data()
                
                # Générer rapport périodique
                if datetime.utcnow().minute % 5 == 0:  # Toutes les 5 minutes
                    self._generate_periodic_report()
                
            except Exception as e:
                self.logger.error(f"Error in maintenance loop: {e}")
    
    def _cleanup_expired_data(self):
        """Nettoyer les données expirées"""
        
        current_time = time.time()
        
        # Nettoyer compteurs de requêtes
        for ip in list(self.request_counts.keys()):
            cutoff = current_time - 60
            while self.request_counts[ip] and self.request_counts[ip][0] < cutoff:
                self.request_counts[ip].popleft()
            
            # Supprimer entrées vides
            if not self.request_counts[ip]:
                del self.request_counts[ip]
        
        # Nettoyer tentatives échouées
        for ip in list(self.ip_stats.keys()):
            cutoff = current_time - self.window
            self.ip_stats[ip].failed_attempts = deque(
                [t for t in self.ip_stats[ip].failed_attempts if t > cutoff]
            )
        
        # Nettoyer événements anciens (garder 24h)
        cutoff_datetime = datetime.utcnow() - timedelta(hours=24)
        self.security_events = [e for e in self.security_events 
                              if e.timestamp > cutoff_datetime]
    
    def _generate_periodic_report(self):
        """Générer rapport périodique"""
        
        try:
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_minutes": (datetime.utcnow() - self.stats['start_time']).total_seconds() / 60,
                "stats": self.stats,
                "active_blocks": len(self.blocked_ips),
                "suspicious_ips": len([ip for ip, stats in self.ip_stats.items() 
                                     if len(stats.failed_attempts) >= self.block_threshold // 2])
            }
            
            # Sauvegarder rapport
            report_file = Path(f"logs/security_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Generated periodic security report: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating periodic report: {e}")


# Instance globale
security_monitor = EmergencySecurityMonitor(
    block_after_failures=5,
    window_seconds=300,
    max_requests_per_minute=60
) 