import pandas as pd
import re

def parse_mps_file(file_path):
    with open(file_path, 'r', encoding='latin1') as file:  # Specify an encoding
        lines = file.readlines()

    # Initialize storage for settings and techniques
    general_settings = {}
    techniques = []
    current_technique = {}

    # Regular expressions for parsing
    technique_header_re = re.compile(r'^Technique\s+:\s+(\d+)')
    key_value_re = re.compile(r'^(\S.*?)\s{2,}(\S.*)$')

    for line in lines:
        line = line.strip()
        print(line)

        # Detect technique headers
        technique_match = technique_header_re.match(line)
        if technique_match:
            # If we were processing a technique, save it
            if current_technique:
                techniques.append(current_technique)
                current_technique = {}
            current_technique['Technique'] = int(technique_match.group(1))
            continue

        # Parse key-value pairs
        key_value_match = key_value_re.match(line)
        if key_value_match:
            key, value = key_value_match.groups()
            value = value.replace(',', '.')  # Ensure decimal points
            # Convert numbers where possible
            try:
                value = float(value) if '.' in value else int(value)
            except ValueError:
                pass

            if 'Technique' in current_technique:
                current_technique[key] = value
            else:
                general_settings[key] = value

    # Add the last technique if any
    if current_technique:
        techniques.append(current_technique)

    # Create DataFrame for techniques
    techniques_df = pd.DataFrame(techniques)

    return general_settings, techniques_df


