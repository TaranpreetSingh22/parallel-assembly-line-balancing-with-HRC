import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from main import folder_results

def generate_graphs():
    # Extract data
    folders = [result['folder'] for result in folder_results]
    cycle_times = [result['cycle_time'] for result in folder_results]
    positive_zoning_percentages = [result['positive_zoning_percentage'] for result in folder_results]
    negative_zoning_percentages = [result['negative_zoning_percentage'] for result in folder_results]

    # Bar Chart: Cycle Time
    plt.figure(figsize=(10, 5))
    plt.bar(folders, cycle_times, color='skyblue')
    plt.xlabel('Folders')
    plt.ylabel('Cycle Time')
    plt.title('Cycle Time for Each Folder')
    plt.show()

    # Line Graph: Cycle Time
    plt.figure(figsize=(10, 5))
    plt.plot(folders, cycle_times, marker='o', linestyle='-', color='blue', label='Cycle Time')
    plt.xlabel('Folders')
    plt.ylabel('Cycle Time')
    plt.title('Cycle Time Trend Across Folders')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Bar Chart: Zoning Constraint Satisfaction
    x = np.arange(len(folders))
    bar_width = 0.35
    plt.figure(figsize=(12, 6))
    plt.bar(x - bar_width / 2, positive_zoning_percentages, width=bar_width, label='Positive Zoning %', color='lightgreen')
    plt.bar(x + bar_width / 2, negative_zoning_percentages, width=bar_width, label='Negative Zoning %', color='salmon')
    plt.xlabel('Folders')
    plt.ylabel('Zoning Constraint Percentage')
    plt.title('Zoning Constraint Satisfaction for Each Folder')
    plt.xticks(x, folders, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Line Graph: Zoning Constraint Satisfaction
    plt.figure(figsize=(10, 5))
    plt.plot(folders, positive_zoning_percentages, marker='o', linestyle='-', color='green', label='Positive Zoning %')
    plt.plot(folders, negative_zoning_percentages, marker='o', linestyle='--', color='red', label='Negative Zoning %')
    plt.xlabel('Folders')
    plt.ylabel('Zoning Constraint Percentage')
    plt.title('Zoning Constraint Trends Across Folders')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Gantt Chart: Task Assignments
    for result in folder_results:
        tasks = result['task_assignments']
        fig, ax = plt.subplots(figsize=(12, 6))

        station_labels = []
        station_indices = []

        # Collect stations and labels
        for task in tasks:
            station = task['station']
            if station not in station_labels:
                station_labels.append(station)
                station_indices.append(len(station_labels) - 1)

            ax.barh(
                station_labels.index(station),
                task['duration'],
                left=task['start'],
                color=f"C{station % 10}",
                edgecolor='black',
                label=f"Task {task['task']}" if f"Task {task['task']}" not in ax.get_legend_handles_labels()[1] else None
            )

        # Set custom y-ticks for station names
        ax.set_yticks(range(len(station_labels)))
        ax.set_yticklabels([f"Station {station}" for station in station_labels])

        # Add horizontal grid lines for separation
        for y in range(len(station_labels)):
            ax.axhline(y=y - 0.5, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)

        # Customize the grid for x-axis (time)
        ax.grid(True, axis='x', linestyle='--', linewidth=0.5, alpha=0.7)  # Only x-axis gridlines
        ax.set_axisbelow(True)  # Ensure gridlines are behind bars

        # Chart labels and title
        ax.set_xlabel('Time')
        ax.set_ylabel('Stations')
        ax.set_title(f"Gantt Chart: {result['folder']}")

        plt.tight_layout()
        plt.show()

    # Pie chart for Cycle Times
    plt.figure(figsize=(6, 6))
    plt.pie(cycle_times, labels=folders, autopct='%1.1f%%', startangle=140)
    plt.title("Cycle Time Distribution")
    plt.show()

    # Pie chart for Zoning Compliance
    plt.figure(figsize=(6, 6))
    plt.pie([sum(positive_zoning_percentages), sum(negative_zoning_percentages)],
          labels=['Total Positive Zoning', 'Total Negative Zoning'],
          autopct='%1.1f%%', colors=['green', 'red'], startangle=140)
    plt.title("Zoning Compliance Percentage")
    plt.show()

    # Pie chart for positive Zoning Compliance
    plt.figure(figsize=(6, 6))
    plt.pie(positive_zoning_percentages, labels=folders,
          autopct='%1.1f%%',startangle=140)
    plt.title("Positive Zoning Compliance Percentages")
    plt.show()

    # Pie chart for negative Zoning Compliance
    plt.figure(figsize=(6, 6))
    plt.pie(negative_zoning_percentages, labels=folders,
          autopct='%1.1f%%',startangle=140)
    plt.title("negative Zoning Compliance Percentages")
    plt.show()


    #table for comparison
    df = pd.DataFrame({
        "Dataset Names": folders,
        "Cycle Time": cycle_times,
        "Positive Zoning %": positive_zoning_percentages,
        "Negative Zoning %": negative_zoning_percentages
    })
    print(df.to_string(index=False))