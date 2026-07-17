#!/usr/bin/env python3
"""
check_features.py — Scan MBIO bot codebase for connected, disconnected, and silenced features.
"""

import os
import re
import sys
import yaml
from pathlib import Path
from collections import defaultdict

# ---------- Configuration ----------
PROJECT_ROOT = Path(__file__).parent.absolute()
CONFIG_FILE = PROJECT_ROOT / "config" / "strategy_config.yaml"
ENV_FILE = PROJECT_ROOT / ".env"

# Features to track: (module_path, import_name, instantiation_pattern, config_key, env_var)
FEATURES = [
    {
        "name": "RiskGuard (hard veto)",
        "import": "from core.risk_guard import RiskGuard",
        "instantiation": r"RiskGuard\s*\(",
        "config": "risk_guard",
        "env": None,
    },
    {
        "name": "ExecutionManager (separation)",
        "import": "from core.execution_manager import ExecutionManager",
        "instantiation": r"ExecutionManager\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "TradeSignal (standardized signal)",
        "import": "from core.trade_signal import TradeSignal",
        "instantiation": r"TradeSignal\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "MetaLearner (self‑learning weights)",
        "import": "from core.meta_learner import MetaLearner",
        "instantiation": r"get_meta_learner\s*\(|MetaLearner\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "StrategyManager (multi‑strategy ensemble)",
        "import": "from core.strategy_manager import StrategyManager",
        "instantiation": r"StrategyManager\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "LLM Strategy (Groq)",
        "import": "from strategies.llm import LLMStrategy",
        "instantiation": r"LLMStrategy\s*\(",
        "config": None,
        "env": "GROQ_API_KEY",
    },
    {
        "name": "SimpleRSI Strategy",
        "import": "from strategies.simple_rsi import SimpleRSIStrategy",
        "instantiation": r"SimpleRSIStrategy\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "Momentum Strategy",
        "import": "from strategies.momentum import MomentumStrategy",
        "instantiation": r"MomentumStrategy\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "MeanReversion Strategy",
        "import": "from strategies.meanreversion import MeanReversionStrategy",
        "instantiation": r"MeanReversionStrategy\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "Breakout Strategy",
        "import": "from strategies.breakout import BreakoutStrategy",
        "instantiation": r"BreakoutStrategy\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "Carry Strategy",
        "import": "from strategies.carry import CarryStrategy",
        "instantiation": r"CarryStrategy\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "Idle Monitor (dynamic confidence)",
        "import": None,
        "instantiation": None,
        "config": "idle_monitor",
        "env": None,
    },
    {
        "name": "Early Exit (auto‑close losers)",
        "import": None,
        "instantiation": None,
        "config": "early_exit",
        "env": None,
    },
    {
        "name": "Smart Entry (scale‑in)",
        "import": None,
        "instantiation": None,
        "config": "smart_entry",
        "env": None,
    },
    {
        "name": "Sentiment Filter",
        "import": "from core.sentiment_analysis import SentimentAnalyzer",
        "instantiation": r"SentimentAnalyzer\s*\(",
        "config": "sentiment",
        "env": None,
    },
    {
        "name": "Dynamic Position Sizing",
        "import": "from core.sizing_wrapper import calculate_safe_position_size",
        "instantiation": r"calculate_safe_position_size\s*\(",
        "config": None,
        "env": None,
    },
    {
        "name": "Telegram Commands",
        "import": "from monitoring.alert_manager import cmd_positions, cmd_close, cmd_closeall",
        "instantiation": None,
        "config": None,
        "env": "TELEGRAM_BOT_TOKEN",
    },
    {
        "name": "ChromaDB Memory",
        "import": "from core.memory import collection",
        "instantiation": None,
        "config": None,
        "env": None,
    },
    {
        "name": "Position Monitor",
        "import": "from monitoring.position_tracker import position_monitor_loop",
        "instantiation": None,
        "config": None,
        "env": None,
    },
    {
        "name": "Entry Scanner",
        "import": "from monitoring.position_tracker import entry_scanner_loop",
        "instantiation": None,
        "config": None,
        "env": None,
    },
    {
        "name": "Full Analysis",
        "import": "from monitoring.position_tracker import full_analysis_loop",
        "instantiation": None,
        "config": None,
        "env": None,
    },
]


def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def get_py_files():
    py_files = []
    for root, _, files in os.walk(PROJECT_ROOT):
        for f in files:
            if f.endswith('.py') and not f.startswith('__') and 'venv' not in root and '.git' not in root:
                py_files.append(os.path.join(root, f))
    return py_files


def get_config_value(config, key):
    if not config or not key:
        return None
    parts = key.split('.')
    val = config
    for part in parts:
        if isinstance(val, dict):
            val = val.get(part)
        else:
            return None
    return val


def check_feature(feature, py_files, config, env):
    name = feature['name']
    import_line = feature.get('import')
    instantiation = feature.get('instantiation')
    config_key = feature.get('config')
    env_key = feature.get('env')

    # Check import
    import_found = False
    if import_line:
        for pyf in py_files:
            content = read_file(pyf)
            if import_line in content:
                import_found = True
                break

    # Check instantiation
    instantiation_found = False
    if instantiation:
        for pyf in py_files:
            content = read_file(pyf)
            if re.search(instantiation, content):
                instantiation_found = True
                break

    # Check config
    config_enabled = None
    if config_key:
        val = get_config_value(config, config_key)
        if isinstance(val, dict):
            config_enabled = val.get('enabled', True)
        else:
            config_enabled = bool(val) if val is not None else False

    # Check env
    env_present = False
    if env_key:
        env_present = bool(os.getenv(env_key))

    # Determine status
    if import_found or instantiation_found or config_enabled or env_present:
        status = "ACTIVE"
        # If it's a config feature and config says disabled, mark as DISABLED
        if config_key and config_enabled is False:
            status = "DISABLED (config)"
        # If it's an env feature and env is missing and not imported, mark as MISSING ENV
        if env_key and not env_present and not import_found:
            status = "MISSING ENV"
        if import_found and not instantiation_found and not config_enabled:
            status = "IMPORTED BUT NOT USED"
        if instantiation_found and not import_found:
            status = "INSTANTIATED WITHOUT IMPORT (unlikely)"
        # If nothing found, mark as INACTIVE
    else:
        status = "INACTIVE"

    return {
        "name": name,
        "import_found": import_found,
        "instantiation_found": instantiation_found,
        "config_enabled": config_enabled,
        "env_present": env_present,
        "status": status,
    }


def main():
    print("🔍 Scanning MBIO bot features...\n")
    py_files = get_py_files()
    config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️ Could not parse config: {e}")

    # Load .env
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    os.environ[k] = v

    results = []
    for feature in FEATURES:
        results.append(check_feature(feature, py_files, config, os.environ))

    # Print report
    print("=" * 80)
    print("FEATURE STATUS REPORT")
    print("=" * 80)
    for r in results:
        status = r['status']
        color = ""
        reset = ""
        if status == "ACTIVE":
            color = "\033[92m"  # green
        elif status.startswith("DISABLED") or status.startswith("MISSING"):
            color = "\033[93m"  # yellow
        elif status == "INACTIVE":
            color = "\033[91m"  # red
        else:
            color = "\033[96m"  # cyan
        reset = "\033[0m"
        print(f"{color}{r['name']:<30} {status}{reset}")

    print("\n" + "=" * 80)
    print("DETAILS")
    print("=" * 80)
    for r in results:
        if r['status'] != "ACTIVE":
            print(f"\n{r['name']}:")
            if not r['import_found'] and not r['instantiation_found'] and not r['config_enabled'] and not r['env_present']:
                print("  - No import, instantiation, config, or env found.")
            else:
                if r['import_found']:
                    print("  - Import found")
                if r['instantiation_found']:
                    print("  - Instantiation found")
                if r['config_enabled'] is not None:
                    print(f"  - Config: {r['config_enabled']}")
                if r['env_present']:
                    print("  - Environment variable present")

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
