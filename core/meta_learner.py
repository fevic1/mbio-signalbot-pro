# core/meta_learner.py
import json
import logging
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

# Default weight initialization for each regime (from backtest priors)
DEFAULT_WEIGHTS = {
    "TRENDING_UP": {
        "Momentum": 0.40,
        "MeanReversion": 0.10,
        "Breakout": 0.20,
        "Carry": 0.10,
        "LLM": 0.15,
        "SimpleRSI": 0.05,
    },
    "TRENDING_DOWN": {
        "Momentum": 0.35,      # short momentum
        "MeanReversion": 0.15,
        "Breakout": 0.20,
        "Carry": 0.10,
        "LLM": 0.15,
        "SimpleRSI": 0.05,
    },
    "RANGING": {
        "Momentum": 0.10,
        "MeanReversion": 0.40,
        "Breakout": 0.10,
        "Carry": 0.20,
        "LLM": 0.10,
        "SimpleRSI": 0.20,
    },
    "VOLATILE": {
        "Momentum": 0.20,
        "MeanReversion": 0.20,
        "Breakout": 0.40,
        "Carry": 0.10,
        "LLM": 0.05,
        "SimpleRSI": 0.05,
    },
}

# ChromaDB collection name
META_COLLECTION = "meta_learner_weights"

class MetaLearner:
    """Bayesian weight updater with ChromaDB persistence per regime."""

    def __init__(self, persist_dir: str = "/app/data/chroma_db"):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=persist_dir, settings=Settings(anonymized_telemetry=False))
        self.collection = self._get_or_create_collection()
        self.weights = self._load_weights()   # regime -> {strategy: weight}

    def _get_or_create_collection(self):
        try:
            return self.client.get_or_create_collection(META_COLLECTION)
        except ValueError:
            return self.client.create_collection(
                name=META_COLLECTION,
                embedding_function=embedding_functions.DefaultEmbeddingFunction()
            )

    def _load_weights(self) -> Dict[str, Dict[str, float]]:
        """Load weights from ChromaDB; if missing, use DEFAULT_WEIGHTS."""
        try:
            results = self.collection.get()
            if results and results['metadatas']:
                weights = {}
                for meta in results['metadatas']:
                    regime = meta.get('regime')
                    w_str = meta.get('weights')
                    if regime and w_str:
                        weights[regime] = json.loads(w_str)
                # ensure all regimes exist
                for regime in DEFAULT_WEIGHTS:
                    if regime not in weights:
                        weights[regime] = DEFAULT_WEIGHTS[regime].copy()
                logger.info("Loaded meta-learner weights from ChromaDB")
                return weights
        except Exception as e:
            logger.warning(f"Could not load weights from ChromaDB: {e}")
        # fallback to defaults
        return {regime: DEFAULT_WEIGHTS[regime].copy() for regime in DEFAULT_WEIGHTS}

    def _persist_weights(self):
        """Store current weights into ChromaDB."""
        # Clear existing entries for these regimes
        existing = self.collection.get()
        if existing and existing['ids']:
            self.collection.delete(ids=existing['ids'])

        ids = []
        metadatas = []
        documents = []
        for regime, w_dict in self.weights.items():
            ids.append(regime)
            metadatas.append({
                "regime": regime,
                "weights": json.dumps(w_dict),
                "updated_at": datetime.now().isoformat()
            })
            documents.append(json.dumps(w_dict))
        if ids:
            self.collection.add(ids=ids, metadatas=metadatas, documents=documents)
            logger.debug("Persisted meta-learner weights")

    def get_weights(self, regime: str) -> Dict[str, float]:
        """Return weight dictionary for a given regime (copy)."""
        return self.weights.get(regime, DEFAULT_WEIGHTS.get(regime, {})).copy()

    def update(self, regime: str, strategy_name: str, pnl_pct: float, learning_rate: float = 0.05):
        """
        Bayesian-inspired weight update.
        pnl_pct is the profit/loss percentage of the trade (e.g., +2.5 for 2.5% gain).
        Positive pnl increases weight, negative decreases, proportional to magnitude.
        Weights are then normalized per regime.
        """
        if regime not in self.weights:
            self.weights[regime] = DEFAULT_WEIGHTS.get(regime, {}).copy()
        if strategy_name not in self.weights[regime]:
            # assign a small default if strategy unknown
            self.weights[regime][strategy_name] = 0.1

        # Update: new_weight = old_weight * (1 + learning_rate * pnl_pct/100)
        # This is multiplicative, so good trades increase weight multiplicatively.
        factor = 1 + learning_rate * (pnl_pct / 100.0)
        # clamp factor to reasonable range [0.8, 1.2] to avoid extreme shifts
        factor = max(0.8, min(1.2, factor))
        new_weight = self.weights[regime][strategy_name] * factor
        self.weights[regime][strategy_name] = max(0.01, new_weight)   # never zero

        # Normalize weights for this regime
        self._normalize(regime)
        self._persist_weights()
        logger.info(f"Updated weight for {strategy_name} in {regime}: {self.weights[regime][strategy_name]:.3f}")

    def _normalize(self, regime: str):
        """Ensure weights sum to 1.0 for the regime."""
        total = sum(self.weights[regime].values())
        if total > 0:
            for s in self.weights[regime]:
                self.weights[regime][s] /= total

    def choose_strategy(self, regime: str, strategies: List[str]) -> str:
        """Randomly select a strategy according to current weights (for exploration)."""
        weights = self.get_weights(regime)
        # filter only strategies that exist in weights and are in the provided list
        valid = [(s, weights.get(s, 0.0)) for s in strategies if s in weights]
        if not valid:
            return strategies[0] if strategies else "LLM"
        names, probs = zip(*valid)
        # add a small epsilon to avoid zero probability
        probs = np.array(probs) + 1e-6
        probs = probs / probs.sum()
        chosen = np.random.choice(names, p=probs)
        logger.debug(f"Weight-based strategy selection in {regime}: {chosen}")
        return chosen

    def get_best_strategy(self, regime: str) -> str:
        """Return the strategy with highest weight (exploitation)."""
        weights = self.get_weights(regime)
        if not weights:
            return "LLM"
        best = max(weights, key=weights.get)
        logger.debug(f"Best strategy in {regime}: {best} ({weights[best]:.3f})")
        return best


    def record_trade_outcome(self, strategy_name: str, regime: str, pnl_pct: float):
        """Update strategy weights based on trade outcome (PnL %)."""
        if regime not in self.weights or strategy_name not in self.weights[regime]:
            return
        
        learning_rate = 0.05
        if pnl_pct > 0:
            # Winning trade: increase weight
            self.weights[regime][strategy_name] += learning_rate
        else:
            # Losing trade: decrease weight
            self.weights[regime][strategy_name] = max(0.01, self.weights[regime][strategy_name] - learning_rate)
            
        # Normalize weights so they sum to 1.0
        total = sum(self.weights[regime].values())
        if total > 0:
            for k in self.weights[regime]:
                self.weights[regime][k] /= total
                
        self._persist_weights()
        logger.info(f"🧠 MetaLearner updated {strategy_name} in {regime} to {self.weights[regime][strategy_name]:.3f} (PnL: {pnl_pct:+.2f}%)")

    def reset_regime_to_default(self, regime: str):
        """Reset weights for a specific regime to DEFAULT_WEIGHTS."""
        self.weights[regime] = DEFAULT_WEIGHTS.get(regime, {}).copy()
        self._persist_weights()
        logger.info(f"Reset weights for {regime} to default")

# Singleton instance (optional)
_meta_learner_instance = None

def get_meta_learner() -> MetaLearner:
    global _meta_learner_instance
    if _meta_learner_instance is None:
        _meta_learner_instance = MetaLearner()
    return _meta_learner_instance
