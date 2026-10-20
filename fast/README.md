# Fast exact solver (2026): 6x6 and a re-check of 3x3–5x5

`ca_quotient.cpp` is a single-file C++ program that solves the problem exactly for
n x n wraparound grids up to 6x6. It finds the longest run of unique states over
**all** rules and **all** start configurations.

| Grid | Symmetry classes of configs | Longest run | Rule (on with k neighbours) | Tail + cycle |
|------|-----------------------------|-------------|-----------------------------|--------------|
| 3x3  | 26                          | 4           | {0,2}                       | 2 + 2        |
| 4x4  | 805                         | 14          | {0,1,2,3,5,6,8}             | 10 + 4       |
| 5x5  | 172,112                     | 916         | {0,2,3,6,7}                 | 136 + 780    |
| 6x6  | 239,123,150                 | **1,717**   | {0,1,3,6,7} (partner: {0,3,4,6}) | 1,701 + 16 |

(For each rule the solver searches one rule of each complementary pair; the other
rule gives the same run with every cell inverted. For example, 5x5 {0,2,3,6,7} is
the partner of the 2025 result {0,3,4,7}.)

The full 6x6 run of all 256 rules took about 85 minutes on a Ryzen 7 4800H (16 threads).
Per-rule results are in `results_6x6.csv`. The columns are rule mask, rule, longest run,
tail, cycle, number of cycles, symmetry classes on cycles, and the deepest tail anywhere.
The record run itself, starting from

```
#.....
##.##.
..#.##
.####.
..#.#.
####.#
```

is listed state by state in `longest_6x6_rule_203.txt`. Its length was checked by
plain simulation, both in the C++ program and in a separate few-line Python script.

**The 6x6 record is unique.** Only one symmetry class of start grids reaches 1,717.
That class contains 288 grids: every shift, rotation and reflection of the grid
above. The inverted copies under the partner rule {0,3,4,6} are the only other
grids that reach 1,717, and no other rule pair comes close.

For comparison, 5x5 has 4 symmetry classes of record starts (800 grids), and all
of them merge into the same path after one step. 4x4 has 8 classes (1,024 grids),
which merge into a single path after 3 steps. In every case only one rule pair
reaches the maximum.
(`ca_quotient N --count RULE` prints these counts; see `count_6x6_rule_203.txt`.)

Runner-up rules for 6x6: {2,3,5,8} gives 1,648; {0,2,3,5,8} gives 1,373; and
{0,1,3,6,7,8} gives 1,329.

## Why not just simulate every start?

The 2025 Python code simulated each start configuration until it repeated. 6x6
has 2^36 ≈ 6.9e10 starts. Even with symmetry, that leaves 2.4e8 starts for each
of 256 rules. Each of those starts can take a thousand or more
steps to repeat, and nobody knows in advance how long the worst ones run.

## The method

1. **Work with symmetry classes, not configurations.** The update rule treats
   every cell the same way. That means it commutes with the 288 symmetries of
   the 6x6 torus: 36 shifts times 8 rotations and reflections. So each class is
   stored once, by its smallest-numbered member. Every class is enumerated, and
   the count is checked against Burnside's lemma, which gives
   239,123,150 classes for 6x6.

2. **Build the whole "next state" graph for a rule.** Each class gets one arrow
   to the class of its successor. That takes one step and one canonicalisation
   per class (a few seconds for 2.4e8 classes on 16 threads).

3. **Peel the graph (Kahn's algorithm).** First remove all classes with no
   predecessor, then the classes that now have none, and so on. Each class's
   removal round is the length of the longest chain leading into it. The classes
   that are never removed are exactly the ones on cycles. The longest run that
   ends in a given cycle is then just *(longest chain leading into the cycle) +
   (cycle length)*.

4. **Tails survive the symmetry reduction exactly.** Suppose a class reaches a
   cycle of classes after μ steps. Then the actual configuration has also
   reached a real cycle after μ steps. (If a configuration later comes back
   shifted or rotated, then repeating that symmetry eventually brings it back
   unshifted, so it was already on a cycle.) Only the cycle length can differ:
   a cycle of classes can be a longer cycle of actual grids that comes back
   rotated or shifted. The real cycle length is measured by simulating one lap
   from a state on the cycle.

5. **Complement trick.** Inverting both the start and the rule gives an inverted
   copy of the same run. Of each such rule pair, exactly one lacks "4 neighbours".
   Only those 256 rules are searched.

Each reported answer is double-checked by `--reconstruct`. That mode walks back
through the graph to a start configuration with the longest tail, then counts its
unique states by plain simulation with a hash set. This check is independent of
the graph logic.

## Building and running (Windows, MSVC Build Tools)

```
build.bat
ca_quotient.exe 5                    # all rules for 5x5 (~1 s)
ca_quotient.exe 6                    # all rules for 6x6 (~1.5 h, ~8 GB RAM)
ca_quotient.exe 6 100 120            # only rules with mask 100..120
ca_quotient.exe 6 --reconstruct 203  # rebuild and verify the best run for one rule
ca_quotient.exe 6 --count 203        # how many starts tie for that rule's best run
```

Rule masks: bit k set means a cell with k live neighbours is on next step. For
example, {0,2,3,6,7} = 1+4+8+64+128 = 205.

On any compiler with OpenMP it should build with something like
`g++ -O2 -fopenmp -mavx2 ca_quotient.cpp`.

## 7x7: sampling and cost estimates (2026-10)

`sample_runs.cpp` runs random starts under every rule and measures each run exactly.
Its output gives the brute-force cost and a lower bound on the answer. Checked on 6x6:
200,000 samples per rule found 1,703, against the exact answer of 1,717, with the same
winning rule.

For 7x7, 20,000 samples per rule (`sample_7x7.csv`) found a run of **545,752** unique
states, from rule {2,3,5,7} starting at hex `19d630e284a4e`. This was re-checked
independently with numpy. So the 7x7 answer is **at least 545,752**, more than 300 times
the 6x6 record. The worst rules average about 40,000 steps per start, so plain brute force
needs about 3.5e18 steps:

| Hardware | Speed (measured / assumed) | Plain brute force |
|---|---|---|
| Laptop CPU, 16 threads | 4e8 steps/s (measured) | ~270 years |
| Laptop RTX 3060 | 2e10 steps/s (measured, `gpu_bench_7x7.cu`) | ~5 years |
| Rented H100s | ~2e11 steps/s each (assumed) | ~5,000 GPU-hours, ~$10-15k |

Storing the whole graph, as the 6x6 solver does, would take about 7 TB per rule.
A realistic path is a memoised search using "distinguished points". Only a sparse
sample of states, plus every cycle state, is remembered in a hash table. Each start
is then walked only until it reaches a remembered state, not to the end of its run.
That could cut the work 10-50x, but it is a substantial engineering project.
