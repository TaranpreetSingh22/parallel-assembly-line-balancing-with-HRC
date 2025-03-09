import zipfile
import numpy as np
import main

# Extract the ZIP file
def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def read_precedence(file_path):
    precedence_constraints = []
    with open(file_path, 'r') as f:
        for line in f:
            # Strip whitespace and split the line
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            parts = line.split()
            if len(parts) != 2:
                print(f"Skipping invalid line in {file_path}: {line}")
                continue
            try:
                task_a = int(parts[0].strip('"').strip("'"))
                task_b = int(parts[1].strip('"').strip("'"))
                precedence_constraints.append((task_a, task_b))
            except ValueError as e:
                print(f"Error parsing line in {file_path}: {line} - {e}")
    return precedence_constraints

def read_processing_times(file_path):
    with open(file_path, 'r') as f:
        processing_times = []
        for line in f:
            # Strip unwanted characters like quotes, whitespace, or newline
            clean_line = line.strip().strip('"').strip("'")
            try:
                processing_times.append(int(clean_line))
            except ValueError as e:
                print(f"Error parsing line in {file_path}: {line} - {e}")
        return processing_times

# Assign tasks to stations based on precedence-matching rule
def assign_tasks_by_precedence():
    assignment = np.zeros(main.total_tasks, dtype=int)
    for precedence_value in main.precedence_order:
        task_idx = main.precedence_mapping[precedence_value]
        station = main.station_assignments[precedence_value]
        assignment[task_idx] = station  # Assign task to the station
    return assignment

# Function to check if a solution respects precedence constraints for both lines
def respects_precedence(solution, precedence_constraints, tasks_line_start, tasks_line_end):
    # Extract the relevant segment of the solution
    line_segment = solution[tasks_line_start:tasks_line_end]
    # Map tasks to their positions in the segment
    task_positions = {task: idx for idx, task in enumerate(line_segment)}

    for task_a, task_b in precedence_constraints:
        # Check if both tasks exist in the current line segment
        if task_a in task_positions and task_b in task_positions:
            # Ensure task_a appears before task_b
            if task_positions[task_a] > task_positions[task_b]:
                return False  # Precedence violated
    return True