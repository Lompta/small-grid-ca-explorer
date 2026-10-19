from typing import List
import numpy as np

class Rule:
    """Represents a cellular automaton rule."""
    
    def __init__(self, birth_conditions: List[int]):
        """
        Initialize a rule from a list of neighbor counts that result in a live cell.
        
        Args:
            birth_conditions: List of integers 0-8 indicating when a cell becomes/stays alive
        """
        if not all(0 <= x <= 8 for x in birth_conditions):
            raise ValueError("Birth conditions must be integers 0-8")
        self.birth_conditions = np.array(birth_conditions, dtype=np.int8)
        
    def apply(self, neighbor_counts: np.ndarray) -> np.ndarray:
        """
        Apply the rule to an array of neighbor counts.
        Returns a boolean array of the same shape.
        """
        return np.isin(neighbor_counts, self.birth_conditions).astype(np.int8) 