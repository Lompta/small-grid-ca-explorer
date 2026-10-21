### Intro
This document was written in 2025 to help Cursor orient to the project, such that it could in turn help me solve the 5x5 case. This effort succeeded: the answer is 916. Yesterday, as of this writing on 10/19, Claude Code oriented to the problem using a draft blog post on [my blog](https://justismills.substack.com), and created the code in fast/ to solve the 6x6 case. This also succeeded: the answer is 1717.

The rest of this document is a snapshot from 2025. It was written by me. Other docs in the repo are Claude generated in this latest 2026 tranche of work, so take these with grains of salt. For a more comprehensive and perhaps clearer explanation of the problem, with lots of diagrams and examples, see my blog.

### Overview
The objective of this project is to study finite cellular automata. Specifically, wraparound small-grid cellular automata in a torus. So, the cell above any cell on the top row is the cell on the bottom row directly below it, and the cell to the right of any cell on the rightmost column is the cell on the leftmost column directly to the left of it.

The types of CA under study are a generalization of the game of life. Basically, for all integers n from 0 to 8, all cells share a rule such that if n of the 8 cells surrounding a cell are alive, then the cell will be alive. For example, in the rule [0, 1, 0, 1, 0, 0, 0, 0, 0], the cell will be alive in the next generation if and only if 1 or 3 of the 8 cells surrounding it are alive.

Specifically, the research question is: for various finite wraparound grid sizes nxn, and for any arbitrary rule as described above, what is the maximum number of generations that can be run before the CA becomes periodic?

In the past, I have solved this question for 3x3 and 4x4 grids. In 3x3, it can be solved with a pencil and paper. 4x4 did not require too much optimization. However, that was some years ago, and computation may have improved. Plus, AI tools may help me make my code more efficient, or help me access more compute. This time, my goal is to solve the question for 5x5 grids.

My plan is, without actually representing the answer to the 3x3 and 4x4 cases, create a more efficient and robust system that can take grid size as a parameter. If it gets the answers I know to be correct for 3x3 and 4x4, I can trust its output for the 5x5 case.

In the past, I have used Python. I would be happy to use Python again, but if necessary can use a more efficient language.

### Past Implementation Strategies
In the past, I represented rules and grids as arrays. Perhaps some other data structure could be more efficient - tensorflow comes to mind, as maybe there are analogous operations for CA transformations with matrices, and tensorflow is already pretty optimized.

Also in the past, I leveraged certain symmetries of the CA to reduce the number of operations needed. For example, the CA is symmetric under rotation, so I only needed to check one of the four possible rotations of the CA to find the period. It's also symmetric under reflection across either the horizontal or vertical axis, and a further division by 2 is possible because the case where inverting both the rule and the starting state is equivalent to the original case. (Inverting just one or the other is not equivalent.)

### Potential Future Strategies
* Use an efficient language, though I'd need help since I'm only highly familiar with Python and Javascript, and some C# from years ago.
* Do the operation in chunks, such that the 5x5 operation could be done over time rather than tying up my system for e.g. a month.
* Use a more efficient operation or data structure, such as matrix operations or a pre-built library like tensorflow.
* Keep track of each "step" that's been done for a given rule before, such that e.g. if I know a given state loops in 5, add 5 to the total up until that point. Given the number of possible states, this may actually be less efficient, but there might be a way where it does help. Another pitfall would be if some step in the loop already occurred in a previous loop, such that the first repeated frame is earlier than this method would naively diagnose.
* For even larger grids than 5x5, such as, say, 10x10, try random rules and start configs to establish a lower bound, even if it's not feasible to find the actual maximum.

### Code Desiderata
Code should be clear and well commented. Auto-generated code should avoid placeholder comments where possible. Everything should be maximally extensible - it should be possible to test just individual rules across start configs, just individual start configs across rules, grids that aren't square, etc. The ability to identify and visualize the longest found run(s) so far would be good, too. Identification more important! Certainly once the program runs, it should be possible to identify the longest run(s) as a proof that a loop that long exists.

### Answer Definition
The answer should be the number of unique states. In other words, the first repeated state doesn't count toward the total. The starting state does, though. So a state that immediately repeats is counted as 1.
