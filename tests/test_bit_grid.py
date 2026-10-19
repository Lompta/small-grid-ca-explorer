import pytest
from src.bit_grid import BitGrid

def test_bit_grid_conversions():
    bg = BitGrid(3)
    grid = [
        [True, False, True],
        [False, True, False],
        [True, False, True]
    ]
    state = bg.to_int(grid)
    recovered_grid = bg.to_grid(state)
    assert recovered_grid == grid

def test_neighbor_counting():
    bg = BitGrid(3)
    grid = [
        [True, True, False],
        [True, False, False],
        [False, False, False]
    ]
    state = bg.to_int(grid)
    assert bg.count_neighbors(state, 0, 0) == 2
    assert bg.count_neighbors(state, 1, 1) == 3

def test_next_state():
    bg = BitGrid(3)
    grid = [
        [True, True, False],
        [True, False, False],
        [False, False, False]
    ]
    state = bg.to_int(grid)
    birth_conditions = {2, 3}
    next_state = bg.next_state(state, birth_conditions)
    next_grid = bg.to_grid(next_state)
    # Add assertions based on expected next state

def test_canonical_form():
    bg = BitGrid(3)
    grid = [
        [True, False, False],
        [False, False, False],
        [False, False, False]
    ]
    state = bg.to_int(grid)
    rotated = bg.rotate_90(state)
    assert bg.get_canonical_form(state) == bg.get_canonical_form(rotated) 