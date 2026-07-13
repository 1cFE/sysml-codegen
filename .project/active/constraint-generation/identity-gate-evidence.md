# Item 7 Identity-Gate Evidence — Aggregator/Class Scale Benchmark (orchestrator, 2026-07-12)

S4 carry-forward (4): take the module-identity decision together with the measured
aggregator-schema scale limit. Benchmark: `bench_aggregator_scale.py` (this directory),
run in the repo venv.

| N assertions | agg schema build (once) | agg validate (per case) | class-per-N source | exec/import |
|---|---|---|---|---|
| 100 | 4.5 ms | 0.1 ms | 33 KB | 6.2 ms |
| 1,000 | 41 ms | 0.9 ms | 334 KB | 67 ms |
| 10,000 | 447 ms | 11 ms | 3.3 MB | 698 ms |

Conclusion: no practical scale limit at plausible model sizes (IFE-class models are tens of
assertions; even thousands are cheap). The concept's module-fusion revisit trigger ("past a
measured aggregator-schema limit") is far beyond realistic scale. The S4 runtime finding
stands: a YAML module instance cannot learn its own key at run time, which is what forced
class-per-concrete-assertion in the slice; id-injection would require new runtime machinery.
