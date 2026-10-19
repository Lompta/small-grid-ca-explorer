from typing import List
import numpy as np
from pathlib import Path
from .bit_simulator import BitSimulator
from .rule_generator import generate_all_rules
from .state_generator import get_unique_starting_states
from .results_collector import Result, ResultsCollector
from .report_generator import generate_markdown_report

def find_longest_runs_bit(size: int, max_steps: int = 1000) -> List[Result]:
    """
    Bit-based version of find_longest_runs.
    Should produce identical results but faster.
    """
    collector = ResultsCollector()
    bit_sim = BitSimulator(size)
    
    # Get unique starting states
    unique_states = get_unique_starting_states(size)
    total_states = len(unique_states)
    print(f"Reduced from {2 ** (size * size)} to {total_states} unique starting states")
    total_rules = sum(1 for _ in generate_all_rules())
    print(f"Testing {total_rules} rules against {total_states} states ({total_rules * total_states} total configurations)")
    
    for rule_idx, rule in enumerate(generate_all_rules(), 1):
        print(f"\rTesting rule {rule_idx}/{total_rules} ({rule.birth_conditions.tolist()})", end="")
        for initial_state in unique_states:
            # Convert numpy array to bit representation
            bit_state = bit_sim.grid.to_int(initial_state)
            
            # Simulate using bit engine
            unique_states_count, cycle_length = bit_sim.simulate_rule(
                set(rule.birth_conditions.tolist()), 
                bit_state, 
                max_steps
            )
            
            # Create result object matching original format
            result = Result(
                rule_conditions=rule.birth_conditions.tolist(),
                initial_state=initial_state,
                unique_states=unique_states_count,
                cycle_length=cycle_length
            )
            collector.add_result(result)
            
    print()  # New line after progress indicator
    return collector.get_longest_runs()

if __name__ == "__main__":
    # Test with 3x3 first
    results = find_longest_runs_bit(3)
    generate_markdown_report(results, "results/3x3_results_bit.md")
    
    # Then 4x4
    results = find_longest_runs_bit(4)
    generate_markdown_report(results, "results/4x4_results_bit.md")

    # Leeeroyyy Jenkinsssss
    print("\nAttempting 5x5 grid - this could take several hours!")
    results = find_longest_runs_bit(5) 
    generate_markdown_report(results, "results/5x5_results_bit.md")