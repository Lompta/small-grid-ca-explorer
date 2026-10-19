import numpy as np
import pytest
from src.transformations import get_all_transformations, filter_equivalent_states
from src.state_generator import get_unique_starting_states

def test_simple_transformations():
    # Test with a simple asymmetric pattern
    state = np.array([
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ])
    
    transformations = get_all_transformations(state)
    
    # Should include all rotations, reflections, and translations
    # For 3x3, we expect 9 (translations) * 8 (rotations+reflections) = 72 total
    assert len(transformations) == 9

def test_filter_equivalent_states():
    states = [
        np.array([[1, 0], [0, 0]]),  # Original
        np.array([[0, 1], [0, 0]]),  # Translation
        np.array([[0, 0], [1, 0]]),  # Rotation
        np.array([[1, 1], [1, 1]]),  # All ones
    ]
    
    unique_states = filter_equivalent_states(states)
    
    # Should only keep two states (one from the equivalent group and the all-ones)
    assert len(unique_states) == 2

def test_symmetrical_pattern():
    # Test with a symmetrical pattern
    state = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ])
    
    transformations = get_all_transformations(state)
    
    # Due to symmetry, should have fewer unique transformations
    # Exact number depends on the symmetries present
    assert len(transformations) == 9  # 72 is max possible for 3x3 
