from PIL import Image
import numpy as np
import os

def state_to_array(state_str):
    """Convert a state string (with ⬛ and ⬜) to a numpy array"""
    lines = state_str.strip().split('\n')
    return np.array([[1 if char == '⬜' else 0 for char in line] for line in lines])

def state_to_string(arr):
    """Convert numpy array to string representation"""
    return '\n'.join(''.join('⬜' if cell else '⬛' for cell in row) for row in arr)

def next_state(current, birth_conditions):
    """Calculate the next state of the CA"""
    height, width = current.shape
    next_arr = np.zeros_like(current)
    
    for i in range(height):
        for j in range(width):
            # Count live neighbors (excluding cell itself)
            neighbors = 0
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue  # Skip the cell itself
                    ni, nj = (i + di) % height, (j + dj) % width
                    neighbors += current[ni, nj]
            
            # Apply birth rule
            next_arr[i,j] = 1 if neighbors in birth_conditions else 0
            
    return next_arr

def generate_sequence_md(initial_state, birth_conditions, output_path, max_steps=1000):
    """Generate markdown file showing CA evolution until first repeat"""
    current = state_to_array(initial_state)
    seen_states = {}
    states_list = []
    
    step = 0
    while step < max_steps:
        state_str = state_to_string(current)
        if state_str in seen_states:
            cycle_start = seen_states[state_str]
            cycle_length = step - cycle_start
            break
            
        seen_states[state_str] = step
        states_list.append(state_str)
        current = next_state(current, birth_conditions)
        step += 1
    
    # Write markdown file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# CA Evolution Sequence\n\n")
        f.write(f"Birth conditions: {birth_conditions}\n\n")
        f.write(f"Total unique states: {len(seen_states)}\n")
        f.write(f"Cycle length: {cycle_length}\n\n")
        
        for i, state in enumerate(states_list):
            f.write(f"## Step {i}\n\n")
            f.write("```\n")
            f.write(state)
            f.write("\n```\n\n")
        
        # Show first repeat
        f.write(f"## Step {step} (Repeat of Step {cycle_start})\n\n")
        f.write("```\n")
        f.write(state_str)
        f.write("\n```\n")

# Example from 3x3 results (Configuration 1)
initial_3x3 = """⬛⬛⬛
⬛⬛⬜
⬜⬜⬜"""
birth_3x3 = [4, 5]

# Example from 4x4 results (Configuration 1)
initial_4x4 = """⬛⬛⬛⬛
⬛⬛⬜⬜
⬛⬜⬜⬜
⬜⬜⬜⬛"""
birth_4x4 = [1, 4]

# Example from 5x5 results (Configuration 1)
initial_5x5 = """⬛⬛⬛⬛⬛
⬛⬛⬜⬛⬜
⬛⬜⬜⬛⬛
⬜⬜⬜⬜⬛
⬜⬜⬛⬜⬜"""
birth_5x5 = [0, 3, 4, 7]

# Create sequences directory if it doesn't exist
seq_dir = "results/sequences"
os.makedirs(seq_dir, exist_ok=True)

# Generate sequence files
generate_sequence_md(initial_3x3, birth_3x3, f"{seq_dir}/sequence_3x3.md")
generate_sequence_md(initial_4x4, birth_4x4, f"{seq_dir}/sequence_4x4.md")
generate_sequence_md(initial_5x5, birth_5x5, f"{seq_dir}/sequence_5x5.md") 