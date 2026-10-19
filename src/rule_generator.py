from typing import List, Iterator
import itertools
from .rule import Rule

def generate_all_rules() -> Iterator[Rule]:
    """
    Generate all possible rules (all possible combinations of 0-8 neighbors).
    
    Yields:
        Rule objects for each possible combination
    """
    # Generate all possible combinations of True/False for each neighbor count
    for rule_bits in itertools.product([0, 1], repeat=9):
        # Convert to list of indices where True
        birth_conditions = [i for i, bit in enumerate(rule_bits) if bit]
        yield Rule(birth_conditions) 