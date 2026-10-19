from typing import List, Tuple, Set
import numpy as np

class Grid:
    """Represents a toroidal cellular automaton grid."""
    
    def __init__(self, size: int):
        """
        Initialize a square grid of given size.
        
        Args:
            size: The width/height of the square grid
        """
        self.size = size
        self.state = np.zeros((size, size), dtype=np.int8)
    
    def set_state(self, state: np.ndarray) -> None:
        """Set the grid state from a numpy array."""
        if state.shape != (self.size, self.size):
            raise ValueError(f"State must be {self.size}x{self.size}")
        self.state = state.astype(np.int8)
    
    def get_neighbor_count(self) -> np.ndarray:
        """
        Calculate the number of live neighbors for each cell.
        Returns a size x size array of neighbor counts.
        """
        counts = np.zeros_like(self.state)
        
        # For each cell (x,y), we need to check:
        # (x-1,y-1), (x-1,y), (x-1,y+1)
        # (x,y-1),             (x,y+1)
        # (x+1,y-1), (x+1,y), (x+1,y+1)
        
        for i in range(self.size):
            for j in range(self.size):
                # Check all 8 neighbors with proper wraparound
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        # Careful wraparound using modulo
                        ni = (i + di) % self.size
                        nj = (j + dj) % self.size
                        counts[i, j] += self.state[ni, nj]
        
        return counts 