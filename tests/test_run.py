import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
from src.grid import Grid
from src.rule import Rule
from src.simulator import Simulator

def main():
    # Create a 3x3 grid with a simple pattern
    grid = Grid(3)
    initial_state = np.array([
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0]
    ])
    grid.set_state(initial_state)
    
    # Create a rule (this is similar to Game of Life)
    # Cell becomes/stays alive if it has 2 or 3 neighbors
    rule = Rule([2, 3])
    
    # Create simulator
    sim = Simulator(grid, rule)
    
    # Find the cycle
    steps_before_cycle, cycle_length = sim.find_cycle(max_steps=100)
    
    # Total unique states is steps_before_cycle + 1 (to include initial state)
    unique_states = steps_before_cycle + 1
    
    print(f"Initial state:\n{initial_state}")
    print(f"Number of unique states: {unique_states}")
    print(f"(Composed of initial state + {steps_before_cycle} steps before first repeat)")
    print(f"Cycle length: {cycle_length}")
    print(f"Final state:\n{sim.grid.state}")

if __name__ == "__main__":
    main() 