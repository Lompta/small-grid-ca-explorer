import numpy as np
from typing import Iterator, List
from itertools import product
from .transformations import filter_equivalent_states

def generate_all_states(size: int) -> Iterator[np.ndarray]:
    """Generate all possible states for a grid of given size."""
    total_cells = size * size
    for bits in product([0, 1], repeat=total_cells):
        yield np.array(bits).reshape(size, size)

def get_unique_starting_states(size: int) -> List[np.ndarray]:
    """Get list of unique starting states, filtering out equivalents."""
    all_states = list(generate_all_states(size))
    return filter_equivalent_states(all_states) 