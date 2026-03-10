import os
import json

def combine_json_files(folder_path, output_file):
    combined_data = {
        "queries": [],
        "unique_inputs": set(),
        "unique_functions": set(),
        "questions": []
    }

    event_types = set()
    metric_types = set()
    metric_names = set()

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                # Combine queries
                combined_data["queries"].extend(data.get("queries", []))
                
                # Extract unique inputs and their values
                for query in data.get("queries", []):
                    inputs = query.get("inputs", {})
                    combined_data["unique_inputs"].update(inputs.keys())
                    
                    # Extract specific values
                    if "eventType" in inputs:
                        event_types.add(inputs["eventType"])
                    if "metricType" in inputs:
                        metric_types.add(inputs["metricType"])
                    if "metricName" in inputs:
                        metric_names.add(inputs["metricName"])

                    combined_data["unique_functions"].add(query.get("function", ""))
                    combined_data["questions"].append(query.get("question", ""))

    # Convert sets to lists
    combined_data["unique_inputs"] = list(combined_data["unique_inputs"])
    combined_data["unique_functions"] = list(combined_data["unique_functions"])

    # Include the values of eventType, metricType, and metricName
    combined_data["unique_event_types"] = list(event_types)
    combined_data["unique_metric_types"] = list(metric_types)
    combined_data["unique_metric_names"] = list(metric_names)

    # Save the combined data to a new JSON file
    with open(output_file, 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)

# Define paths relative to current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(current_dir, '..', 'raw')
output_file = os.path.join(current_dir, '..', 'combined/combined.json')

# Combine JSON files
combine_json_files(folder_path, output_file)
