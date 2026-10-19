from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def state_to_array(state_str):
    """Convert a state string (with ⬛ and ⬜) to a numpy array"""
    lines = state_str.strip().split('\n')
    return np.array([[1 if char == '⬜' else 0 for char in line] for line in lines])

def array_to_image(arr, cell_size=50, frame_num=None, repeat_info=None):
    """Convert a numpy array to a PIL Image with larger cells and optional text"""
    height, width = arr.shape
    padding = 30  # Space for frame number
    img = Image.new('RGB', (width * cell_size, height * cell_size + padding), 'black')
    draw = ImageDraw.Draw(img)
    
    # Draw light blue background for text area
    for y in range(padding):
        for x in range(width * cell_size):
            img.putpixel((x, y), (173, 216, 230))  # Light blue
    
    # Draw cells (shifted down by padding)
    for i in range(height):
        for j in range(width):
            color = 'white' if arr[i,j] else 'black'
            for x in range(cell_size):
                for y in range(cell_size):
                    img.putpixel((j * cell_size + x, i * cell_size + y + padding), 
                               (255,255,255) if color == 'white' else (0,0,0))
    
    # Add frame number at top (now with black text since background is light)
    if frame_num is not None:
        text = f"Frame {frame_num + 1}"  # Add 1 to start from Frame 1
        if repeat_info is not None:  # Check if it's not None first
            text = f"Frame {frame_num + 1} repeats Frame {int(repeat_info) + 1}"
        draw.text((10, 5), text, fill='black')
    
    return img

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

def create_ca_gif(initial_state, birth_conditions, output_path, cell_size=50):
    """Create a GIF of the CA evolution until first repeat"""
    current = state_to_array(initial_state)
    seen_states = {}
    frames = []
    
    # Generate frames until repeat
    step = 0
    while True:
        state_tuple = tuple(map(tuple, current))  # Make array hashable
        if state_tuple in seen_states:
            cycle_start = seen_states[state_tuple]
            # Create final frame with repeat information
            img = array_to_image(current, cell_size, step, cycle_start)  # Pass cycle_start directly
            frames.append(img)
            break
            
        seen_states[state_tuple] = step
        img = array_to_image(current, cell_size, step)
        frames.append(img)
        current = next_state(current, birth_conditions)
        step += 1
    
    # Save as GIF
    # Normal frames
    durations = [500] * (len(frames) - 1)
    # Last frame (repeat frame) stays longer
    durations.append(2000)
    
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0
    )

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

# Create the gif directory if it doesn't exist
gif_dir = "results/gif"
os.makedirs(gif_dir, exist_ok=True)

# Generate GIFs
create_ca_gif(initial_3x3, birth_3x3, f"{gif_dir}/ca_3x3.gif", cell_size=50)
create_ca_gif(initial_4x4, birth_4x4, f"{gif_dir}/ca_4x4.gif", cell_size=50)
create_ca_gif(initial_5x5, birth_5x5, f"{gif_dir}/ca_5x5.gif", cell_size=50) 