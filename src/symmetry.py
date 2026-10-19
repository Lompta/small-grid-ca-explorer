import numpy as np
from typing import List

def get_unique_rotations(state: np.ndarray) -> List[np.ndarray]:
    """
    Get all unique rotations of a grid state.
    
    Args:
        state: 2D numpy array representing the grid state
        
    Returns:
        List of unique rotated states
    """
    rotations = []
    current = state.copy()
    
    for _ in range(4):
        rotations.append(current.copy())
        current = np.rot90(current)
    
    return list(set(state.tobytes() for state in rotations))

def get_reflections(state: np.ndarray) -> List[np.ndarray]:
    """
    Get all unique reflections of a grid state.
    
    Args:
        state: 2D numpy array representing the grid state
        
    Returns:
        List of unique reflected states
    """
    reflections = [
        state,
        np.fliplr(state),
        np.flipud(state),
        np.flipud(np.fliplr(state))
    ]
    
    return list(set(state.tobytes() for state in reflections)) 