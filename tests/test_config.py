"""Test configuration and utilities."""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test environment variables
os.environ['TESTING'] = 'true'
os.environ['DRY_RUN'] = 'true'  # Don't execute real trades

# Feature flags for safe rollout
FEATURE_FLAGS = {
    'dynamic_position_sizing': False,
    'llm_trade_reasoning': False,
    'realtime_dashboard': False,
    'smart_exit_strategies': False,
    'sentiment_analysis': False,
}

def enable_feature(feature_name: str):
    """Safely enable a feature."""
    if feature_name in FEATURE_FLAGS:
        FEATURE_FLAGS[feature_name] = True
        print(f"✅ Feature enabled: {feature_name}")
    else:
        print(f"❌ Unknown feature: {feature_name}")

def is_feature_enabled(feature_name: str) -> bool:
    """Check if feature is enabled."""
    return FEATURE_FLAGS.get(feature_name, False)
