from dataclasses import dataclass
from typing import List, Dict, Set
import numpy as np
from .rule import Rule

@dataclass
class Result:
    """Stores the result of a single simulation run."""
    rule_conditions: List[int]
    initial_state: np.ndarray
    unique_states: int
    cycle_length: int

class ResultsCollector:
    """Collects and organizes simulation results."""
    
    def __init__(self):
        self.results: List[Result] = []
        self.max_unique_states = 0
    
    def add_result(self, result: Result) -> None:
        """Add a new result and update max_unique_states if necessary."""
        self.results.append(result)
        self.max_unique_states = max(self.max_unique_states, result.unique_states)
    
    def get_longest_runs(self) -> List[Result]:
        """Return all results that achieved the maximum number of unique states."""
        return [r for r in self.results if r.unique_states == self.max_unique_states] 