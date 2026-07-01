"""
core/grid_persistence.py — Persistent Grid State Storage
Serializes/deserializes GRID:: configs to data/grid_state.json.
Survives container restarts via Docker volume mount.
"""
import json
import os
import logging
from typing import Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

GRID_STATE_PATH = "data/grid_state.json"


def save_grid_state(open_positions: Dict) -> None:
    """Save all GRID:: namespaced configs to persistent storage."""
    try:
        grid_configs = {
            k: v for k, v in open_positions.items()
            if k.startswith("GRID::")
        }
        if not grid_configs:
            return

        os.makedirs(os.path.dirname(GRID_STATE_PATH), exist_ok=True)

        # Load existing file to preserve non-grid data if any
        existing = {}
        if os.path.exists(GRID_STATE_PATH):
            try:
                with open(GRID_STATE_PATH, "r") as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        existing["grids"] = grid_configs
        existing["last_saved"] = datetime.now(timezone.utc).isoformat()

        with open(GRID_STATE_PATH, "w") as f:
            json.dump(existing, f, indent=2, default=str)

        count = len(grid_configs)
        logger.info(f"💾 Grid state persisted: {count} grid(s) to {GRID_STATE_PATH}")
    except Exception as e:
        logger.error(f"❌ Failed to save grid state: {e}")


def load_grid_state() -> Dict:
    """Load GRID:: configs from persistent storage."""
    if not os.path.exists(GRID_STATE_PATH):
        logger.info("ℹ️ No saved grid state found")
        return {}

    try:
        with open(GRID_STATE_PATH, "r") as f:
            data = json.load(f)

        grids = data.get("grids", {})
        last_saved = data.get("last_saved", "unknown")
        count = len(grids)

        if count > 0:
            logger.info(f"📂 Grid state loaded: {count} grid(s) (saved: {last_saved})")
        else:
            logger.info("ℹ️ Grid state file exists but contains no grids")

        return grids
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"⚠️ Failed to load grid state: {e}")
        return {}


def clear_grid_state(asset: str = None) -> None:
    """Remove grid state for specific asset or all assets."""
    try:
        if not os.path.exists(GRID_STATE_PATH):
            return

        with open(GRID_STATE_PATH, "r") as f:
            data = json.load(f)

        grids = data.get("grids", {})

        if asset:
            key = f"GRID::{asset.upper()}"
            if key in grids:
                del grids[key]
                logger.info(f"🗑️ Cleared grid state for {asset}")
        else:
            grids = {}
            logger.info("🗑️ Cleared all grid state")

        data["grids"] = grids
        data["last_saved"] = datetime.now(timezone.utc).isoformat()

        with open(GRID_STATE_PATH, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"❌ Failed to clear grid state: {e}")
