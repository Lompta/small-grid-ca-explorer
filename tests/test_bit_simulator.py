import pytest
from src.bit_simulator import BitSimulator
from src.bit_grid import BitGrid

def test_known_3x3_configuration():
    """Test against a known configuration from 3x3_results.md"""
    simulator = BitSimulator(3)
    bg = BitGrid(3)
    
    # Configuration 491 from results
    birth_conditions = {0, 1, 5}
    initial_grid = [
        [True, True, False],
        [True, False, True],
        [False, False, False]
    ]
    
    initial_state = bg.to_int(initial_grid)
    unique_states, cycle_length = simulator.simulate_rule(birth_conditions, initial_state)
    
    assert unique_states == 4
    assert cycle_length == 2

def test_batch_processing():
    """Test that we can process multiple states efficiently"""
    simulator = BitSimulator(3)
    results = simulator.find_interesting_configurations(min_unique_states=4)
    
    # Verify we found at least one interesting configuration
    assert len(results) > 0
    
    # Check structure of results
    for birth_conditions, initial_state, unique_states, cycle_length in results:
        assert isinstance(birth_conditions, set)
        assert isinstance(initial_state, int)
        assert unique_states >= 4 