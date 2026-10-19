# Analysis of Finite Wraparound Cellular Automata
## Research Findings Report

### Introduction

This research investigates cellular automata (CA) on finite wraparound grids of varying sizes. Unlike traditional infinite-grid cellular automata like Conway's Game of Life, these CA operate on a torus topology where the edges wrap around - the top connects to the bottom and the left connects to the right.

### Problem Space

#### Rules
The CA rules are defined by "birth conditions" - a list of numbers from 0-8 indicating how many live neighbors will cause a cell to be alive in the next generation. For example, birth conditions [3,4] means a cell will be alive in the next generation if and only if it has exactly 3 or 4 live neighbors.

#### Grid Structure
- Grids are square (nxn)
- Edges wrap around (torus topology)
- Each cell has 8 neighbors
- States are binary (alive/dead)

### Key Findings

#### 3x3 Grid Results
- Maximum unique states: 4
- 704 different configurations achieve this maximum
- Most configurations have cycle length 1 or 2
- Example maximal configuration:
  ```
  ⬛⬛⬛
  ⬛⬛⬜
  ⬜⬜⬜
  ```
  With birth conditions: [4,5]

#### 4x4 Grid Results
- Maximum unique states: 14
- 16 different configurations achieve this maximum
- All maximal configurations have cycle length 4
- Example maximal configuration:
  ```
  ⬛⬛⬛⬛
  ⬛⬛⬜⬜
  ⬛⬜⬜⬜
  ⬜⬜⬜⬛
  ```
  With birth conditions: [1,4]

#### 5x5 Grid Results
- Maximum unique states: 916
- 8 different configurations achieve this maximum
- All maximal configurations have cycle length 780
- Example maximal configuration:
  ```
  ⬛⬛⬛⬛⬛
  ⬛⬛⬜⬛⬜
  ⬛⬜⬜⬛⬛
  ⬜⬜⬜⬜⬛
  ⬜⬜⬛⬜⬜
  ```
  With birth conditions: [0,3,4,7]

### Analysis

#### Growth Pattern
The maximum number of unique states grows dramatically with grid size:
- 3x3: 4 states
- 4x4: 14 states
- 5x5: 916 states

Growth was expected to be fast, since sufficiently large grids can of course create a gigantic number of variety. But the speed of increase is pretty impressive, even given that.

#### Rule Patterns
Interesting patterns emerge in the birth conditions that produce maximal configurations:
- 3x3: Rules tend to involve 4-5 neighbors
- 4x4: Simpler rules ([1,4]) can achieve maximum states
- 5x5: More complex rules involving 3-4 specific neighbor counts

#### Cycle Lengths
- 3x3: Short cycles (1-2 steps)
- 4x4: Consistent 4-step cycles
- 5x5: Much longer cycles (780 steps)

### Conclusions

1. The complexity of these systems grows exponentially with grid size
2. Optimal rules tend to become more specific for larger grids
3. Cycle lengths increase dramatically with grid size
4. Multiple distinct configurations can achieve the maximum number of states
5. The torus topology allows for rich behavioral patterns despite finite size

### Future Research Directions

1. Investigate 6x6 and larger grids
2. Study patterns in rules that produce maximal configurations
3. Analyze the relationship between grid size and cycle length
4. Explore non-square grid configurations
5. Study the impact of different neighborhood definitions

### Appendix: Visualization of State Transitions

#### A1. 3x3 Grid Evolution (Rule: [4, 5])
From sequence_3x3.md, showing the complete 4-state sequence before repetition:
```
Step 0           Step 1           Step 2           Step 3 (Final)
⬛⬛⬛          ⬜⬜⬜          ⬜⬜⬜          ⬛⬛⬛
⬛⬛⬜    →     ⬜⬜⬛    →     ⬜⬜⬜     →    ⬛⬛⬛
⬜⬜⬜          ⬛⬛⬛          ⬜⬜⬜          ⬛⬛⬛
```

#### A2. 4x4 Grid Evolution (Rule: [1, 4])
From sequence_4x4.md, showing the complete 14-state sequence:
```
Step 0              Step 1              Step 2              Step 3
⬛⬛⬛⬛           ⬛⬜⬜⬜           ⬜⬜⬛⬜           ⬛⬛⬛⬛
⬛⬛⬜⬜     →     ⬛⬛⬜⬛     →     ⬛⬛⬛⬛     →     ⬛⬛⬛⬛
⬛⬜⬜⬜           ⬛⬛⬛⬛           ⬛⬛⬜⬛           ⬜⬛⬛⬛
⬜⬜⬜⬛           ⬛⬜⬜⬜           ⬜⬛⬛⬛           ⬛⬜⬛⬜

Step 4              Step 5              Step 6              Step 7
⬛⬜⬛⬜           ⬛⬛⬛⬛           ⬜⬛⬜⬛           ⬛⬛⬜⬛
⬜⬜⬛⬜     →     ⬜⬛⬜⬛     →     ⬛⬛⬜⬛     →     ⬛⬛⬛⬛
⬛⬛⬛⬛           ⬛⬜⬜⬜           ⬜⬛⬜⬛           ⬛⬛⬜⬛
⬛⬛⬜⬛           ⬛⬜⬛⬜           ⬛⬜⬛⬜           ⬜⬜⬜⬜

Step 8              Step 9              Step 10             Step 11
⬛⬛⬛⬛           ⬛⬜⬜⬜           ⬜⬛⬜⬛           ⬛⬛⬜⬛
⬛⬛⬛⬛     →     ⬛⬛⬛⬛     →     ⬜⬜⬛⬜     →     ⬜⬛⬜⬛
⬛⬛⬛⬛           ⬛⬜⬜⬜           ⬜⬛⬜⬛           ⬛⬛⬜⬛
⬛⬛⬜⬛           ⬛⬜⬛⬜           ⬛⬜⬛⬜           ⬜⬜⬜⬜

Step 12             Step 13             Step 14 (Repeats)
⬜⬛⬜⬛           ⬜⬛⬛⬛           ⬜⬛⬜⬛
⬛⬜⬛⬜     →     ⬜⬜⬜⬜     →     ⬜⬜⬛⬜
⬜⬛⬜⬛           ⬜⬛⬛⬛           ⬜⬛⬜⬛
⬛⬜⬜⬜           ⬜⬛⬜⬛           ⬛⬜⬛⬜
```

#### A3. 5x5 Grid Evolution (Rule: [0, 3, 4, 7])
From sequence_5x5.md, showing first few states of the 916-step sequence:
```
Step 0           Step 1           Step 2           Step 3
⬛⬛⬛⬛⬛      ⬜⬜⬜⬜⬜      ⬜⬛⬛⬛⬜      ⬜⬜⬛⬛⬛
⬛⬛⬜⬛⬜  →   ⬛⬜⬛⬜⬜  →   ⬜⬜⬛⬛⬛  →   ⬛⬜⬜⬜⬛
⬛⬜⬜⬛⬛      ⬜⬛⬛⬛⬜      ⬜⬛⬜⬜⬜      ⬜⬛⬛⬜⬜
⬜⬜⬜⬜⬛      ⬛⬛⬛⬜⬛      ⬛⬜⬜⬜⬛      ⬜⬜⬛⬜⬜
⬜⬜⬛⬜⬜      ⬜⬜⬛⬜⬜      ⬛⬜⬛⬛⬛      ⬜⬜⬜⬜⬜
```

Key observations from the actual sequences:
1. The 3x3 grid quickly reaches a stable all-black state after just 4 steps
2. The 4x4 grid shows more complex behavior with a 14-state sequence
3. The 5x5 grid demonstrates dramatically more complex evolution with a 780-step cycle at the end of a 916-step sequence
4. Each grid size shows distinct pattern types in their evolution:
   - 3x3: Quick stabilization
   - 4x4: Regular oscillation
   - 5x5: Long, complex patterns with extensive variation
5. In general, the longest sequences tend to come about starting with about half the grid alive.
