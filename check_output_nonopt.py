# Similar to check_output but ONLY checks for termination
# Suitable for non_opt g16 files

import os
import sys

def check_gaussian_termination(filepath):
    """Check if the Gaussian output file has a termination issue."""
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
    
    return 'Normal termination' not in content

def main():
    # Set default directory to current working directory
    if len(sys.argv) > 2:
        print("Usage: python check_gaussian.py [directory]")
        sys.exit(1)
    
    directory = sys.argv[1] if len(sys.argv) == 2 else os.getcwd()
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    # Collect and sort files
    files = sorted([f for f in os.listdir(directory) if f.endswith('.out')])
    
    # Prepare data matrix
    results = []
    max_name_len = 0
    for filename in files:
        filepath = os.path.join(directory, filename)
        termination_issue = check_gaussian_termination(filepath)
        base_name = os.path.splitext(filename)[0]
        
        results.append((base_name, termination_issue))
        max_name_len = max(max_name_len, len(base_name))
    
    # Create formatted output
    header = f"{'Filename':<{max_name_len}}  {'Termination':<12}"
    separator = "-" * (max_name_len + 12 + 2)
    
    print(f"\nChecking files in: {directory}")
    print(header)
    print(separator)
    
    for base_name, termination_issue in results:
        line = f"{base_name:<{max_name_len}}  {'FAIL' if termination_issue else 'OK':<12}"
        print(line)

if __name__ == "__main__":
    main()
