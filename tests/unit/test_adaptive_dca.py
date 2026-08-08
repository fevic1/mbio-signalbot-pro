from core.adaptive_dca import (
    AdaptiveDCAConfig,
    DCAAction,
    MarketSnapshot,
    evaluate_dca_order,
    parse_ai_advice,
)


def test_ai_advice_is_bounded_and_unknown_action_fails_closed():
    advice = parse_ai_advice(
        {
            "action": "DO_SOMETHING",
            "confidence": 999,
            "learner_score": -5,
            "size_multiplier": 99,
            "valid_for_seconds": 9999,
        }
    )
    assert advice.action == "WAIT"
    assert advice.confidence == 1.0
    assert advice.learner_score == 0.0
    assert advice.size_multiplier == 10.0
    assert advice.valid_for_seconds == 300.0


def test_stale_long_order_is_repriced_toward_market():
    decision = evaluate_dca_order(
        side="LONG",
        market=MarketSnapshot(price=96.0, momentum=-0.3),
        order={"price": 94.0, "placed_at_ts": 0.0, "order_id": 1},
        now_ts=60.0,
        config=AdaptiveDCAConfig(order_ttl_seconds=45.0),
    )
    assert decision.action is DCAAction.REPRICE
    assert decision.target_price == 94.0


def test_ai_can_accelerate_only_when_all_gates_pass():
    decision = evaluate_dca_order(
        side="LONG",
        market=MarketSnapshot(
            price=96.0,
            momentum=-0.6,
            spread_pct=0.10,
            liquidity_score=0.95,
        ),
        order={"price": 94.0, "placed_at_ts": 55.0, "order_id": 1},
        now_ts=60.0,
        config=AdaptiveDCAConfig(),
        ai_advice={
            "action": "ACCELERATE",
            "confidence": 0.91,
            "learner_score": 0.82,
            "max_price": 96.0,
            "size_multiplier": 2.0,
            "valid_for_seconds": 30,
        },
    )
    assert decision.action is DCAAction.ACCELERATE
    assert decision.target_price == 96.0
    assert decision.size_multiplier == 1.25


def test_ai_acceleration_is_rejected_without_directional_momentum():
    decision = evaluate_dca_order(
        side="LONG",
        market=MarketSnapshot(
            price=96.0,
            momentum=0.2,
            spread_pct=0.10,
            liquidity_score=0.95,
        ),
        order={"price": 94.0, "placed_at_ts": 55.0, "order_id": 1},
        now_ts=60.0,
        config=AdaptiveDCAConfig(),
        ai_advice={
            "action": "ACCELERATE",
            "confidence": 0.95,
            "learner_score": 0.90,
            "max_price": 96.0,
        },
    )
    assert decision.action is DCAAction.WAIT


def test_risk_gate_always_wins():
    decision = evaluate_dca_order(
        side="LONG",
        market=MarketSnapshot(price=96.0, momentum=-0.7),
        order={"price": 94.0, "placed_at_ts": 0.0, "order_id": 1},
        now_ts=60.0,
        config=AdaptiveDCAConfig(),
        ai_advice={
            "action": "ACCELERATE",
            "confidence": 1.0,
            "learner_score": 1.0,
            "max_price": 96.0,
        },
        risk_allowed=False,
    )
    assert decision.action is DCAAction.PAUSE


def test_invalid_side_fails_closed():
    decision = evaluate_dca_order(
        side="SIDEWAYS",
        market=MarketSnapshot(price=100.0),
        order={"price": 99.0, "placed_at_ts": 0.0},
        now_ts=60.0,
    )
    assert decision.action is DCAAction.PAUSE
