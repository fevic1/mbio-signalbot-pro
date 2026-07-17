# reporting.py
from datetime import datetime

class ReportGenerator:
    @staticmethod
    def format_summary(account_value, free, pos_count, trade_details, macro_bias, realized_pnl, daily_pnl):
        return (
            f"🚨 *Agent Performance Summary*\n"
            f"📅 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"*📈 Portfolio Overview*\n"
            f"💰 *Balance:* ${account_value:.2f}\n"
            f"💵 *Free Collateral:* ${free:.2f}\n"
            f"📦 *Open Positions:* {pos_count}\n\n"
            f"*🎯 Recent Trades*\n{trade_details}\n"
            f"*🧠 AI Status:* {macro_bias}\n"
            f"*💹 Realised PnL:* ${realized_pnl:+.2f}\n"
            f"*📊 Running Daily PnL:* ${daily_pnl:+.2f}\n"
        )

    @staticmethod
    def format_order(coin, side, order_type, size, price, daily_total):
        icon = "🟢" if side == "BUY" else "🔴"
        return (
            f"{icon} *ORDER FILLED*\n"
            f"• *Pair:* {coin}\n"
            f"• *Action:* {side} | {order_type}\n"
            f"• *Size:* {size}\n"
            f"• *Price:* ${price:.4f}\n"
            f"• *Running Daily Total:* ${daily_total:+.2f}\n"
        )
