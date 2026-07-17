#!/usr/bin/env python3
"""
MBIO SignalBot Backtesting Module
Validates trading strategies using historical data
"""

import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Backtester:
    def __init__(self, initial_balance=1000, risk_per_trade=0.02):
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.trades = []
        self.balance = initial_balance
        
    def fetch_historical_data(self, symbol, period="6mo", interval="1h"):
        """Fetch historical OHLCV data"""
        logging.info(f"📥 Fetching {symbol} data...")
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        df.columns = [col.lower() for col in df.columns]
        
        # Calculate indicators
        if len(df) >= 14:
            df.ta.rsi(length=14, append=True)
            df.ta.macd(append=True)
            df.ta.bbands(append=True)
            df.ta.atr(length=14, append=True)
        
        logging.info(f"✅ Loaded {len(df)} candles")
        return df
    
    def generate_signal(self, row):
        """Generate trading signal based on strategy"""
        rsi_1h = row.get('rsi_')
        macd = row.get('macd_')
        bb_lower = row.get('bbl_')
        bb_upper = row.get('bbu_')
        close = row['close']
        
        # Strategy: Buy when RSI < 35 and price near lower BB
        if rsi_1h and rsi_1h < 35 and bb_lower and close <= bb_lower * 1.02:
            return "BUY"
        
        # Strategy: Sell when RSI > 65 and price near upper BB
        elif rsi_1h and rsi_1h > 65 and bb_upper and close >= bb_upper * 0.98:
            return "SELL"
        
        return "HOLD"
    
    def calculate_position_size(self, entry, sl):
        """Calculate position size based on risk"""
        risk_amount = self.balance * self.risk_per_trade
        risk_per_unit = abs(entry - sl)
        
        if risk_per_unit == 0:
            return 0
        
        return risk_amount / risk_per_unit
    
    def run_backtest(self, symbol, start_date=None, end_date=None):
        """Run backtest on historical data"""
        logging.info(f"🚀 Starting backtest for {symbol}")
        
        df = self.fetch_historical_data(symbol)
        
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        position = None
        trades = []
        
        for idx, row in df.iterrows():
            signal = self.generate_signal(row)
            
            # Open position
            if signal in ["BUY", "SELL"] and position is None:
                entry = row['close']
                atr = row.get('atr_', entry * 0.02)
                
                if signal == "BUY":
                    sl = entry - (1.5 * atr)
                    tp1 = entry + (1.0 * atr)
                    tp2 = entry + (2.0 * atr)
                    tp3 = entry + (3.0 * atr)
                else:
                    sl = entry + (1.5 * atr)
                    tp1 = entry - (1.0 * atr)
                    tp2 = entry - (2.0 * atr)
                    tp3 = entry - (3.0 * atr)
                
                size = self.calculate_position_size(entry, sl)
                
                position = {
                    'entry_time': idx,
                    'entry': entry,
                    'size': size,
                    'side': signal,
                    'sl': sl,
                    'tp1': tp1,
                    'tp2': tp2,
                    'tp3': tp3
                }
                
                logging.info(f"📈 Opened {signal} @ {entry:.2f} | Size: {size:.4f}")
            
            # Check position
            elif position is not None:
                hit_tp = None
                hit_sl = False
                
                if position['side'] == 'BUY':
                    if row['low'] <= position['sl']:
                        hit_sl = True
                    elif row['high'] >= position['tp3']:
                        hit_tp = 'TP3'
                    elif row['high'] >= position['tp2']:
                        hit_tp = 'TP2'
                    elif row['high'] >= position['tp1']:
                        hit_tp = 'TP1'
                else:  # SELL
                    if row['high'] >= position['sl']:
                        hit_sl = True
                    elif row['low'] <= position['tp3']:
                        hit_tp = 'TP3'
                    elif row['low'] <= position['tp2']:
                        hit_tp = 'TP2'
                    elif row['low'] <= position['tp1']:
                        hit_tp = 'TP1'
                
                # Close position
                if hit_sl or hit_tp:
                    if position['side'] == 'BUY':
                        exit_price = position['sl'] if hit_sl else (
                            position['tp3'] if hit_tp == 'TP3' else
                            position['tp2'] if hit_tp == 'TP2' else
                            position['tp1']
                        )
                        pnl = (exit_price - position['entry']) * position['size']
                    else:
                        exit_price = position['sl'] if hit_sl else (
                            position['tp3'] if hit_tp == 'TP3' else
                            position['tp2'] if hit_tp == 'TP2' else
                            position['tp1']
                        )
                        pnl = (position['entry'] - exit_price) * position['size']
                    
                    pnl_percent = (pnl / self.balance) * 100
                    self.balance += pnl
                    
                    trade = {
                        'entry_time': position['entry_time'],
                        'exit_time': idx,
                        'side': position['side'],
                        'entry': position['entry'],
                        'exit': exit_price,
                        'size': position['size'],
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'result': hit_tp if hit_tp else 'SL'
                    }
                    trades.append(trade)
                    
                    status = "✅" if pnl > 0 else "❌"
                    logging.info(f"{status} Closed {position['side']} | PnL: ${pnl:+.2f} ({pnl_percent:+.2f}%) | {hit_tp if hit_tp else 'SL'}")
                    
                    position = None
        
        self.trades = trades
        return self.generate_report()
    
    def generate_report(self):
        """Generate backtest report"""
        if not self.trades:
            return {"error": "No trades executed"}
        
        total_trades = len(self.trades)
        wins = sum(1 for t in self.trades if t['pnl'] > 0)
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        total_pnl_percent = ((self.balance - self.initial_balance) / self.initial_balance) * 100
        
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        best_trade = max(t['pnl'] for t in self.trades)
        worst_trade = min(t['pnl'] for t in self.trades)
        
        # TP level breakdown
        tp1_hits = sum(1 for t in self.trades if t['result'] == 'TP1')
        tp2_hits = sum(1 for t in self.trades if t['result'] == 'TP2')
        tp3_hits = sum(1 for t in self.trades if t['result'] == 'TP3')
        sl_hits = sum(1 for t in self.trades if t['result'] == 'SL')
        
        report = {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_return': total_pnl_percent,
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'tp1_hits': tp1_hits,
            'tp2_hits': tp2_hits,
            'tp3_hits': tp3_hits,
            'sl_hits': sl_hits,
            'trades': self.trades
        }
        
        # Print report
        print("\n" + "="*60)
        print("📊 BACKTEST REPORT")
        print("="*60)
        print(f"Initial Balance: ${self.initial_balance:.2f}")
        print(f"Final Balance: ${self.balance:.2f}")
        print(f"Total Return: {total_pnl_percent:+.2f}%")
        print(f"\nTotal Trades: {total_trades}")
        print(f"Wins: {wins} | Losses: {losses}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"\nTotal PnL: ${total_pnl:+.2f}")
        print(f"Average PnL: ${avg_pnl:+.2f}")
        print(f"Best Trade: ${best_trade:+.2f}")
        print(f"Worst Trade: ${worst_trade:+.2f}")
        print(f"\nTP1 Hits: {tp1_hits}")
        print(f"TP2 Hits: {tp2_hits}")
        print(f"TP3 Hits: {tp3_hits}")
        print(f"SL Hits: {sl_hits}")
        print("="*60 + "\n")
        
        return report

if __name__ == "__main__":
    # Example usage
    backtester = Backtester(initial_balance=1000, risk_per_trade=0.02)
    
    # Backtest BTC
    report = backtester.run_backtest("BTC-USD")
    
    # You can also backtest other assets
    # backtester2 = Backtester(initial_balance=1000)
    # report2 = backtester2.run_backtest("ETH-USD")
