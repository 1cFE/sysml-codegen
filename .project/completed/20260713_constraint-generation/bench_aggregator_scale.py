"""Orchestrator benchmark for the Item 7 identity gate: aggregator-schema and
class-per-assertion scale behavior.

Measures, for N concrete assertions:
  1. pydantic create_model with N required structured fields (the exact-schema
     aggregator input) — build time + one validation.
  2. N distinct generated classes (class-per-concrete-assertion) — module source
     size + exec (import) time, vs one class with id-injection.
"""

from __future__ import annotations

import time

from pydantic import BaseModel, create_model


class ConstraintEvaluation(BaseModel):
    constraint_id: str
    actual: float
    status: str
    margin: float | None = None


def bench_aggregator(n: int) -> tuple[float, float]:
    t0 = time.perf_counter()
    fields = {f"c{i:05d}": (ConstraintEvaluation, ...) for i in range(n)}
    Agg = create_model(f"AggIn{n}", **fields)
    t_build = time.perf_counter() - t0
    payload = {
        f"c{i:05d}": {"constraint_id": f"c{i:05d}", "actual": 1.0, "status": "satisfied"}
        for i in range(n)
    }
    t0 = time.perf_counter()
    Agg.model_validate(payload)
    t_validate = time.perf_counter() - t0
    return t_build, t_validate


CLASS_TMPL = '''
class ConstraintModule_{i:05d}:
    CONSTRAINT_ID = "c{i:05d}"
    def run(self, inputs):
        actual = inputs["x"]
        satisfied = actual <= 100.0
        return {{"constraint_id": self.CONSTRAINT_ID, "actual": actual,
                "status": "satisfied" if satisfied else "violated",
                "margin": 100.0 - actual}}
'''


def bench_classes(n: int) -> tuple[int, float]:
    src = "\n".join(CLASS_TMPL.format(i=i) for i in range(n))
    ns: dict = {}
    t0 = time.perf_counter()
    exec(compile(src, f"gen_{n}", "exec"), ns)  # noqa: S102 — benchmark of generated code
    t_exec = time.perf_counter() - t0
    return len(src), t_exec


def main() -> None:
    print(f"{'N':>6} | {'agg build':>10} | {'agg validate':>12} | {'src bytes':>10} | {'exec time':>10}")
    for n in (10, 100, 500, 1000, 5000, 10000):
        tb, tv = bench_aggregator(n)
        size, te = bench_classes(n)
        print(f"{n:>6} | {tb*1000:>9.1f}ms | {tv*1000:>11.1f}ms | {size:>10,} | {te*1000:>9.1f}ms")


if __name__ == "__main__":
    main()
