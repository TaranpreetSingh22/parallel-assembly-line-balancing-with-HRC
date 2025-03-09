import os

# Global Variables
tasks_nt1 = 0
tasks_nt2 = 0
total_tasks = 0
processing_times = None
precedence_order = None
precedence_mapping = None
station_assignments = None
precedence_line1 = None
precedence_line2 = None
number_of_stations = 3
folder_results = []
robot_density = [0, 1, 1]  # 0 indicates no robot, 1 indicates robot present

# Main function
def main(zip_file, extract_to):
    from process_each_folder import process_folder
    from file_handles import extract_zip
    from generate_graphs import generate_graphs

    extract_zip(zip_file, extract_to)
    for folder_name in os.listdir(extract_to):
        folder_path = os.path.join(extract_to, folder_name)
        if os.path.isdir(folder_path):
            process_folder(folder_path)

# Generate graphs after processing all folders
    generate_graphs()


# Run the script
if __name__ == "__main__":
    zip_file = "./PALBP_DATASET/PALBP_DATASET/small/PALBP-data-sets.zip"  # Path to the ZIP file
    extract_to = "./PALBP_DATASET/PALBP_DATASET/small/PALBP-data-sets"  # Directory to extract to
    main(zip_file, extract_to)