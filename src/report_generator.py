from typing import List
import numpy as np
from pathlib import Path
from .results_collector import Result

def state_to_markdown(state: np.ndarray) -> str:
    """Convert a grid state to a markdown-friendly string."""
    rows = []
    for row in state:
        rows.append(''.join(['⬜' if cell else '⬛' for cell in row]))
    return '\n'.join(rows)

def generate_markdown_report(results: List[Result], output_path: str) -> None:
    """
    Generate a markdown report of the results.
    
    Args:
        results: List of Result objects representing the longest runs
        output_path: Where to save the markdown file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('# Cellular Automata Analysis Results\n\n')
        f.write(f'Found {len(results)} configuration(s) with maximum unique states of {results[0].unique_states}\n\n')
        
        for i, result in enumerate(results, 1):
            f.write(f'## Configuration {i}\n\n')
            f.write(f'### Rule\n')
            f.write(f'Birth conditions: {result.rule_conditions}\n\n')
            f.write(f'### Initial State\n')
            f.write('```\n')
            f.write(state_to_markdown(result.initial_state))
            f.write('\n```\n\n')
            f.write(f'Unique states: {result.unique_states}\n')
            f.write(f'Cycle length: {result.cycle_length}\n\n')
            f.write('---\n\n') 