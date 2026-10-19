from typing import Set, Tuple, List
from .bit_grid import BitGrid

class BitSimulator:
    def __init__(self, size: int):
        self.size = size
        self.grid = BitGrid(size)
        
    def simulate_rule(self, birth_conditions: Set[int], initial_state: int, max_steps: int = 1000) -> Tuple[int, int]:
        """
        Simulates the CA with given birth conditions and initial state.
        Returns (unique_states, cycle_length)
        """
        seen_states = {}
        current_state = initial_state
        step = 0
        
        while step < max_steps:
            # Use exact state, not canonical form!
            if current_state in seen_states:
                cycle_start = seen_states[current_state]
                cycle_length = step - cycle_start
                unique_states = len(seen_states)
                return unique_states, cycle_length
                
            seen_states[current_state] = step
            current_state = self.grid.next_state(current_state, birth_conditions)
            step += 1
            
        return len(seen_states), 0  # No cycle found within max_steps
    
    def find_interesting_configurations(self, min_unique_states: int = 4) -> List[Tuple[Set[int], int, int, int]]:
        """
        Find configurations with at least min_unique_states unique states.
        Returns list of (birth_conditions, initial_state, unique_states, cycle_length)
        """
        results = []
        
        # Generate all possible birth conditions
        for i in range(512):  # 2^9 possible birth rules
            birth_conditions = {j for j in range(9) if (i & (1 << j))}
            
            # Generate initial states (we can do this in batches for 5x5)
            for initial_state in range(1 << (self.size * self.size)):
                # Skip states that aren't canonical
                if self.grid.get_canonical_form(initial_state) != initial_state:
                    continue
                    
                unique_states, cycle_length = self.simulate_rule(birth_conditions, initial_state)
                
                if unique_states >= min_unique_states:
                    results.append((birth_conditions, initial_state, unique_states, cycle_length))
                    
        return results
    
    def process_batch(self, start_state: int, batch_size: int, birth_conditions: Set[int]) -> List[Tuple[int, int, int]]:
        """Process a batch of states for a given rule"""
        results = []
        for state in range(start_state, min(start_state + batch_size, 1 << (self.size * self.size))):
            # Skip non-canonical forms
            if self.grid.get_canonical_form(state) != state:
                continue
                
            unique_states, cycle_length = self.simulate_rule(birth_conditions, state)
            if unique_states >= 4:  # or whatever threshold
                results.append((state, unique_states, cycle_length))
        return results

def format_grid(grid: List[List[bool]]) -> str:
    """Convert grid to string representation using ⬛ for True and ⬜ for False"""
    return '\n'.join(''.join('⬛' if cell else '⬜' for cell in row) for row in grid) 