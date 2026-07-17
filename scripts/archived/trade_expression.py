import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

# ... rest of the code (exactly as in the previous full version)
# Optional: PNG generation with Pillow
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class TradeExpressionEngine:
    """
    Generates visual trade closure cards (terminal + optional PNG) for Hyperliquid agents.
    """

    def __init__(self, agent_name: str = "AGENT 1💋"):
        self.agent_name = agent_name

    def print_terminal_card(self, trade_data: Dict[str, Any]):
        """
        Prints a coloured, high‑visibility execution card to the terminal.
        """
        pair = trade_data.get("pair", "HYPE")
        direction = trade_data.get("direction", "LONG")
        leverage = trade_data.get("leverage", 3)
        pnl_pct = trade_data.get("pnl_pct", 0.0)
        net_profit_usd = trade_data.get("net_profit_usd", 0.0)
        entry_price = trade_data.get("entry_price", 0.0)
        exit_price = trade_data.get("exit_price", 0.0)
        fees_paid = trade_data.get("fees_paid", 0.0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Choose colour based on profit/loss
        if net_profit_usd >= 0:
            profit_colour = "\033[92m"   # green
            sign = "+"
        else:
            profit_colour = "\033[91m"   # red
            sign = ""

        reset = "\033[0m"

        print("\n" + "=" * 70)
        print(f"⚡ AI-AUGMENTED AGENT – {self.agent_name} Edition (Trade Closed)")
        print("=" * 70)
        print(f" 📡 Asset       :  {pair} ({direction} {leverage}X)")
        print(f" ⏱️ Closed at   :  {timestamp}")
        print("-" * 70)
        print(f" 📊 Gross PnL   :  {profit_colour}{sign}{pnl_pct:.2f}%{reset}")
        print(f" ⛽ Total Fees  :  -${fees_paid:.4f} USD")
        print(f" 💰 Net Profit  :  {profit_colour}${net_profit_usd:+.4f} USD{reset}")
        print("-" * 70)
        print(f" 📉 Entry → Exit:  ${entry_price:,.2f}  →  ${exit_price:,.2f}")
        print("=" * 70 + "\n")

    def generate_image_card(self, trade_data: Dict[str, Any],
                            output_filename: str = "pnl_card.png") -> Optional[str]:
        """
        Generates a PNG image card (Hyperliquid dark theme) if Pillow is available.
        Returns the filename or None if Pillow missing.
        """
        if not PILLOW_AVAILABLE:
            print("⚠️ Pillow not installed – image card skipped. Run 'pip install Pillow' to enable PNG cards.")
            return None

        # Dimensions & colours (Hyperliquid dark palette)
        width, height = 800, 560
        bg_color = (4, 18, 16)          # deep dark green/black
        image = Image.new("RGBA", (width, height), bg_color)
        draw = ImageDraw.Draw(image)

        # --- Background radar circles (subtle) ---
        center = (600, 280)
        for radius in range(50, 600, 30):
            draw.ellipse(
                [center[0] - radius, center[1] - radius,
                 center[0] + radius, center[1] + radius],
                outline=(10, 35, 30, 100), width=1
            )

        # --- Font handling (fallback if no system font) ---
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except (IOError, OSError):
            # Fallback to default PIL font
            font_title = ImageFont.load_default()
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Data extraction
        pair = trade_data.get("pair", "HYPE")
        direction = trade_data.get("direction", "LONG")
        leverage = trade_data.get("leverage", 3)
        pnl_pct = trade_data.get("pnl_pct", 0.0)
        net_profit_usd = trade_data.get("net_profit_usd", 0.0)
        entry_price = trade_data.get("entry_price", 0.0)
        exit_price = trade_data.get("exit_price", 0.0)

        # Colour logic
        is_profit = net_profit_usd >= 0
        pnl_colour = (34, 197, 94) if is_profit else (239, 68, 68)   # green / red
        sign = "+" if is_profit else ""

        # --- Render elements ---
        # Header
        draw.text((50, 50), "Hyperliquid", fill=(255, 255, 255), font=font_title)
        draw.text((50, 150), pair, fill=(255, 255, 255), font=font_medium)

        # Leverage badge background
        draw.rectangle([140, 148, 320, 188], fill=(16, 45, 40))
        draw.text((150, 153), f"{direction} {leverage}X", fill=(52, 211, 153), font=font_small)

        # PnL percentage (large)
        draw.text((50, 220), f"{sign}{pnl_pct:.1f}%", fill=pnl_colour, font=font_large)

        # Stats footer
        draw.text((50, 400), "Entry Price", fill=(156, 163, 175), font=font_small)
        draw.text((50, 430), f"{entry_price:,.2f}", fill=(255, 255, 255), font=font_medium)

        draw.text((250, 400), "Exit Price", fill=(156, 163, 175), font=font_small)
        draw.text((250, 430), f"{exit_price:,.2f}", fill=(255, 255, 255), font=font_medium)

        draw.text((450, 400), "Net Profit (After Fees)", fill=(156, 163, 175), font=font_small)
        draw.text((450, 430), f"${net_profit_usd:.2f}", fill=pnl_colour, font=font_medium)

        # Save image
        image.save(output_filename)
        print(f"🎨 PNG card saved: {output_filename}")
        return output_filename


# =============================================================================
# INTEGRATION EXAMPLE – call this when a position is closed in your agent
# =============================================================================
if __name__ == "__main__":
    # Create the engine
    engine = TradeExpressionEngine(agent_name="BTC MAKER")

    # Example: WIN trade
    win_trade = {
        "pair": "BTC",
        "direction": "LONG",
        "leverage": 20,
        "entry_price": 64564,
        "exit_price": 64693,
        "pnl_pct": 3.7,
        "fees_paid": 0.1450,
        "net_profit_usd": 15.42
    }
    engine.print_terminal_card(win_trade)
    engine.generate_image_card(win_trade, "btc_win.png")

    # Example: LOSS trade
    loss_trade = {
        "pair": "HYPE",
        "direction": "SHORT",
        "leverage": 3,
        "entry_price": 67.50,
        "exit_price": 68.20,
        "pnl_pct": -1.04,
        "fees_paid": 0.082,
        "net_profit_usd": -4.32
    }
    engine.print_terminal_card(loss_trade)
    engine.generate_image_card(loss_trade, "hype_loss.png")
