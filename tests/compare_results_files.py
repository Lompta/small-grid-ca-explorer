def compare_result_files(original_file: str, bit_file: str) -> bool:
    """Compare two markdown result files for equality"""
    with open(original_file, 'r') as f1, open(bit_file, 'r') as f2:
        original = f1.read()
        bit = f2.read()
        
    if original == bit:
        print(f"Results match exactly for {original_file}")
        return True
    else:
        print(f"Results differ for {original_file}")
        # Could add more detailed comparison here
        return False

if __name__ == "__main__":
    # Compare 3x3 results
    compare_result_files("results/3x3_results.md", "results/3x3_results_bit.md")
    
    # Compare 4x4 results
    compare_result_files("results/4x4_results.md", "results/4x4_results_bit.md") 