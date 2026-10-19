import numpy as np
from src.bit_simulator import BitSimulator

def format_grid(grid):
    """Format grid for readable output"""
    return '\n'.join(' '.join('⬜' if cell else '⬛' for cell in row) for row in grid)

def test_known_14_config():
    """Test a known configuration that should have 14 unique states"""
    grid = np.array([
        [0, 0, 0, 0],
        [0, 0, 1, 1],
        [0, 1, 1, 1],
        [1, 1, 1, 0]
    ])
    birth_conditions = {1, 4}
    
    bit_sim = BitSimulator(4)
    initial_state = bit_sim.grid.to_int(grid)
    
    # Track the evolution
    current_state = initial_state
    seen_states = set()  # Just track the states themselves
    print("\nState evolution:")
    for step in range(20):  # Show first 20 steps or until cycle
        print(f"\nStep {step}:")
        current_grid = bit_sim.grid.to_grid(current_state)
        print(format_grid(current_grid))
        print(f"State value: {current_state}")
        
        if current_state in seen_states:
            print(f"\nExact state repeat detected!")
            print(f"Total unique states: {len(seen_states)}")
            break
            
        seen_states.add(current_state)
        current_state = bit_sim.grid.next_state(current_state, birth_conditions)

if __name__ == "__main__":
    test_known_14_config() 