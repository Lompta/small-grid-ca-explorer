import pytest
import numpy as np
from src.grid import Grid

def test_grid_initialization():
    grid = Grid(3)
    assert grid.size == 3
    assert grid.state.shape == (3, 3)
    assert np.all(grid.state == 0)

def test_invalid_state_size():
    grid = Grid(3)
    with pytest.raises(ValueError):
        grid.set_state(np.zeros((4, 4)))

def test_neighbor_count_single_cell():
    """Test neighbor counting with a single live cell in 3x3 grid"""
    grid = Grid(3)
    initial_state = np.array([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0]
    ])
    grid.set_state(initial_state)
    expected = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ])    
    np.testing.assert_array_equal(grid.get_neighbor_count(), expected)

def test_neighbor_count_all_cells():
    """Test neighbor counting with all live cells"""
    grid = Grid(3)
    grid.set_state(np.ones((3, 3), dtype=np.int8))
    expected = np.full((3, 3), 8, dtype=np.int8)
    np.testing.assert_array_equal(grid.get_neighbor_count(), expected)

def test_neighbor_count_half_cells():
    """Test neighbor counting with half cells alive"""
    grid = Grid(3)
    initial_state = np.array([
        [1, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
    ])
    grid.set_state(initial_state)
    # Each cell should see 4 or 5 neighbors depending on position
    expected = np.array([
        [4, 4, 4],
        [4, 4, 5],
        [5, 5, 5]
    ])
    np.testing.assert_array_equal(grid.get_neighbor_count(), expected)

def test_neighbor_count_4x4():
    """Test neighbor counting in a 4x4 grid with wraparound"""
    grid = Grid(4)
    initial_state = np.array([
        [1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1]
    ])
    grid.set_state(initial_state)
    # Each corner should see the other corners as neighbors
    # Plus their immediate neighbors along edges
    expected = np.array([
        [1, 1, 1, 2],
        [1, 1, 0, 1],
        [1, 0, 1, 1],
        [2, 1, 1, 1]
    ])
    np.testing.assert_array_equal(grid.get_neighbor_count(), expected) 