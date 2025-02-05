# This script finds information in the specified .gjf files and replace them
# Specially useful to create .gjf files in tandem
# List as many replacements as needed

import os
import sys
from pathlib import Path

# Check if a directory argument is provided
if len(sys.argv) > 1:
    directory = Path(sys.argv[1]).resolve()
else:
    directory = Path(__file__).parent  # Default to the script's directory

output_directory = directory  # Set output to the same directory by default

# Dictionary of replacements
replacements = {
    '%nprocshared=32': '%nprocshared=120',
    '%mem=20GB': '%mem=40GB'
}

# Ensure the directory exists
if not directory.exists():
    print(f"Error: Directory '{directory}' does not exist.")
    sys.exit(1)

# Get all .gjf files in the directory
gjf_files = list(directory.glob('*.gjf'))

if not gjf_files:
    print(f"No .gjf files found in '{directory}'.")
    sys.exit(0)

for file_path in gjf_files:
    with file_path.open('r') as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        for old_str, new_str in replacements.items():
            line = line.replace(old_str, new_str)
        modified_lines.append(line)

    new_filename = file_path.name
    for old_str, new_str in replacements.items():
        if old_str in new_filename:
            new_filename = new_filename.replace(old_str, new_str)

    output_file = output_directory / new_filename
    with output_file.open('w') as file:
        file.writelines(modified_lines)

    print(f"Processed: {file_path.name} -> {output_file.name}")

# Ask if the user wants to delete the original files
delete_files = input("Do you want to delete the original files? (y/n): ").strip().lower()

if delete_files == 'y':
    for file_path in gjf_files:
        file_path.unlink()
        print(f"Deleted: {file_path.name}")
    print("All original files have been deleted.")
else:
    print("Original files have been kept.")

print("Processing complete.")
