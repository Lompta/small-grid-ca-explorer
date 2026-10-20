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

Post placeholders (4x4, shifts/rotations/reflections, with inverse configs merged):
**[x] = 433**, **[y] = 433 x 512 = 221,696**. Without merging inverses there are
805 classes; the solver uses 805 and halves the rules instead (805 x 256).

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

## Post: revisions planned
- Fix the inverted-rule example: the partner of {3,4} is {0,1,2,3,6,7,8}.
  General rule: k is in the partner iff 8-k is NOT in the original.
- Fix the first 6x6 example: the panel says {3,4} but the text says 4 or 5, and the
  two cells with 5 neighbours behave differently.
- Revise "Claude's techniques don't differ at root". The new ingredient is
  algorithmic: the per-rule graph, so each class costs ~1 step instead of a whole run.
- The divisibility theory is undercut by 8x8 being wild. Possible new mystery: the
  same rules that are tame on 6x6 run for millions of steps on 8x8.
- Soften "cleverness won't help" for 7x7. Distinguished-point memoisation might make
  7x7 feasible: months on the laptop, or roughly $500-2k in the cloud (estimated,
  not measured).
- 9x9 "all of humanity would fail" is shaky; 10x10 and up is solid.
- Fill in [x] and [y].

## Next: images (tomorrow)
Diagrams and GIFs for the post. The state-by-state runs are in
`fast/longest_6x6_rule_203.txt` and `fast/longest_5x5_rule_205.txt`. Hex is one state
per line, and bit r*N+c is the cell at row r, column c.
The 2025 GIF code is in `src/generate_ca_gifs.py`.
For the post, use the 2025 rule (not the solver's partner rule) for 4x4 and 5x5.
