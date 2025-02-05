#This script automatically checks all output files in a specify directory or current directory for gaussian16 output files
#The script prints a table with all output files and shows if these files correctly terminated the calculation, converged and do not have imaginary frequencies

import os
import sys

def check_gaussian_file(filepath):
    issues = []
    
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
    lines = content.split('\n')
    
    # Check for normal termination
    if 'Normal termination' not in content:
        issues.append('termination problem')
    
    # Parse route section from first # line
    route_lines = []
    route_found = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            route_found = True
            current_line = stripped
            route_lines.append(current_line)
            # Handle continuation lines
            while current_line.endswith('\\'):
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1].strip()
                    route_lines.append(next_line)
                    current_line = next_line
                    line = lines[idx + 1]
                else:
                    break
            break  # Only process first route section
    
    route_str = ' '.join(route_lines).lower()
    is_optimization = 'opt' in route_str
    is_frequency = 'freq' in route_str

    # Enhanced convergence check for optimizations
    if is_optimization:
        # Find last convergence criteria by searching backward for "converged"
        last_conv_index = -1
        for i in reversed(range(len(lines))):
            if 'converged' in lines[i].lower():
                last_conv_index = i
                break
        
        if last_conv_index == -1:
            issues.append('convergence problem')
        else:
            # Check for stationary point after last convergence
            stationary_found = False
            for line in lines[last_conv_index:]:
                if 'Stationary point found' in line:
                    stationary_found = True
                    break
            if not stationary_found:
                issues.append('convergence problem')

    # Enhanced frequency check for imaginary frequencies
    if is_frequency:
        # Find last force constants mention
        last_fc_index = -1
        for i in reversed(range(len(lines))):
            if 'force constants' in lines[i].lower():
                last_fc_index = i
                break
        
        if last_fc_index == -1:
            issues.append('frequency problem')
        else:
            # Find next frequency listing after force constants
            freq_line = None
            for line in lines[last_fc_index:last_fc_index+20]:  # Check next 20 lines
                if line.strip().startswith('Frequencies --'):
                    freq_line = line
                    break
            
            if freq_line is None:
                issues.append('frequency problem')
            else:
                # Parse frequencies
                frequencies = []
                try:
                    freq_str = freq_line.split('--')[1]
                    frequencies = [float(x) for x in freq_str.split() if replace_chars(x).replace('.', '', 1).isdigit()]
                except:
                    pass
                
                if any(f < 0 for f in frequencies):
                    issues.append('frequency problem')

    return issues

def replace_chars(s):
    # Helper to handle negative signs in different formats
    return s.replace('−', '-').replace('–', '-').strip()

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
        issues = check_gaussian_file(filepath)
        base_name = os.path.splitext(filename)[0]
        
        status = {
            'termination': 'termination problem' in issues,
            'convergence': 'convergence problem' in issues,
            'frequency': 'frequency problem' in issues
        }
        results.append((base_name, status))
        max_name_len = max(max_name_len, len(base_name))

    # Create formatted output
    header = f"{'Filename':<{max_name_len}}  {'Termination':<12}  {'Convergence':<12}  {'Frequency':<12}"
    separator = "-" * (max_name_len + 12*3 + 6)
    
    print(f"\nChecking files in: {directory}")
    print(header)
    print(separator)
    
    for base_name, status in results:
        line = (
            f"{base_name:<{max_name_len}}  "
            f"{'FAIL' if status['termination'] else 'OK':<12}  "
            f"{'FAIL' if status['convergence'] else 'OK':<12}  "
            f"{'FAIL' if status['frequency'] else 'OK':<12}"
        )
        print(line)

if __name__ == "__main__":
    main()
