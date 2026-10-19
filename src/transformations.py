import numpy as np
from typing import Set, List

def get_all_transformations(state: np.ndarray) -> Set[bytes]:
    """
    Get all equivalent states through rotations, reflections, translations, and inversions.
    Returns them as bytes for easy comparison/storage in set.
    """
    equivalents = set()
    n = len(state)
    
    # Get base transformations of the original state
    rotated = state.copy()
    for _ in range(4):  # 4 rotations (including original)
        rotated = np.rot90(rotated)
        
        # For each rotation, get reflections
        flipped_h = np.fliplr(rotated)
        flipped_v = np.flipud(rotated)
        
        # For each of these variants, get all possible translations
        for variant in [rotated, flipped_h, flipped_v]:
            for i in range(n):  # vertical shifts
                shifted_v = np.roll(variant, i, axis=0)
                for j in range(n):  # horizontal shifts
                    shifted = np.roll(shifted_v, j, axis=1)
                    equivalents.add(shifted.tobytes())
                    # Also add the inverted version (1s become 0s and vice versa)
                    equivalents.add((1 - shifted).tobytes())
    
    return equivalents

def filter_equivalent_states(states: List[np.ndarray]) -> List[np.ndarray]:
    """
    Filter a list of states to remove equivalent configurations.
    Returns one representative from each equivalence class.
    """
    seen = set()
    unique_states = []
    
    for state in states:
        # If we haven't seen this state or any of its transformations
        if state.tobytes() not in seen:
            # Add this state and all its transformations to seen
            seen.update(get_all_transformations(state))
            # Keep this state as the representative of its class
            unique_states.append(state)
    
    return unique_states 