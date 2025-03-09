import os
import numpy as np
import random
from file_handles import read_precedence, read_processing_times
from ga_algo import fitness_with_robot,  genetic_algorithm_with_precedence_and_zoning
import main

# Process each folder
def process_folder(folder_path):
    print(f"Finding best solution for folder: {os.path.basename(folder_path)}")

    o1_path = os.path.join(folder_path, 'o1.txt')
    o2_path = os.path.join(folder_path, 'o2.txt')
    z1_path = os.path.join(folder_path, 'z1.txt')
    z2_path = os.path.join(folder_path, 'z2.txt')

    main.precedence_constraints_line1 = read_precedence(o1_path)
    main.precedence_constraints_line2 = read_precedence(o2_path)
    processing_times_nt1 = read_processing_times(z1_path)
    processing_times_nt2 = read_processing_times(z2_path)

    main.tasks_nt1 = len(processing_times_nt1)
    main.tasks_nt2 = len(processing_times_nt2)
    main.total_tasks = main.tasks_nt1 + main.tasks_nt2
    main.processing_times = np.concatenate((processing_times_nt1, processing_times_nt2))
    print("\nPrecedence Constraints Line 1:", main.precedence_constraints_line1)
    print("Precedence Constraints Line 2:", main.precedence_constraints_line2)

    # Randomly permute precedence order
    main.precedence_order = np.random.permutation(np.arange(main.total_tasks, 0, -1))
    print("Random Precedence Order:", main.precedence_order)

    # Randomly assign stations to precedence values
    main.station_assignments = {prec: random.randint(0, main.number_of_stations - 1) for prec in main.precedence_order}
    print("\nStation Assignments Based on Precedence:", main.station_assignments)

    # Map precedence to task indices for both lines
    main.precedence_mapping = {value: idx for idx, value in enumerate(main.precedence_order)}

    # Run the Genetic Algorithm
    best_solution = genetic_algorithm_with_precedence_and_zoning(
        pop_size=10, generations=50,
        precedence_constraints_line1=main.precedence_constraints_line1,
        precedence_constraints_line2=main.precedence_constraints_line2
    )
    print("\nBest solution:", best_solution)

    cycle_time = fitness_with_robot(best_solution, main.processing_times, main.robot_density)

    def validate_solution(solution, precedence_constraints, tasks_line_start, tasks_line_end, offset=0):
        # Extract the relevant segment of the solution
        line_segment = solution[tasks_line_start:tasks_line_end]
        # Map tasks to their positions in the segment (adjust for offset if tasks start from 1)
        task_positions = {task + offset: idx for idx, task in enumerate(line_segment, start=1)}

        for task_a, task_b in precedence_constraints:
            # Ensure both tasks are part of the current line
            if task_a in task_positions and task_b in task_positions:
                # Check precedence relationship
                if task_positions[task_a] > task_positions[task_b]:
                    print(f"Precedence violated: Task {task_a} should come before Task {task_b}\n")
                    return False
        return True

    #zoning percentage function
    def zoning_check(task_a, task_b):
        # Check precedence to determine positive or negative zoning
        for constraint in main.precedence_constraints_line1 + main.precedence_constraints_line2:
            if constraint == (task_a, task_b) or constraint == (task_b, task_a):
                return True  # Positive zoning
        return False  # Negative zoning

    # Calculate Zoning Satisfaction Percentage
    positive_zoning = 0
    negative_zoning = 0
    total_zoning = 0
    for i in range(len(best_solution)):
      for j in range(i + 1, len(best_solution)):
        task_a, task_b = best_solution[i], best_solution[j]
        if zoning_check(task_a, task_b):  # Check zoning constraints
            positive_zoning += 1
        else:
            negative_zoning += 1

    total_zoning = positive_zoning + negative_zoning

    total_tasks_checked = main.total_tasks * (main.total_tasks - 1) // 2
    positive_zoning_percentage = (positive_zoning / total_tasks_checked) * 100
    negative_zoning_percentage = (negative_zoning / total_tasks_checked) * 100

    print("Cycle time:", cycle_time)
    print("Positive Zoning Satisfaction Percentage:", positive_zoning_percentage)
    print("Negative Zoning Satisfaction Percentage:", negative_zoning_percentage)

     # Save results for graphing
    main.folder_results.append({
        'folder': os.path.basename(folder_path),
        'cycle_time': cycle_time,
        'positive_zoning_percentage': positive_zoning_percentage,
        'negative_zoning_percentage': negative_zoning_percentage,
        'task_assignments': [
            {'task': i + 1, 'start': sum(main.processing_times[:i]), 'duration': main.processing_times[i],
             'station': best_solution[i]} for i in range(main.total_tasks)
        ]
    })

    # Validate Line 1
    line1_respects = validate_solution(solution=best_solution,
                                      precedence_constraints=main.precedence_constraints_line1,
                                      tasks_line_start=0, tasks_line_end=9,
                                      offset=0)

    # Validate Line 2
    line2_respects = validate_solution(solution=best_solution,
                                      precedence_constraints=main.precedence_constraints_line2,
                                      tasks_line_start=9, tasks_line_end=17,
                                      offset=9)

    if line1_respects and line2_respects:
        print("Solution respects all precedence constraints.\n")
        print("------------------------------------------------")
    else:
        print("Solution violates precedence constraints.\n")
        print("------------------------------------------------")