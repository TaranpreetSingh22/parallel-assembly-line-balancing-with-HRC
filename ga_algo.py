import numpy as np
import random
from file_handles import read_precedence, read_processing_times, assign_tasks_by_precedence, respects_precedence
import main

# Fitness function: calculate cycle time considering worker and robot constraints
def fitness_with_robot(individual, processing_times, robot_density):
    station_loads = np.zeros(main.number_of_stations)

    for task in range(len(individual)):
        station = individual[task]
        station_loads[station] += processing_times[task]

    # Apply the cycle time rules based on station type
    adjusted_station_loads = np.zeros_like(station_loads)
    for i, load in enumerate(station_loads):
        if robot_density[i] == 0:  # Worker-only
            adjusted_station_loads[i] = load
        else:  # Mixed (Worker and Robot)
            adjusted_station_loads[i] = 0.7 * load

    return max(adjusted_station_loads)  # Minimize the maximum cycle time

# Ensure initial population respects precedence
def initialize_population_with_precedence(pop_size, initial_assignment, precedence_constraints_line1, precedence_constraints_line2):
    population = []
    for _ in range(pop_size):
        while True:
            individual = initial_assignment.copy()
            np.random.shuffle(individual[:main.tasks_nt1])  # Shuffle Line 1
            np.random.shuffle(individual[main.tasks_nt1:])  # Shuffle Line 2
            if (respects_precedence(individual, precedence_constraints_line1, 0, main.tasks_nt1) and
                    respects_precedence(individual, precedence_constraints_line2, main.tasks_nt1, main.total_tasks)):
                population.append(individual)
                break
    return np.array(population)

# Tournament selection
def tournament_selection(population, fitness_scores, tournament_size=3):
    selected = []
    for _ in range(len(population)):
        competitors = random.sample(list(enumerate(fitness_scores)), tournament_size)
        winner = min(competitors, key=lambda x: x[1])[0]
        selected.append(population[winner])
    return np.array(selected)

# Crossover function
def single_point_crossover_with_precedence(parent1, parent2, precedence_constraints_line1, precedence_constraints_line2):
    point = random.randint(1, len(parent1) - 1)
    offspring1 = np.concatenate((parent1[:point], parent2[point:]))
    offspring2 = np.concatenate((parent2[:point], parent1[point:]))

    if (not respects_precedence(offspring1, precedence_constraints_line1, 0, main.tasks_nt1) or
            not respects_precedence(offspring1, precedence_constraints_line2, main.tasks_nt1, main.total_tasks)):
        offspring1 = parent1.copy()
    if (not respects_precedence(offspring2, precedence_constraints_line1, 0, main.tasks_nt1) or
            not respects_precedence(offspring2, precedence_constraints_line2, main.tasks_nt1, main.total_tasks)):
        offspring2 = parent2.copy()

    return offspring1, offspring2

# Mutation function
def swap_mutation_with_precedence(individual, precedence_constraints_line1, precedence_constraints_line2):
    for _ in range(10):  # Try multiple swaps to find a valid one
        mutated = individual.copy()
        idx1, idx2 = random.sample(range(len(mutated)), 2)
        mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]
        if (respects_precedence(mutated, precedence_constraints_line1, 0, main.tasks_nt1) and
                respects_precedence(mutated, precedence_constraints_line2, main.tasks_nt1, main.total_tasks)):
            return mutated
    return individual  # Return original if no valid mutation found

# Apply zoning constraints after crossover and mutation
def apply_zoning_constraints(population, precedence_constraints_line1, precedence_constraints_line2):
    def zoning_check(task_a, task_b):
        # Check precedence to determine positive or negative zoning
        for constraint in precedence_constraints_line1 + precedence_constraints_line2:
            if constraint == (task_a, task_b) or constraint == (task_b, task_a):
                return True  # Positive zoning
        return False  # Negative zoning

    for individual in population:
        for i in range(len(individual) - 1):
            for j in range(i + 1, len(individual)):
                if individual[i] // main.tasks_nt1 == individual[j] // main.tasks_nt1:  # Same line check
                    if not zoning_check(individual[i], individual[j]):
                        # Repair the solution by swapping
                        individual[i], individual[j] = individual[j], individual[i]
    return population

# Elitism selection: Survivors
def elitism_selection(population, fitness_scores, elite_size=2):
    elites = np.argsort(fitness_scores)[:elite_size]
    return population[elites]

# Genetic Algorithm
def genetic_algorithm_with_precedence_and_zoning(pop_size, generations, precedence_constraints_line1, precedence_constraints_line2):
    initial_assignment = assign_tasks_by_precedence()
    population = initialize_population_with_precedence(pop_size, initial_assignment, precedence_constraints_line1, precedence_constraints_line2)

    for generation in range(generations):
        fitness_scores = np.array([fitness_with_robot(individual, main.processing_times, main.robot_density) for individual in population])

        # Selection using tournament
        selected = tournament_selection(population, fitness_scores)

        # Generate next generation with precedence-respecting crossover
        next_generation = []
        for i in range(0, len(selected), 2):
            parent1 = selected[i]
            parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
            offspring1, offspring2 = single_point_crossover_with_precedence(
                parent1, parent2, precedence_constraints_line1, precedence_constraints_line2)
            next_generation.append(offspring1)
            next_generation.append(offspring2)

        # Mutation with precedence-respecting mutation
        for individual in next_generation:
            if random.random() < 0.2:
                individual[:] = swap_mutation_with_precedence(
                    individual, precedence_constraints_line1, precedence_constraints_line2)

        # Apply zoning constraints
        next_generation = apply_zoning_constraints(next_generation, precedence_constraints_line1, precedence_constraints_line2)

        # Apply elitism
        elites = elitism_selection(population, fitness_scores)
        next_generation = np.array(next_generation)
        next_generation[:len(elites)] = elites

        # Update population
        population = next_generation

    # Get the best solution
    best_index = np.argmin([fitness_with_robot(individual, main.processing_times, main.robot_density) for individual in population])
    return population[best_index]