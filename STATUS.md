# Status (2026-10-20)

## Results
| Grid | Longest run | Rule (on with k neighbours) | Status |
|---|---|---|---|
| 3x3 | 4 | {0,5} in post; solver reports {0,2} | exact |
| 4x4 | 14 | {1,4} (partner {0,1,2,3,5,6,8}) | exact |
| 5x5 | 916 | {0,3,4,7} (partner {0,2,3,6,7}) | exact |
| 6x6 | **1,717** | {0,1,3,6,7} (partner {0,3,4,6}); 1,701 tail + 16 cycle | exact, unique up to symmetry |
| 7x7 | ≥ 545,752 | {2,3,5,7}, start `19d630e284a4e` | lower bound from sampling |
| 8x8 | ≥ 5,064,397 | {0,1,3,6,7}, start `d5c3e041c7eb59a9` | lower bound from sampling |

Every number above was re-checked by a separate simulation that shares no code with
the solver.

## Code
- `src/`, `tests/`, `results/`: 2025 Python work, committed unchanged.
- `fast/ca_quotient.cpp`: exact solver for up to 6x6. It builds a graph of
  symmetry classes per rule and peels it to find tails. Modes:
  - `--reconstruct RULE`: rebuild the best run for a rule and verify it.
  - `--count RULE`: count the starts that tie for that rule's best run.
- `fast/sample_runs.cpp`: random sampling per rule, used for the 7x7/8x8 lower
  bounds and cost estimates.
- `fast/gpu_bench_7x7.cu`: GPU speed test.
- `fast/README.md`: write-up of the method and the estimates.
- `fast/longest_6x6_rule_203.txt`, `fast/longest_5x5_rule_205.txt`: the record runs,
  one state per line in hex. Bit r*N+c is the cell at row r, column c.
