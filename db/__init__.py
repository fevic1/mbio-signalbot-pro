# Database package initialization
# Re-export commonly used functions for backward compatibility

try:
    from db.dashboard_models import init_db, save_signal
except ImportError:
    # Fallback if functions don't exist in dashboard_models
    def init_db():
        pass
    
    def save_signal(*args, **kwargs):
        pass

# Also export get_dashboard_db for audit log functionality
try:
    from db.dashboard_models import get_dashboard_db
except ImportError:
    pass
