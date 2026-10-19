import time
from typing import Callable
import numpy as np
from src.find_longest_runs_bit import find_longest_runs_bit

def time_function(func: Callable, *args, **kwargs) -> tuple[float, any]:
    """Run a function and return its execution time and result"""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return end - start, result

def run_benchmark(size: int):
    print(f"\nBenchmarking {size}x{size} grid:")
    print("-" * 40)
    
    bit_time, bit_results = time_function(find_longest_runs_bit, size)
    print(f"Time: {bit_time:.2f} seconds")
    print(f"Found {len(bit_results)} configurations")
    
    # Memory usage
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"Memory usage: {memory_mb:.1f} MB")
    except ImportError:
        pass
    
    return bit_time  # Return time for scaling calculations

if __name__ == "__main__":
    time_4x4 = run_benchmark(4)
    
    print("\nPotential 5x5 estimate:")
    states_4x4 = 2**(4*4)  # 65,536
    states_5x5 = 2**(5*5)  # 33,554,432
    scaling_factor = states_5x5 / states_4x4
    estimated_5x5_time = time_4x4 * scaling_factor
    
    print(f"4x4 took: {time_4x4:.2f} seconds")
    print(f"Estimated 5x5 time: {estimated_5x5_time/60:.1f} minutes")
    print(f"                   {estimated_5x5_time/3600:.1f} hours") 