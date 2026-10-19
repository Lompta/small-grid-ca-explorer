import time
from typing import Callable
import numpy as np
from src.find_longest_runs import find_longest_runs
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
    
    # Time original implementation
    print("Original implementation:")
    orig_time, orig_results = time_function(find_longest_runs, size)
    print(f"Time: {orig_time:.2f} seconds")
    print(f"Found {len(orig_results)} configurations")
    
    # Time bit implementation
    print("\nBit implementation:")
    bit_time, bit_results = time_function(find_longest_runs_bit, size)
    print(f"Time: {bit_time:.2f} seconds")
    print(f"Found {len(bit_results)} configurations")
    
    # Compare results
    print("\nResults comparison:")
    print(f"Speed improvement: {orig_time/bit_time:.1f}x faster")
    print(f"Same number of results: {len(orig_results) == len(bit_results)}")
    
    # Memory usage (if psutil is available)
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"\nMemory usage: {memory_mb:.1f} MB")
    except ImportError:
        pass

if __name__ == "__main__":
    # Run benchmarks for both sizes
    run_benchmark(3)
    run_benchmark(4)
    
    print("\nPotential 5x5 estimate:")
    # Estimate 5x5 time based on scaling factor from 4x4
    states_4x4 = 2**(4*4)  # 65,536
    states_5x5 = 2**(5*5)  # 33,554,432
    scaling_factor = states_5x5 / states_4x4
    print(f"Estimated states to check: {states_5x5:,}")
    print(f"Scaling factor from 4x4: {scaling_factor:.1f}x") 