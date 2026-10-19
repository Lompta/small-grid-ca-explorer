import numpy as np
from typing import Set
from src.bit_simulator import BitSimulator
from src.find_longest_runs import simulate_configuration
from src.grid import Grid
from src.rule import Rule

def compare_single_case(grid_array: np.ndarray, birth_conditions: Set[int]) -> bool:
    """Compare results between original and bit implementations for a single case"""
    # Original implementation
    grid = Grid(len(grid_array))
    grid.set_state(grid_array)
    rule = Rule(list(birth_conditions))
    orig_result = simulate_configuration(grid, rule)
    
    # Bit implementation
    bit_sim = BitSimulator(len(grid_array))
    initial_state = bit_sim.grid.to_int(grid_array)
    bit_unique_states, bit_cycle_length = bit_sim.simulate_rule(birth_conditions, initial_state)
    
    matches = (orig_result.unique_states == bit_unique_states and 
              orig_result.cycle_length == bit_cycle_length)
    
    if not matches:
        print(f"\nMismatch found:")
        print(f"Initial grid:\n{grid_array}")
        print(f"Birth conditions: {birth_conditions}")
        print(f"Original: {orig_result.unique_states} states, cycle {orig_result.cycle_length}")
        print(f"Bit-based: {bit_unique_states} states, cycle {bit_cycle_length}")
    
    return matches

def test_known_cases():
    """Test some known cases from your existing tests"""
    # Test case from test_problematic_configuration
    grid = np.array([
        [1, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
    ])
    birth_conditions = {4, 5}
    assert compare_single_case(grid, birth_conditions)
    
    # Test case from test_simple_cycle
    grid = np.array([
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1]
    ])
    birth_conditions = {0, 1}
    assert compare_single_case(grid, birth_conditions)

if __name__ == '__main__':
    test_known_cases() 