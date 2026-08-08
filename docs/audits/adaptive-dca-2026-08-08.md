# Adaptive DCA Security Audit — 2026-08-08

## Scope

Reviewed the adaptive DCA policy, DCA manager, fast supervisor, automatic runtime wiring, unit tests, and dedicated CI workflows on `institutional-upgrade`.

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
- The supervisor has a bounded 2–60 second scheduling range and defaults to 10 seconds.
- The supervisor skips grid positions and only evaluates enabled DCA metadata.
- Runtime wiring is applied by an exact-match, fail-closed script. It aborts if the expected source marker is missing or duplicated.
- The legacy five-minute `update_trailing_dca` task is removed from the main background task registry; the adaptive supervisor is registered instead.

## Verification

- Adaptive policy compiled successfully in GitHub Actions.
- DCA manager compiled successfully in GitHub Actions.
- Adaptive supervisor compiled successfully in GitHub Actions.
- Adaptive DCA unit suite passed.
- Manager bounds and progressive ladder sizing tests passed.
- Supervisor interval bounds test passed.
- Runtime wiring test passed against the actual `main.py`.
- Automatic wiring workflow passed syntax, whitespace, and runtime-registration verification before committing the wiring change.

Workflows: `Adaptive DCA CI` and `Adaptive DCA Wiring`.

## Live-money gate

The adaptive DCA path is **not yet approved for unrestricted live-money operation**. The code path is wired and statically/unit verified, but the following production verification remains mandatory:

1. Run the supervisor in dry-run mode against a live market-data feed with exchange writes disabled.
2. Exercise stale-order cancellation/reprice behavior using mocked executor responses.
3. Exercise AI-approved acceleration using mocked multi-provider output and MetaLearner weights.
4. Verify every acceleration risk gate blocks correctly under failure conditions.
5. Verify restart/reconciliation cannot duplicate resting orders.
6. Run the repository's broader CI suite.
7. Review live execution slippage and exchange acknowledgement behavior before enabling live acceleration.

No production capital should be enabled for unrestricted adaptive acceleration until these checks pass.
