import os
import json

def combine_json_files(folder_path, output_file):
    combined_data = {"unique_inputs": [], "unique_functions": []}
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                # Merge individual data items
                for key in data:
                    if key.startswith("unique_"):
                        # Update unique_inputs and unique_functions lists
                        if key == "unique_inputs":
                            combined_data["unique_inputs"] = list(set(combined_data["unique_inputs"] + data[key]))
                        elif key == "unique_functions":
                            combined_data["unique_functions"] = list(set(combined_data["unique_functions"] + data[key]))
                    else:
                        # Merge question data
                        combined_data[key] = data[key]
    
    # Save the combined data to a new JSON file
    with open(output_file, 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)

# Define paths relative to current directory
current_dir = os.path.dirname(__file__)
folder_path = os.path.join(current_dir, '..')
output_file = os.path.join(current_dir, '..', 'combined.json')

# Combine JSON files
combine_json_files(folder_path, output_file)
