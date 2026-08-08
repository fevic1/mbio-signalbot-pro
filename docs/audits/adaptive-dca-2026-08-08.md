# Adaptive DCA Security Audit — 2026-08-08

## Scope

Reviewed the adaptive DCA policy, DCA manager integration, unit tests, and isolated CI workflow on `institutional-upgrade`.

## Controls verified

- LLM output is treated as untrusted advisory input.
- Unknown actions fail closed to `WAIT`.
- Confidence, learner score, validity, and size multiplier are bounded.
- Acceleration requires AI alignment, confidence threshold, MetaLearner score, directional momentum, liquidity, and price-bound checks.
- Acceleration is capped at a 1.25x size multiplier.
- Live DCA exposure is checked against `dca.max_total_dca_exposure_pct` and current account equity.
- Account-equity lookup failure blocks acceleration rather than permitting it.
- Resting DCA orders are cancelled before an accelerated leg is submitted to reduce double-fill risk.
- The accelerated leg uses the existing executor's marketable-limit path rather than an unbounded market-order path.
- Remaining unfilled levels are rebuilt from the new execution anchor after acceleration.
- State is persisted after adaptive actions.
- The existing large-drop DCA pause guardrail remains active.

## Verification

- Adaptive policy compiled successfully in GitHub Actions.
- DCA manager compiled successfully in GitHub Actions.
- Adaptive DCA unit suite passed in GitHub Actions.
- Manager bounds and progressive ladder sizing tests passed.

Workflow: `Adaptive DCA CI`

## Production wiring gate

The adaptive policy and manager are **not declared production-live solely by these commits**. The current `monitoring/position_tracker.py` contains a legacy `update_trailing_dca()` loop that sleeps for 300 seconds and references a `dca` object that is not defined in that function's module scope. The next integration change must replace that legacy path with a dedicated fast adaptive-DCA supervisor and then verify the complete runtime path before live deployment.

No production capital should be enabled for the adaptive path until that wiring test passes.

## Required next verification

1. Wire a dedicated adaptive-DCA supervisor into the application task registry.
2. Verify one supervisor tick per configured interval without exchange writes in dry-run mode.
3. Verify stale-order cancellation/reprice behavior with mocked executor responses.
4. Verify AI-approved acceleration with mocked multi-provider output and MetaLearner weights.
5. Verify acceleration is blocked when any risk gate fails.
6. Verify restart/reconciliation does not duplicate resting orders.
7. Run the full repository CI suite.
8. Only then enable the feature for live-money DCA.
