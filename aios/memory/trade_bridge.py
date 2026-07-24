from .event_store import EventStore
from .events import MemoryEvent


def record_trade_outcome(record: dict):

    event = MemoryEvent(
        event_type="trade_outcome",
        action=record.get("event_type", "trade_recorded"),
        source="trade_ledger",
        metadata=record,
    )

    EventStore().append(event)

    return event
