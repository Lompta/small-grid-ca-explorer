from typing import List
import numpy as np
from pathlib import Path
from .grid import Grid
from .rule import Rule
from .simulator import Simulator, simulate_configuration
from .rule_generator import generate_all_rules
from .state_generator import generate_all_states, get_unique_starting_states
from .results_collector import Result, ResultsCollector
from .report_generator import generate_markdown_report

def find_longest_runs(size: int, max_steps: int = 1000) -> List[Result]:
    """
    Find the longest possible runs for a given grid size.
    
    Args:
        size: The width/height of the square grid
        max_steps: Maximum steps to simulate before giving up
        
    Returns:
        List of Result objects representing the longest runs found
    """
    collector = ResultsCollector()
    grid = Grid(size)
    
    # Get unique starting states first
    unique_states = get_unique_starting_states(size)
    total_states = len(unique_states)
    print(f"Reduced from {2 ** (size * size)} to {total_states} unique starting states")
    total_rules = sum(1 for _ in generate_all_rules())
    print(f"Testing {total_rules} rules against {total_states} states ({total_rules * total_states} total configurations)")
    
    for rule_idx, rule in enumerate(generate_all_rules(), 1):
        print(f"\rTesting rule {rule_idx}/{total_rules} ({rule.birth_conditions.tolist()})", end="")
        for initial_state in unique_states:
            grid.set_state(initial_state)
            result = simulate_configuration(grid, rule, max_steps)
            collector.add_result(result)
    print()  # New line after progress indicator
    
    return collector.get_longest_runs()

def main():
    results = find_longest_runs(3)
    output_path = Path(__file__).parent.parent / 'results' / '3x3_results.md'
    output_path.parent.mkdir(exist_ok=True)
    generate_markdown_report(results, str(output_path))
    print(f"Results written to {output_path}")

if __name__ == "__main__":
    main() 