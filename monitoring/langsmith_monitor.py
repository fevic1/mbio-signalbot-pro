"""
Advanced LangSmith monitoring with cost tracking, latency alerts, and analytics.
"""
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List
import json

logger = logging.getLogger(__name__)

class LangSmithMonitor:
    """Monitor LangSmith traces for costs, latency, and performance."""
    
    def __init__(self):
        self.call_history = []
        self.daily_stats = {
            'date': datetime.now(timezone.utc).date().isoformat(),
            'total_calls': 0,
            'total_tokens': 0,
            'total_cost_usd': 0.0,
            'avg_latency_ms': 0.0,
            'errors': 0,
            'by_model': {}
        }
        
        # Cost per 1K tokens (approximate)
        self.cost_per_1k_tokens = {
            'groq': 0.0002,  # Groq is very cheap
            'openai': 0.002,
            'anthropic': 0.003
        }
        
        # Alert thresholds
        self.latency_alert_threshold_ms = 5000  # Alert if latency > 5s
        self.error_rate_threshold = 0.1  # Alert if > 10% errors
        self.cost_alert_threshold_usd = 5.0  # Alert if daily cost > $5
    
    def record_call(self, model: str, tokens_used: int, latency_ms: float, 
                   success: bool, provider: str = 'groq'):
        """Record an LLM call for analytics."""
        call_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'model': model,
            'tokens': tokens_used,
            'latency_ms': latency_ms,
            'success': success,
            'provider': provider,
            'cost_usd': self._calculate_cost(tokens_used, provider)
        }
        
        self.call_history.append(call_record)
        
        # Update daily stats
        self._update_daily_stats(call_record)
        
        # Check for alerts
        self._check_alerts(call_record)
        
        # Keep only last 1000 calls in memory
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-1000:]
    
    def _calculate_cost(self, tokens: int, provider: str) -> float:
        """Calculate cost based on token usage."""
        cost_per_token = self.cost_per_1k_tokens.get(provider, 0.001) / 1000
        return tokens * cost_per_token
    
    def _update_daily_stats(self, call: Dict):
        """Update daily statistics."""
        self.daily_stats['total_calls'] += 1
        self.daily_stats['total_tokens'] += call['tokens']
        self.daily_stats['total_cost_usd'] += call['cost_usd']
        
        if not call['success']:
            self.daily_stats['errors'] += 1
        
        # Update model-specific stats
        model = call['model']
        if model not in self.daily_stats['by_model']:
            self.daily_stats['by_model'][model] = {
                'calls': 0,
                'tokens': 0,
                'total_latency_ms': 0
            }
        
        self.daily_stats['by_model'][model]['calls'] += 1
        self.daily_stats['by_model'][model]['tokens'] += call['tokens']
        self.daily_stats['by_model'][model]['total_latency_ms'] += call['latency_ms']
        
        # Calculate average latency
        total_latency = sum(m['total_latency_ms'] for m in self.daily_stats['by_model'].values())
        total_calls = sum(m['calls'] for m in self.daily_stats['by_model'].values())
        self.daily_stats['avg_latency_ms'] = total_latency / total_calls if total_calls > 0 else 0
    
    def _check_alerts(self, call: Dict):
        """Check for alert conditions."""
        alerts = []
        
        # High latency alert
        if call['latency_ms'] > self.latency_alert_threshold_ms:
            alerts.append(f"⚠️ High latency: {call['latency_ms']:.0f}ms for {call['model']}")
        
        # Error rate alert
        if self.daily_stats['total_calls'] > 10:
            error_rate = self.daily_stats['errors'] / self.daily_stats['total_calls']
            if error_rate > self.error_rate_threshold:
                alerts.append(f"⚠️ High error rate: {error_rate:.1%}")
        
        # Cost alert
        if self.daily_stats['total_cost_usd'] > self.cost_alert_threshold_usd:
            alerts.append(f"⚠️ High daily cost: ${self.daily_stats['total_cost_usd']:.2f}")
        
        # Log alerts
        for alert in alerts:
            logger.warning(alert)
    
    def get_daily_summary(self) -> str:
        """Generate daily summary report."""
        stats = self.daily_stats
        
        summary = f"""
📊 **Daily LangSmith Report**
━━━━━━━━━━━━━━━━━━━━━━━━
📅 Date: {stats['date']}
🔢 Total Calls: {stats['total_calls']}
💰 Total Cost: ${stats['total_cost_usd']:.4f}
🎯 Total Tokens: {stats['total_tokens']:,}
⚡ Avg Latency: {stats['avg_latency_ms']:.0f}ms
❌ Errors: {stats['errors']} ({stats['errors']/max(stats['total_calls'],1):.1%})

**By Model:**
"""
        for model, model_stats in stats['by_model'].items():
            avg_lat = model_stats['total_latency_ms'] / model_stats['calls'] if model_stats['calls'] > 0 else 0
            summary += f"  • {model}: {model_stats['calls']} calls, {model_stats['tokens']:,} tokens, {avg_lat:.0f}ms avg\n"
        
        return summary
    
    def save_stats(self, filepath: str = 'data/langsmith_daily_stats.json'):
        """Save daily stats to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.daily_stats, f, indent=2)
            logger.debug(f"Saved LangSmith stats to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save LangSmith stats: {e}")
    
    def load_stats(self, filepath: str = 'data/langsmith_daily_stats.json'):
        """Load daily stats from file."""
        try:
            with open(filepath, 'r') as f:
                self.daily_stats = json.load(f)
            logger.debug(f"Loaded LangSmith stats from {filepath}")
        except Exception as e:
            logger.debug(f"No existing LangSmith stats found: {e}")

# Singleton instance
_monitor_instance = None

def get_langsmith_monitor() -> LangSmithMonitor:
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = LangSmithMonitor()
        _monitor_instance.load_stats()
    return _monitor_instance
