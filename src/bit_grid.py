from typing import List, Set, Tuple
import numpy as np

class BitGrid:
    def __init__(self, size: int):
        self.size = size
        self.max_state = (1 << (size * size)) - 1
        
        # Precompute neighbor masks for each position
        self.neighbor_masks = {}
        for i in range(size):
            for j in range(size):
                mask = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx = (i + dx) % size
                        ny = (j + dy) % size
                        mask |= 1 << (nx * size + ny)
                self.neighbor_masks[i * size + j] = mask
        
        # Precompute birth condition lookup
        self.birth_lookups = {}  # Cache for birth condition lookups
        
        # Precompute rotation and reflection patterns
        self.rotation_patterns = []  # For each position, where does it go after rotation
        self.reflection_patterns = []  # For each position, where does it go after reflection
        for i in range(size):
            for j in range(size):
                # Rotation: (i,j) -> (j,n-1-i)
                self.rotation_patterns.append(
                    (i * size + j, j * size + (size - 1 - i))
                )
                # Reflection: (i,j) -> (i,n-1-j)
                self.reflection_patterns.append(
                    (i * size + j, i * size + (size - 1 - j))
                )

    def to_int(self, grid: np.ndarray) -> int:
        """Convert numpy grid to integer representation"""
        state = 0
        for i in range(self.size):
            for j in range(self.size):
                if grid[i, j] == 1:  # Changed to match numpy array access
                    state |= 1 << (i * self.size + j)
        return state
    
    def to_grid(self, state: int) -> np.ndarray:
        """Convert integer representation back to numpy grid"""
        grid = np.zeros((self.size, self.size), dtype=int)  # Changed to numpy array
        for i in range(self.size):
            for j in range(self.size):
                if state & (1 << (i * self.size + j)):
                    grid[i, j] = 1
        return grid
    
    def count_neighbors(self, state: int, x: int, y: int) -> int:
        """Count live neighbors using precomputed masks"""
        return bin(state & self.neighbor_masks[x * self.size + y]).count('1')
    
    def get_birth_lookup(self, birth_conditions: Set[int]) -> int:
        """Convert birth conditions to a fast lookup bitmap"""
        # Cache the lookup to avoid recomputing
        key = tuple(sorted(birth_conditions))
        if key not in self.birth_lookups:
            self.birth_lookups[key] = sum(1 << i for i in birth_conditions)
        return self.birth_lookups[key]
    
    def next_state(self, state: int, birth_conditions: Set[int]) -> int:
        """Compute next state using optimized bit operations"""
        new_state = 0
        birth_lookup = self.get_birth_lookup(birth_conditions)
        
        for i in range(self.size):
            for j in range(self.size):
                neighbors = self.count_neighbors(state, i, j)
                # Use fast bitwise lookup instead of 'in' operation
                if (birth_lookup >> neighbors) & 1:
                    new_state |= 1 << (i * self.size + j)
        
        return new_state

    def get_canonical_form(self, state: int) -> int:
        """Optimized canonical form calculation"""
        if state == 0 or state == self.max_state:
            return state  # All zeros or ones - no need to check transformations
        
        min_form = state
        current = state
        
        # Check rotations first (often finds min form quickly)
        for _ in range(3):  # Only need 3 more rotations
            current = self.rotate_90(current)
            if current < min_form:
                min_form = current
            
        # If we found a smaller form, reflect that one
        reflected = self.reflect_horizontal(min_form)
        if reflected < min_form:
            min_form = reflected
            # Check rotations of reflection
            current = reflected
            for _ in range(3):
                current = self.rotate_90(current)
                if current < min_form:
                    min_form = current
                
        return min_form
    
    def rotate_90(self, state: int) -> int:
        """Faster rotation using precomputed patterns"""
        new_state = 0
        for src, dst in self.rotation_patterns:
            if state & (1 << src):
                new_state |= 1 << dst
        return new_state
    
    def reflect_horizontal(self, state: int) -> int:
        """Faster reflection using precomputed patterns"""
        new_state = 0
        for src, dst in self.reflection_patterns:
            if state & (1 << src):
                new_state |= 1 << dst
        return new_state 