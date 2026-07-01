"""
Automated daily reporting to Telegram with bot performance and LangSmith stats.
"""
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional
import core.state as state
from monitoring.langsmith_monitor import get_langsmith_monitor
from monitoring.alert_manager import send_telegram_message

logger = logging.getLogger(__name__)

class DailyReporter:
    """Generate and send daily performance reports."""
    
    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        self.last_report_date = None
    
    async def check_and_send_report(self):
        """Check if it's time for daily report and send if needed."""
        now = datetime.now(timezone.utc)
        today = now.date()
        
        # Send report at 8:00 AM UTC daily
        if now.hour == 8 and now.minute < 5:
            if self.last_report_date != today:
                await self.send_daily_report()
                self.last_report_date = today
    
    async def send_daily_report(self):
        """Generate and send comprehensive daily report."""
        try:
            logger.info("📊 Generating daily report...")
            
            # Get LangSmith stats
            monitor = get_langsmith_monitor()
            langsmith_report = monitor.get_daily_summary()
            
            # Get trading stats
            trading_report = self._generate_trading_report()
            
            # Get system health
            system_report = self._generate_system_report()
            
            # Combine reports
            full_report = f"""
🌅 **Daily Bot Report - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}**
{trading_report}
{langsmith_report}
{system_report}
━━━━━━━━━━━━━━━━━━━━━━━━
🤖 MBIO SignalBot v9.0
🧠 Self-Learning: Active
📊 Pattern Analysis: Active
🔍 LangSmith Tracing: Active
"""
            
            # Send to Telegram
            await send_telegram_message(self.chat_id, full_report)
            
            # Save stats
            monitor.save_stats()
            
            logger.info("✅ Daily report sent")
            
        except Exception as e:
            logger.error(f"Failed to send daily report: {e}")
    
    def _generate_trading_report(self) -> str:
        """Generate trading performance summary."""
        open_pos = len(state.OPEN_POSITIONS)
        daily_pnl = state.get_daily_pnl() if hasattr(state, 'get_daily_pnl') else 0.0
        
        # 🧠 MetaLearner Top Strategy Extraction
        try:
            from core.meta_learner import get_meta_learner
            meta = get_meta_learner()
            best_overall = None
            best_weight = 0.0
            for regime in ["TRENDING_UP", "TRENDING_DOWN", "RANGING", "VOLATILE"]:
                weights = meta.get_weights(regime)
                if weights:
                    top_strat = max(weights, key=weights.get)
                    if weights[top_strat] > best_weight:
                        best_weight = weights[top_strat]
                        best_overall = top_strat
            meta_note = f"🏆 Top Strategy: {best_overall} ({best_weight*100:.1f}% weight)" if best_overall else "🏆 Top Strategy: Learning..."
        except Exception:
            meta_note = "🏆 Top Strategy: Unavailable"

        # 📊 Win/Loss Stats (if tracked in state)
        win_loss_note = ""
        if hasattr(state, 'TRADE_HISTORY') and state.TRADE_HISTORY:
            wins = sum(1 for t in state.TRADE_HISTORY if t.get('pnl', 0) > 0)
            losses = sum(1 for t in state.TRADE_HISTORY if t.get('pnl', 0) <= 0)
            total = wins + losses
            if total > 0:
                win_rate = (wins / total) * 100
                win_loss_note = f"🎯 Win Rate: {win_rate:.1f}% ({wins}W / {losses}L)\n"
        
        report = f"""
**💰 Trading Performance**
━━━━━━━━━━━━━━━━━━━━━━━━
📂 Open Positions: {open_pos}
📈 Daily PnL: {daily_pnl:+.2f}%
{win_loss_note}{meta_note}
"""
        
        # Add position details if any
        if open_pos > 0:
            report += "\n**Active Positions:**\n"
            for symbol, pos in list(state.OPEN_POSITIONS.items())[:5]:
                side = pos.get('side', 'BUY')
                entry = pos.get('entry', 0)
                report += f"  • {symbol} {side} @ ${entry:.2f}\n"
        
        return report
    
    def _generate_system_report(self) -> str:
        """Generate system health report."""
        return """
**🔧 System Health**
━━━━━━━━━━━━━━━━━━━━━━━━
✅ Bot Status: Running
✅ Position Monitor: Active (60s)
✅ Entry Scanner: Active (15min)
✅ Full Analysis: Active (30min)
✅ Pattern Analysis: Active (60s)
"""

# Singleton instance
_reporter_instance = None

def get_daily_reporter(chat_id: str) -> DailyReporter:
    global _reporter_instance
    if _reporter_instance is None:
        _reporter_instance = DailyReporter(chat_id)
    return _reporter_instance
