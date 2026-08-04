# AIOS Coding Standards

Adopted as a **binding module standard**. For AIOS, the compiler must remain an **optional optimization layer** over the execution kernel, never a hard dependency. The rules below are written so they can be enforced in code review, CI, and architecture tests.

---

## 1. Normative module contract

Every module must satisfy all of the following.

### 1.1 SOLID

#### Single Responsibility Principle

Each module must have exactly one reason to change.

Examples:

```text
aios.domain.plan        -> plan value objects only
aios.kernel.executor    -> canonical execution semantics only
aios.compiler.passes    -> plan-to-plan transformations only
aios.application.pipeline -> orchestration only
aios.adapters.broker    -> external broker/exchange I/O only
aios.composition.root   -> wiring only
```

A module must not mix domain rules, I/O, configuration loading, logging policy, and orchestration.

---

#### Open/Closed Principle

New behavior must be introduced by adding new implementations or passes, not by modifying stable kernel semantics.

Preferred extension points:

```python
class PlanOptimizer(Protocol): ...
class PlanValidator(Protocol): ...
class ExecutionKernel(Protocol): ...
```

New compiler passes implement `PlanOptimizer`. They must not modify the kernel.

---

#### Liskov Substitution Principle

Any implementation of a typed interface must be substitutable for any other implementation without changing caller behavior.

Rules:

- Do not narrow preconditions silently.
- Do not widen postconditions silently.
- Do not raise unexpected exception types from protocol methods.
- Do not require callers to know the concrete implementation.
- Do not use `NotImplementedError` in production execution paths.

---

#### Interface Segregation Principle

Prefer many small protocols over one large service interface.

Good:

```python
class ExecutionKernel(Protocol): ...
class PlanOptimizer(Protocol): ...
class PlanValidator(Protocol): ...
```

Bad:

```python
class TradingPlatform(Protocol):
    async def submit_order(...) -> ...
    def compile_plan(...) -> ...
    def load_config(...) -> ...
    def log_event(...) -> ...
    def connect_exchange(...) -> ...
```

---

#### Dependency Inversion Principle

High-level modules must depend on typed interfaces, not concrete adapters.

Allowed dependency direction:

```text
composition -> adapters -> application -> domain
                      -> compiler    -> domain
                      -> kernel      -> domain
```

The kernel must not import the compiler.

The compiler must not import the kernel.

The domain must not import application, kernel, compiler, adapters, or composition.

---

## 2. Typing rules

Use strict static typing.

### 2.1 Typed interfaces

Use `typing.Protocol` for interfaces.

Do not rely on runtime type inspection.

Good:

```python
from typing import Protocol

class PlanOptimizer(Protocol):
    def optimize(self, plan: ExecutionPlan) -> ExecutionPlan: ...
```

Avoid:

```python
isinstance(obj, SomeRuntimeCheckableProtocol)
getattr(obj, "optimize")
hasattr(obj, "optimize")
```

---

### 2.2 No implicit `Any`

Forbidden except with explicit review justification:

```python
def f(x: Any) -> Any: ...
```

Prefer:

```python
def f(x: object) -> object: ...
```

or a precise type.

---

### 2.3 Precise domain types

Use precise scalar types.

For trading and financial values:

```python
from decimal import Decimal
```

Do not use `float` for price, quantity, margin, profit, swap, commission, or volume.

Good:

```python
quantity: Decimal
price: Decimal
margin_usd: Decimal
profit_usd: Decimal
```

Bad:

```python
quantity: float
price: float
```

---

### 2.4 Explicit collections

Use immutable or explicitly owned collections.

Good:

```python
intents: tuple[OrderIntent, ...]
diagnostics: tuple[Diagnostic, ...]
```

Avoid shared mutable structures in public APIs:

```python
intents: list[OrderIntent]
metadata: dict[str, object]
```

If lookup is needed, build a local dictionary inside a function and do not expose it.

---

## 3. Dataclass rules

Use:

```python
@dataclass(frozen=True, slots=True)
```

for value objects, commands, events, configuration snapshots, results, diagnostics, and plan representations.

Example:

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class OrderIntent:
    client_order_id: str
    symbol: str
    quantity: Decimal
```

### 3.1 Use frozen dataclasses for value semantics

Frozen dataclasses must be treated as immutable.

Do not mutate them.

Do not expose mutable fields.

Use `with_*` methods for derived values.

Good:

```python
from dataclasses import replace

def with_quantity(self, quantity: Decimal) -> OrderIntent:
    return replace(self, quantity=quantity)
```

Bad:

```python
self.quantity = quantity
```

---

### 3.2 Do not use dataclasses for services

Services, repositories, adapters, compilers, and kernels should be `final` classes with explicit constructor dependencies.

Good:

```python
from typing import final

@final
class ExecutionPipeline:
    def __init__(self, kernel: ExecutionKernel) -> None:
        self._kernel = kernel
```

Bad:

```python
@dataclass
class ExecutionPipeline:
    kernel: ExecutionKernel
```

unless the class is purely a passive value container, which an execution pipeline is not.

---

## 4. Immutability and state rules

### 4.1 No global mutable state

Forbidden:

```python
_cache: dict[str, object] = {}
_current_bot: Bot | None = None
active_orders: list[Order] = []
```

Allowed:

```python
from typing import Final

MAX_ORDER_INTENTS: Final[int] = 10_000
```

Constants must be truly immutable.

If state is required, it must be owned by an explicitly constructed object and injected where needed.

---

### 4.2 No singletons

Do not introduce module-level singleton instances.

Bad:

```python
engine = Engine()
```

Good:

```python
def create_engine(config: EngineConfig) -> Engine:
    return Engine(config=config)
```

The composition root may instantiate one object graph, but the module itself must not hide that graph behind a global accessor.

---

### 4.3 No hidden caches

Do not use hidden global caches such as:

```python
@lru_cache
def get_thing(key: str) -> Thing: ...
```

unless explicitly approved and isolated behind a typed cache interface.

Prefer explicit memoization services if caching is needed.

---

## 5. Async-safety rules

### 5.1 Async boundaries are explicit

Only adapter and application orchestration layers may be async.

Domain logic should be synchronous and pure.

Good separation:

```text
domain      -> pure sync functions
compiler    -> pure sync transformations
kernel      -> async execution only where external submission is required
adapters    -> async I/O wrappers
```

---

### 5.2 No blocking calls inside async code

Forbidden inside async functions:

```python
time.sleep(...)
requests.get(...)
open(...).read()
socket.recv(...)
subprocess.run(...)
```

Use explicit async adapters or thread offloading inside an adapter boundary only.

---

### 5.3 No implicit event loops

Do not call:

```python
asyncio.get_event_loop()
asyncio.new_event_loop()
loop.run_until_complete(...)
```

inside library modules.

Only the composition root may start the runtime:

```python
asyncio.run(main())
```

---

### 5.4 Shared mutable async state must be guarded

If a service must own mutable state, it must use explicit async synchronization.

Example:

```python
import asyncio

@final
class OrderStateStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._orders: dict[str, OrderState] = {}

    async def update(self, order_id: str, state: OrderState) -> None:
        async with self._lock:
            self._orders[order_id] = state
```

However, the preferred design is to avoid shared mutable state entirely by using immutable snapshots and event-sourced or reducer-style state transitions.

---

### 5.5 Cancellation must be safe

Async execution functions must assume cancellation can occur between awaited steps.

For trading, use idempotent client order identifiers.

Good:

```python
client_order_id: str
```

A partially executed pipeline must be recoverable by querying or reconciling the kernel state, not by assuming that no cancellation can occur.

---

## 6. Side-effect rules

### 6.1 No hidden side effects

Functions in domain and compiler modules must not:

- perform network I/O
- perform filesystem I/O
- read environment variables
- read global configuration
- log directly
- print
- mutate global state
- create tasks
- start timers
- read the wall clock
- generate random values
- depend on execution order outside their inputs

They must return outputs determined only by their inputs.

---

### 6.2 Time is injected

Do not call:

```python
datetime.now()
time.time()
time.monotonic()
```

inside domain or compiler logic.

Use a typed clock port:

```python
from datetime import datetime
from typing import Protocol

class Clock(Protocol):
    def now(self) -> datetime: ...
```

Production adapters provide the real clock. Tests provide fixed clocks.

---

### 6.3 Identifiers are injected

Do not generate IDs inside pure domain functions.

Bad:

```python
order_id = uuid4().hex
```

Good:

```python
@dataclass(frozen=True, slots=True)
class IdGenerator(Protocol):
    def next_client_order_id(self) -> str: ...
```

or pass the ID in from the application layer.

---

### 6.4 Diagnostics are returned, not printed

Do not log from core modules.

Return diagnostics as data:

```python
@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    message: str
```

The composition root or an adapter may later emit diagnostics.

---

## 7. Import rules

### 7.1 No circular imports

Modules must form a directed acyclic graph.

Recommended AIOS layering:

```text
aios.domain
aios.kernel
aios.compiler
aios.application
aios.adapters
aios.composition
```

Dependency rules:

```text
aios.domain       imports nothing internal
aios.kernel       imports aios.domain only
aios.compiler     imports aios.domain only
aios.application  imports aios.domain, aios.kernel interfaces, aios.compiler interfaces
aios.adapters     imports aios.domain and application interfaces
aios.composition  imports everything needed for wiring
```

The kernel and compiler must remain independent.

---

### 7.2 Kernel/compiler isolation

Required architectural invariant:

```text
kernel   -> no dependency on compiler
compiler -> no dependency on kernel
```

The compiler optimizes plans.

The kernel executes plans.

The application pipeline decides whether to use the compiler.

---

### 7.3 Type-only imports

If a type import is needed only for annotations, use:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aios.domain.plan import ExecutionPlan
```

However, do not use this to hide architectural cycles. Fix the layering instead.

---

## 8. Forbidden techniques

The following are forbidden in production modules.

### 8.1 No reflection

Do not use:

```python
getattr(...)
setattr(...)
hasattr(...)
delattr(...)
inspect(...)
importlib.import_module(...)
eval(...)
exec(...)
dynamic metaclass tricks
dynamic class generation
```

for normal application flow.

Explicit dispatch is required.

Good:

```python
match command:
    case SubmitOrder():
        return await submit_order(command)
    case CancelOrder():
        return await cancel_order(command)
```

Bad:

```python
handler = getattr(handlers, command.name)
return await handler(command)
```

---

### 8.2 No monkey patching

Do not patch modules, classes, or functions in production code.

Tests must also avoid monkey patching. Use dependency injection and fakes instead.

Bad:

```python
monkeypatch.setattr(module, "function", fake)
```

Good:

```python
service = Service(kernel=FakeKernel())
```

---

### 8.3 No import-time side effects

Modules must not perform work at import time.

Forbidden:

```python
config = load_config()
engine = create_engine()
asyncio.run(start())
logging.basicConfig()
```

Module import must be safe, inert, and side-effect free.

---

## 9. Compiler as an optional optimization layer

The compiler must satisfy this contract:

```text
Input: canonical ExecutionPlan
Output: optimized ExecutionPlan
```

The compiler must preserve semantics or fail safely.

The kernel must remain able to execute the original canonical plan without the compiler.

The compiler must be removable.

---

### 9.1 Required compiler behavior

A compiler pass must:

1. Be deterministic.
2. Be pure.
3. Not perform I/O.
4. Not mutate input plans.
5. Return a new plan.
6. Preserve trading semantics unless a validator explicitly proves equivalence.
7. Raise only typed compiler errors on failure.
8. Allow fallback to the original plan.

---

### 9.2 Required runtime behavior

The execution runtime must:

1. Accept a compiler optionally.
2. Use the original plan if the compiler is disabled.
3. Use the original plan if the compiler fails.
4. Use the original plan if validation rejects the optimized plan.
5. Return diagnostics explaining the decision.
6. Never require the compiler to be present.

This preserves determinism and resilience.

---

## 10. Reference implementation

The following module demonstrates the standard.

It is intentionally small, typed, immutable, async-safe, and free of global mutable state.

```python
from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from enum import StrEnum
from typing import Protocol, final


class CompilerError(Exception):
    """Raised when a compiler pass cannot safely transform a plan."""


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True, slots=True)
class OrderIntent:
    client_order_id: str
    symbol: str
    side: Side
    quantity: Decimal

    def with_quantity(self, quantity: Decimal) -> OrderIntent:
        return replace(self, quantity=quantity)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    plan_id: str
    intents: tuple[OrderIntent, ...]

    def with_intents(self, intents: tuple[OrderIntent, ...]) -> ExecutionPlan:
        return replace(self, intents=intents)


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    client_order_id: str
    accepted: bool
    reject_reason: str | None = None


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class CompilationDecision:
    plan: ExecutionPlan
    used_compiler: bool
    diagnostics: tuple[Diagnostic, ...]


class ExecutionKernel(Protocol):
    async def submit(self, intent: OrderIntent) -> ExecutionReport: ...


class PlanOptimizer(Protocol):
    def optimize(self, plan: ExecutionPlan) -> ExecutionPlan:
        """
        Pure transformation.

        Must not mutate the input plan.
        Must not perform I/O.
        Must raise CompilerError only for safe fallback conditions.
        """
        ...


class PlanValidator(Protocol):
    def validate(
        self,
        original: ExecutionPlan,
        candidate: ExecutionPlan,
    ) -> tuple[Diagnostic, ...]:
        """
        Returns an empty tuple when the candidate is semantically acceptable.

        Returns diagnostics when the candidate must be rejected.
        """
        ...


@final
class PassThroughOptimizer:
    """
    Safe no-op optimizer.

    Useful when the compiler is enabled structurally but no optimization
    passes are configured.
    """

    def optimize(self, plan: ExecutionPlan) -> ExecutionPlan:
        return plan


@final
class CompositeOptimizer:
    """
    Applies compiler passes in deterministic order.

    Passes are immutable and explicitly injected.
    """

    def __init__(self, passes: tuple[PlanOptimizer, ...]) -> None:
        self._passes = passes

    def optimize(self, plan: ExecutionPlan) -> ExecutionPlan:
        current = plan
        for optimizer in self._passes:
            current = optimizer.optimize(current)
        return current


@final
class ExactPlanValidator:
    """
    Strict validator.

    Rejects any change. This is the safest initial validator for a compiler
    layer that must not alter execution semantics.
    """

    def validate(
        self,
        original: ExecutionPlan,
        candidate: ExecutionPlan,
    ) -> tuple[Diagnostic, ...]:
        if original == candidate:
            return ()

        return (
            Diagnostic(
                code="compiler.plan_changed",
                message="Compiled plan is not exactly equivalent to the original plan.",
            ),
        )


@final
class OptionalCompiler:
    """
    Compiler boundary.

    This component is not required by the kernel. It is an optional
    optimization layer that may be disabled or removed without affecting
    execution correctness.
    """

    def __init__(
        self,
        optimizer: PlanOptimizer | None,
        validator: PlanValidator,
    ) -> None:
        self._optimizer = optimizer
        self._validator = validator

    def compile(self, plan: ExecutionPlan) -> CompilationDecision:
        if self._optimizer is None:
            return CompilationDecision(
                plan=plan,
                used_compiler=False,
                diagnostics=(
                    Diagnostic(
                        code="compiler.disabled",
                        message="Compiler is disabled.",
                    ),
                ),
            )

        try:
            candidate = self._optimizer.optimize(plan)
        except CompilerError as exc:
            return CompilationDecision(
                plan=plan,
                used_compiler=False,
                diagnostics=(
                    Diagnostic(
                        code="compiler.error",
                        message=str(exc),
                    ),
                ),
            )

        diagnostics = self._validator.validate(
            original=plan,
            candidate=candidate,
        )

        if diagnostics:
            return CompilationDecision(
                plan=plan,
                used_compiler=False,
                diagnostics=diagnostics,
            )

        return CompilationDecision(
            plan=candidate,
            used_compiler=True,
            diagnostics=(),
        )


@dataclass(frozen=True, slots=True)
class PipelineResult:
    decision: CompilationDecision
    reports: tuple[ExecutionReport, ...]


@final
class ExecutionPipeline:
    """
    Orchestrates optional compilation and kernel execution.

    This class performs no hidden I/O, owns no global state, and does not
    depend on concrete broker adapters.
    """

    def __init__(
        self,
        kernel: ExecutionKernel,
        compiler: OptionalCompiler,
    ) -> None:
        self._kernel = kernel
        self._compiler = compiler

    async def run(self, plan: ExecutionPlan) -> PipelineResult:
        decision = self._compiler.compile(plan)

        reports: list[ExecutionReport] = []

        for intent in decision.plan.intents:
            report = await self._kernel.submit(intent)
            reports.append(report)

        return PipelineResult(
            decision=decision,
            reports=tuple(reports),
        )
```

---

## 11. Unit-test example

Tests must not monkey patch. Tests must use local fakes and explicit injection.

```python
from decimal import Decimal

import pytest

from aios.execution import (
    ExactPlanValidator,
    ExecutionPipeline,
    ExecutionPlan,
    ExecutionReport,
    OptionalCompiler,
    OrderIntent,
    Side,
)


class RecordingKernel:
    """
    Test double.

    It records submitted intents locally.
    It does not use global state.
    """

    def __init__(self) -> None:
        self.submitted: list[OrderIntent] = []

    async def submit(self, intent: OrderIntent) -> ExecutionReport:
        self.submitted.append(intent)
        return ExecutionReport(
            client_order_id=intent.client_order_id,
            accepted=True,
        )


@pytest.mark.asyncio
async def test_pipeline_executes_original_plan_when_compiler_is_disabled() -> None:
    intent = OrderIntent(
        client_order_id="order-1",
        symbol="BTCUSD",
        side=Side.BUY,
        quantity=Decimal("0.01"),
    )

    plan = ExecutionPlan(
        plan_id="plan-1",
        intents=(intent,),
    )

    kernel = RecordingKernel()

    compiler = OptionalCompiler(
        optimizer=None,
        validator=ExactPlanValidator(),
    )

    pipeline = ExecutionPipeline(
        kernel=kernel,
        compiler=compiler,
    )

    result = await pipeline.run(plan)

    assert result.decision.used_compiler is False
    assert result.decision.plan is plan
    assert kernel.submitted == [intent]
    assert result.reports == (
        ExecutionReport(
            client_order_id="order-1",
            accepted=True,
            reject_reason=None,
        ),
    )
```

---

## 12. Module layout recommendation

Use this structure for AIOS modules:

```text
aios/
    domain/
        __init__.py
        plan.py
        orders.py
        diagnostics.py
        clocks.py
        errors.py

    kernel/
        __init__.py
        executor.py
        reconciler.py

    compiler/
        __init__.py
        optimizer.py
        validator.py
        passes/
            __init__.py

    application/
        __init__.py
        pipeline.py
        use_cases.py

    adapters/
        __init__.py
        broker/
        persistence/
        clock/
        id_generator/

    composition/
        __init__.py
        root.py
```

Public APIs should be exported through `__init__.py`.

Internal implementation modules should not be imported directly by other packages unless explicitly allowed.

---

## 13. Import-linter rules

Use architecture tests to enforce the layering.

Example contract style:

```ini
[importlinter]
root_packages =
    aios

[importlinter:contract:layering]
name = AIOS layering
type = layers
layers =
    aios.composition
    aios.adapters
    aios.application
    aios.compiler
    aios.kernel
    aios.domain

[importlinter:contract:kernel_must_not_import_compiler]
name = Kernel must not import compiler
type = forbidden
source_modules =
    aios.kernel
forbidden_modules =
    aios.compiler

[importlinter:contract:compiler_must_not_import_kernel]
name = Compiler must not import kernel
type = forbidden
source_modules =
    aios.compiler
forbidden_modules =
    aios.kernel

[importlinter:contract:domain_must_not_import_infrastructure]
name = Domain must not import infrastructure
type = forbidden
source_modules =
    aios.domain
forbidden_modules =
    aios.adapters
    aios.application
    aios.composition
    aios.kernel
    aios.compiler
```

---

## 14. Static analysis enforcement

Use strict mypy.

Recommended configuration:

```toml
[tool.mypy]
strict = true
disallow_any_unimported = true
disallow_any_explicit = true
disallow_untyped_defs = true
disallow_untyped_calls = true
disallow_untyped_decorators = true
warn_return_any = true
warn_unused_ignores = true
no_implicit_optional = true
check_untyped_defs = true
```

Use Ruff with at least:

```toml
[tool.ruff.lint]
select = [
    "E",
    "F",
    "I",
    "UP",
    "B",
    "C4",
    "ASYNC",
    "SIM",
    "TID",
    "RUF",
]
```

Forbidden imports should include:

```text
inspect
importlib
pkgutil
ctypes
multiprocessing in async core modules
threading in async core modules
```

unless explicitly allowed inside an isolated adapter.

---

## 15. Applied to trading bot modules

For trading modules such as DCA and GRID, the same rules apply.

### DCA module responsibilities

```text
dca.domain
    -> averaging math, layer spacing, take-profit derivation

dca.application
    -> orchestrate DCA plan creation

dca.adapters
    -> broker/exchange order submission
```

The DCA domain module must not call CCXT directly.

Good:

```python
@dataclass(frozen=True, slots=True)
class DcaLayerPlan:
    base_order: OrderIntent
    safety_orders: tuple[OrderIntent, ...]
    take_profit_price: Decimal
```

Bad:

```python
async def create_dca_plan(...):
    exchange = ccxt.binance()
    ticker = exchange.fetch_ticker("BTC/USDT")
```

Exchange access belongs in an adapter.

---

### GRID module responsibilities

```text
grid.domain
    -> geometric grid calculation, range validation, line generation

grid.application
    -> plan construction and rebalancing orchestration

grid.adapters
    -> order placement and cancellation
```

The grid calculator should be pure:

```python
def build_grid_lines(
    low_price: Decimal,
    high_price: Decimal,
    grid_levels: int,
) -> tuple[Decimal, ...]: ...
```

It must not read market data directly.

Market data must be injected as typed input.

---

## 16. Definition of done

A module is complete only if all of the following are true:

- [ ] It has one responsibility.
- [ ] It passes strict mypy.
- [ ] It has no `Any` without approved justification.
- [ ] It uses frozen slotted dataclasses for value objects.
- [ ] It has no global mutable state.
- [ ] It has no module-level side effects.
- [ ] It has no circular imports.
- [ ] It has no reflection.
- [ ] It has no monkey patching.
- [ ] It has no hidden I/O.
- [ ] It has no direct clock or random usage in core logic.
- [ ] It is async-safe if async.
- [ ] It is unit-testable without network, filesystem, or database access.
- [ ] It depends only on lower architectural layers.
- [ ] Compiler functionality is optional and can be disabled without breaking execution.
- [ ] Kernel execution remains correct with the compiler removed.
- [ ] Diagnostics are returned as data.
- [ ] Tests use explicit fakes, not patches.

---

## 17. Final architectural invariant

The resulting system must satisfy:

```text
Kernel correctness does not depend on the compiler.
Compiler availability does not affect execution safety.
Optimized execution is used only when validation proves equivalence.
Disabled or failed compilation automatically falls back to canonical execution.
All modules remain deterministic, testable, and independently replaceable.
```

This preserves the proven execution kernel while allowing the compiler to act purely as a safe, optional optimization layer.
