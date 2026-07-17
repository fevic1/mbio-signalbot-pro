import chromadb
from chromadb.config import Settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TradeMemory:
    def __init__(self, persist_dir: str = "/app/data/chroma_db"):
        """Initialize ChromaDB and create the trade_history collection."""
        self.client = chromadb.PersistentClient(path=persist_dir, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(
            name="trade_history",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"🧠 TradeMemory initialized. Historical trades stored: {self.collection.count()}")

    def store_trade(self, trade_id: str, asset: str, side: str, pnl: float,
                    regime: str, strategy: str, entry_price: float, exit_price: float,
                    metadata_extra: dict = None):
        """Store a completed or active trade into ChromaDB."""
        doc = f"Trade {trade_id} for {asset} {side} using {strategy} in {regime} regime."
        
        metadata = {
            "asset": asset,
            "side": side,
            "pnl_pct": float(pnl),
            "regime": regime,
            "strategy": strategy,
            "entry_price": float(entry_price),
            "exit_price": float(exit_price),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata_extra:
            metadata.update(metadata_extra)

        self.collection.upsert(
            ids=[trade_id],
            documents=[doc],
            metadatas=[metadata]
        )
        logger.info(f"💾 Stored trade {trade_id} ({asset} {side}) in ChromaDB memory.")

    def get_recent_trades(self, asset: str = None, limit: int = 20):
        """Retrieve recent trade history for analysis."""
        try:
            if asset:
                results = self.collection.get(where={"asset": asset}, limit=limit, include=["metadatas"])
            else:
                results = self.collection.get(limit=limit, include=["metadatas"])
            return results.get('metadatas', [])
        except Exception as e:
            logger.error(f"Failed to query trade memory: {e}")
            return []
