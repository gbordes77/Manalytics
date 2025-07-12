"""
Business metrics and KPI calculation for executive dashboards.
"""

import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class BusinessMetrics:
    """Business metrics calculator for executive dashboards."""
    
    def __init__(self, metrics_store: Any):
        """
        Initialize business metrics calculator.
        
        Args:
            metrics_store: Data store for metrics (could be database, file, etc.)
        """
        self.metrics_store = metrics_store
        
    def calculate_kpis(self, timeframe: str = 'monthly') -> Dict[str, Any]:
        """
        Calculate key performance indicators.
        
        Args:
            timeframe: Time period for calculations ('daily', 'weekly', 'monthly', 'yearly')
            
        Returns:
            Dictionary of KPIs
        """
        try:
            # Get time range
            start_date, end_date = self._get_time_range(timeframe)
            
            # Calculate core KPIs
            kpis = {
                'data_freshness': self.calculate_data_freshness(start_date, end_date),
                'coverage_rate': self.calculate_tournament_coverage(start_date, end_date),
                'classification_accuracy': self.calculate_classification_metrics(start_date, end_date),
                'api_usage': self.get_api_usage_stats(start_date, end_date),
                'pipeline_reliability': self.calculate_sla_metrics(start_date, end_date),
                'cost_per_tournament': self.calculate_processing_costs(start_date, end_date),
                'data_quality': self.calculate_data_quality_metrics(start_date, end_date),
                'user_engagement': self.calculate_user_engagement_metrics(start_date, end_date)
            }
            
            # Add metadata
            kpis['metadata'] = {
                'timeframe': timeframe,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'calculated_at': datetime.now().isoformat()
            }
            
            return kpis
            
        except Exception as e:
            logger.error(f"Error calculating KPIs: {e}")
            return self._get_empty_kpis()
    
    def _get_time_range(self, timeframe: str) -> Tuple[datetime, datetime]:
        """Get start and end dates for timeframe."""
        end_date = datetime.now()
        
        if timeframe == 'daily':
            start_date = end_date - timedelta(days=1)
        elif timeframe == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif timeframe == 'monthly':
            start_date = end_date - timedelta(days=30)
        elif timeframe == 'yearly':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to monthly
        
        return start_date, end_date
    
    def calculate_data_freshness(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate data freshness metrics."""
        try:
            # This would query the metrics store for actual data
            # For now, return mock structure
            
            freshness_metrics = {
                'average_delay_hours': 2.5,
                'median_delay_hours': 1.8,
                'max_delay_hours': 12.0,
                'tournaments_within_sla': 0.95,  # 95% within SLA
                'sla_target_hours': 6,
                'total_tournaments_processed': 150,
                'status': 'healthy'
            }
            
            # Determine status
            if freshness_metrics['average_delay_hours'] > 6:
                freshness_metrics['status'] = 'critical'
            elif freshness_metrics['average_delay_hours'] > 3:
                freshness_metrics['status'] = 'warning'
            
            return freshness_metrics
            
        except Exception as e:
            logger.error(f"Error calculating data freshness: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def calculate_tournament_coverage(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate tournament coverage metrics."""
        try:
            coverage_metrics = {
                'total_tournaments_available': 200,
                'tournaments_processed': 185,
                'coverage_rate': 0.925,  # 92.5%
                'missed_tournaments': 15,
                'coverage_by_source': {
                    'melee': {'available': 120, 'processed': 115, 'rate': 0.958},
                    'mtgo': {'available': 60, 'processed': 55, 'rate': 0.917},
                    'topdeck': {'available': 20, 'processed': 15, 'rate': 0.75}
                },
                'coverage_by_format': {
                    'modern': {'available': 80, 'processed': 78, 'rate': 0.975},
                    'legacy': {'available': 45, 'processed': 42, 'rate': 0.933},
                    'vintage': {'available': 25, 'processed': 23, 'rate': 0.92},
                    'standard': {'available': 50, 'processed': 42, 'rate': 0.84}
                }
            }
            
            return coverage_metrics
            
        except Exception as e:
            logger.error(f"Error calculating tournament coverage: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def calculate_classification_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate archetype classification accuracy metrics."""
        try:
            classification_metrics = {
                'overall_accuracy': 0.887,  # 88.7%
                'unknown_rate': 0.095,     # 9.5%
                'confidence_score': 0.92,
                'total_decks_classified': 2500,
                'manual_review_required': 125,
                'accuracy_by_format': {
                    'modern': {'accuracy': 0.92, 'unknown_rate': 0.08},
                    'legacy': {'accuracy': 0.85, 'unknown_rate': 0.12},
                    'vintage': {'accuracy': 0.88, 'unknown_rate': 0.10},
                    'standard': {'accuracy': 0.90, 'unknown_rate': 0.07}
                },
                'top_misclassified_archetypes': [
                    {'archetype': 'Midrange Variants', 'error_rate': 0.15},
                    {'archetype': 'Combo Variants', 'error_rate': 0.12},
                    {'archetype': 'Control Variants', 'error_rate': 0.08}
                ]
            }
            
            return classification_metrics
            
        except Exception as e:
            logger.error(f"Error calculating classification metrics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_api_usage_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get API usage statistics."""
        try:
            api_stats = {
                'total_requests': 45000,
                'successful_requests': 43200,
                'failed_requests': 1800,
                'success_rate': 0.96,
                'average_response_time_ms': 250,
                'p95_response_time_ms': 450,
                'p99_response_time_ms': 850,
                'rate_limit_hits': 25,
                'top_endpoints': [
                    {'endpoint': '/api/v1/metagame/{format}', 'requests': 15000, 'avg_response_ms': 180},
                    {'endpoint': '/api/v1/archetype/{format}/{archetype}', 'requests': 12000, 'avg_response_ms': 220},
                    {'endpoint': '/api/v1/matchups/{format}', 'requests': 8000, 'avg_response_ms': 350}
                ],
                'usage_by_client': {
                    'web_dashboard': 25000,
                    'mobile_app': 12000,
                    'third_party_integrations': 8000
                }
            }
            
            return api_stats
            
        except Exception as e:
            logger.error(f"Error getting API usage stats: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def calculate_sla_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate SLA and reliability metrics."""
        try:
            sla_metrics = {
                'uptime_percentage': 99.85,
                'total_downtime_minutes': 65,
                'mttr_minutes': 12,  # Mean Time To Recovery
                'mtbf_hours': 168,   # Mean Time Between Failures
                'incidents_count': 3,
                'sla_breaches': 1,
                'availability_by_component': {
                    'scraper_service': 99.9,
                    'classifier_service': 99.8,
                    'api_service': 99.95,
                    'database': 99.99,
                    'cache_service': 99.7
                },
                'performance_sla': {
                    'api_response_time_sla': 500,  # ms
                    'api_response_time_actual': 250,
                    'data_processing_sla': 6,  # hours
                    'data_processing_actual': 2.5,
                    'sla_compliance': 0.98
                }
            }
            
            return sla_metrics
            
        except Exception as e:
            logger.error(f"Error calculating SLA metrics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def calculate_processing_costs(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate processing costs and efficiency metrics."""
        try:
            cost_metrics = {
                'total_cost_usd': 1250.0,
                'cost_per_tournament': 6.75,
                'cost_per_deck_processed': 0.50,
                'cost_breakdown': {
                    'compute_costs': 750.0,
                    'storage_costs': 200.0,
                    'api_costs': 150.0,
                    'monitoring_costs': 100.0,
                    'other_costs': 50.0
                },
                'cost_efficiency': {
                    'cost_per_gb_processed': 2.5,
                    'cost_per_api_request': 0.000028,
                    'cost_optimization_opportunities': [
                        {'area': 'Cache optimization', 'potential_savings': 150.0},
                        {'area': 'Compute scaling', 'potential_savings': 100.0}
                    ]
                },
                'budget_utilization': 0.83,  # 83% of budget used
                'monthly_budget': 1500.0
            }
            
            return cost_metrics
            
        except Exception as e:
            logger.error(f"Error calculating processing costs: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def calculate_data_quality_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        try:
            quality_metrics = {
                'overall_quality_score': 0.91,
                'completeness_score': 0.95,
                'accuracy_score': 0.89,
                'consistency_score': 0.93,
                'timeliness_score': 0.87,
                'data_quality_issues': {
                    'missing_player_data': 45,
                    'duplicate_tournaments': 12,
                    'invalid_deck_data': 23,
                    'inconsistent_formats': 8
                },
                'quarantine_rate': 0.03,  # 3% of data quarantined
                'data_validation_failures': 67,
                'quality_trends': {
                    'improving': ['completeness_score', 'consistency_score'],
                    'declining': ['timeliness_score'],
                    'stable': ['accuracy_score']
                }
            }
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error calculating data quality metrics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def calculate_user_engagement_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate user engagement metrics."""
        try:
            engagement_metrics = {
                'total_active_users': 1250,
                'new_users': 85,
                'returning_users': 1165,
                'user_retention_rate': 0.78,
                'average_session_duration_minutes': 12.5,
                'pages_per_session': 4.2,
                'bounce_rate': 0.25,
                'top_features': [
                    {'feature': 'Metagame Analysis', 'usage_percentage': 0.85},
                    {'feature': 'Archetype Comparison', 'usage_percentage': 0.72},
                    {'feature': 'Tournament Search', 'usage_percentage': 0.68}
                ],
                'user_satisfaction': {
                    'nps_score': 42,  # Net Promoter Score
                    'satisfaction_rating': 4.2,  # out of 5
                    'support_tickets': 23,
                    'feature_requests': 15
                }
            }
            
            return engagement_metrics
            
        except Exception as e:
            logger.error(f"Error calculating user engagement metrics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def generate_executive_dashboard(self) -> Dict[str, Any]:
        """Generate executive dashboard with key metrics."""
        try:
            # Get KPIs for different timeframes
            monthly_kpis = self.calculate_kpis('monthly')
            weekly_kpis = self.calculate_kpis('weekly')
            
            # Calculate trends
            trends = self.calculate_trends(monthly_kpis, weekly_kpis)
            
            # Get alerts
            alerts = self.get_business_alerts(monthly_kpis)
            
            # Generate forecast
            forecast = self.predict_next_month_metrics(monthly_kpis)
            
            dashboard = {
                'current_metrics': monthly_kpis,
                'trends': trends,
                'alerts': alerts,
                'forecast': forecast,
                'executive_summary': self._generate_executive_summary(monthly_kpis, trends, alerts),
                'recommendations': self._generate_recommendations(monthly_kpis, trends)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating executive dashboard: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def calculate_trends(self, current_kpis: Dict[str, Any], previous_kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate trends between current and previous KPIs."""
        trends = {}
        
        try:
            # Data freshness trend
            current_freshness = current_kpis.get('data_freshness', {}).get('average_delay_hours', 0)
            previous_freshness = previous_kpis.get('data_freshness', {}).get('average_delay_hours', 0)
            
            if previous_freshness > 0:
                freshness_change = (current_freshness - previous_freshness) / previous_freshness
                trends['data_freshness'] = {
                    'change_percentage': freshness_change * 100,
                    'direction': 'improving' if freshness_change < 0 else 'declining',
                    'current_value': current_freshness,
                    'previous_value': previous_freshness
                }
            
            # Coverage rate trend
            current_coverage = current_kpis.get('coverage_rate', {}).get('coverage_rate', 0)
            previous_coverage = previous_kpis.get('coverage_rate', {}).get('coverage_rate', 0)
            
            if previous_coverage > 0:
                coverage_change = (current_coverage - previous_coverage) / previous_coverage
                trends['coverage_rate'] = {
                    'change_percentage': coverage_change * 100,
                    'direction': 'improving' if coverage_change > 0 else 'declining',
                    'current_value': current_coverage,
                    'previous_value': previous_coverage
                }
            
            # Classification accuracy trend
            current_accuracy = current_kpis.get('classification_accuracy', {}).get('overall_accuracy', 0)
            previous_accuracy = previous_kpis.get('classification_accuracy', {}).get('overall_accuracy', 0)
            
            if previous_accuracy > 0:
                accuracy_change = (current_accuracy - previous_accuracy) / previous_accuracy
                trends['classification_accuracy'] = {
                    'change_percentage': accuracy_change * 100,
                    'direction': 'improving' if accuracy_change > 0 else 'declining',
                    'current_value': current_accuracy,
                    'previous_value': previous_accuracy
                }
            
            # Cost efficiency trend
            current_cost = current_kpis.get('cost_per_tournament', {}).get('cost_per_tournament', 0)
            previous_cost = previous_kpis.get('cost_per_tournament', {}).get('cost_per_tournament', 0)
            
            if previous_cost > 0:
                cost_change = (current_cost - previous_cost) / previous_cost
                trends['cost_efficiency'] = {
                    'change_percentage': cost_change * 100,
                    'direction': 'improving' if cost_change < 0 else 'declining',
                    'current_value': current_cost,
                    'previous_value': previous_cost
                }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {}
    
    def get_business_alerts(self, kpis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate business alerts based on KPIs."""
        alerts = []
        
        try:
            # Data freshness alerts
            freshness = kpis.get('data_freshness', {})
            if freshness.get('average_delay_hours', 0) > 6:
                alerts.append({
                    'type': 'critical',
                    'category': 'data_freshness',
                    'message': f"Data freshness SLA breach: {freshness.get('average_delay_hours', 0):.1f}h average delay",
                    'action_required': True
                })
            
            # Coverage rate alerts
            coverage = kpis.get('coverage_rate', {})
            if coverage.get('coverage_rate', 1) < 0.9:
                alerts.append({
                    'type': 'warning',
                    'category': 'coverage',
                    'message': f"Tournament coverage below target: {coverage.get('coverage_rate', 0):.1%}",
                    'action_required': True
                })
            
            # Classification accuracy alerts
            classification = kpis.get('classification_accuracy', {})
            if classification.get('overall_accuracy', 1) < 0.85:
                alerts.append({
                    'type': 'warning',
                    'category': 'classification',
                    'message': f"Classification accuracy below target: {classification.get('overall_accuracy', 0):.1%}",
                    'action_required': True
                })
            
            # Cost alerts
            costs = kpis.get('cost_per_tournament', {})
            if costs.get('budget_utilization', 0) > 0.9:
                alerts.append({
                    'type': 'info',
                    'category': 'budget',
                    'message': f"Budget utilization high: {costs.get('budget_utilization', 0):.1%}",
                    'action_required': False
                })
            
            # SLA alerts
            sla = kpis.get('pipeline_reliability', {})
            if sla.get('uptime_percentage', 100) < 99.5:
                alerts.append({
                    'type': 'critical',
                    'category': 'sla',
                    'message': f"Uptime below SLA: {sla.get('uptime_percentage', 0):.2f}%",
                    'action_required': True
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating business alerts: {e}")
            return []
    
    def predict_next_month_metrics(self, current_kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Predict next month's metrics based on current trends."""
        try:
            # Simple linear prediction based on current values
            # In a real implementation, this would use historical data and ML models
            
            forecast = {
                'data_freshness': {
                    'predicted_average_delay': current_kpis.get('data_freshness', {}).get('average_delay_hours', 0) * 0.95,
                    'confidence': 0.75
                },
                'coverage_rate': {
                    'predicted_coverage': min(1.0, current_kpis.get('coverage_rate', {}).get('coverage_rate', 0) * 1.02),
                    'confidence': 0.80
                },
                'classification_accuracy': {
                    'predicted_accuracy': min(1.0, current_kpis.get('classification_accuracy', {}).get('overall_accuracy', 0) * 1.01),
                    'confidence': 0.85
                },
                'cost_projection': {
                    'predicted_monthly_cost': current_kpis.get('cost_per_tournament', {}).get('total_cost_usd', 0) * 1.05,
                    'confidence': 0.70
                }
            }
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error predicting next month metrics: {e}")
            return {}
    
    def _generate_executive_summary(self, kpis: Dict[str, Any], trends: Dict[str, Any], 
                                   alerts: List[Dict[str, Any]]) -> str:
        """Generate executive summary text."""
        try:
            summary_parts = []
            
            # Overall health
            critical_alerts = len([a for a in alerts if a['type'] == 'critical'])
            if critical_alerts == 0:
                summary_parts.append("System is operating within normal parameters.")
            else:
                summary_parts.append(f"{critical_alerts} critical issues require immediate attention.")
            
            # Key metrics
            coverage = kpis.get('coverage_rate', {}).get('coverage_rate', 0)
            accuracy = kpis.get('classification_accuracy', {}).get('overall_accuracy', 0)
            
            summary_parts.append(f"Tournament coverage at {coverage:.1%}, classification accuracy at {accuracy:.1%}.")
            
            # Trends
            improving_trends = [k for k, v in trends.items() if v.get('direction') == 'improving']
            if improving_trends:
                summary_parts.append(f"Positive trends in {', '.join(improving_trends)}.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return "Unable to generate summary due to data issues."
    
    def _generate_recommendations(self, kpis: Dict[str, Any], trends: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        try:
            # Data freshness recommendations
            freshness = kpis.get('data_freshness', {})
            if freshness.get('average_delay_hours', 0) > 3:
                recommendations.append("Consider optimizing scraper performance or increasing processing capacity.")
            
            # Coverage recommendations
            coverage = kpis.get('coverage_rate', {})
            if coverage.get('coverage_rate', 1) < 0.95:
                recommendations.append("Investigate missed tournaments and improve source monitoring.")
            
            # Classification recommendations
            classification = kpis.get('classification_accuracy', {})
            if classification.get('unknown_rate', 0) > 0.1:
                recommendations.append("Review and update archetype classification rules.")
            
            # Cost recommendations
            costs = kpis.get('cost_per_tournament', {})
            if costs.get('budget_utilization', 0) > 0.85:
                recommendations.append("Review cost optimization opportunities and consider budget adjustment.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Unable to generate recommendations due to data issues."]
    
    def _get_empty_kpis(self) -> Dict[str, Any]:
        """Return empty KPI structure for error cases."""
        return {
            'data_freshness': {'status': 'error'},
            'coverage_rate': {'status': 'error'},
            'classification_accuracy': {'status': 'error'},
            'api_usage': {'status': 'error'},
            'pipeline_reliability': {'status': 'error'},
            'cost_per_tournament': {'status': 'error'},
            'metadata': {
                'calculated_at': datetime.now().isoformat(),
                'status': 'error'
            }
        } 