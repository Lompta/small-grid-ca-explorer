from typing import Optional, Tuple, List
import numpy as np
from .grid import Grid
from .rule import Rule
from .results_collector import Result

def simulate_configuration(grid: Grid, rule: Rule, max_steps: int = 1000) -> Result:
    """
    Simulate a single configuration until a cycle is found.
    
    Args:
        grid: Initial grid configuration
        rule: Rule to apply
        max_steps: Maximum steps to simulate before giving up
        
    Returns:
        Result object containing simulation results
    """
    # Store initial state before simulation
    initial_state = grid.state.copy()
    
    sim = Simulator(grid, rule)
    steps_before_cycle, cycle_length = sim.find_cycle(max_steps)
    
    return Result(
        rule_conditions=rule.birth_conditions.tolist(),
        initial_state=initial_state,
        unique_states=steps_before_cycle,
        cycle_length=cycle_length
    )

class Simulator:
    """Handles the simulation of cellular automaton evolution."""
    
    def __init__(self, grid: Grid, rule: Rule):
        self.grid = grid
        self.rule = rule
        self.history = []  # Track states for cycle detection
        
    def step(self) -> None:
        """Advance the simulation by one step."""
        neighbor_counts = self.grid.get_neighbor_count()
        self.grid.state = self.rule.apply(neighbor_counts)
        
    def find_cycle(self, max_steps: int) -> Tuple[int, int]:
        """
        Run the simulation until a cycle is found or max_steps is reached.
        
        Returns:
            Tuple of (steps_before_cycle, cycle_length)
            steps_before_cycle is the number of steps taken before seeing first repeat
        """
        self.history = [self.grid.state.tobytes()]
        
        for step in range(max_steps):
            self.step()
            current_state = self.grid.state.tobytes()
            
            # Check if we've seen this state before
            if current_state in self.history:
                cycle_start = self.history.index(current_state)
                return step + 1, step + 1 - cycle_start
                
            self.history.append(current_state)
            
        return max_steps, 0  # No cycle found within max_steps