import os
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta

# Define folder paths
source_folder = "./"
unique_folder = "UniqueFiles"
converted_folder = "ConvertedFiles"
log_file = "conversion_log.txt"

# Ensure output directories exist
os.makedirs(unique_folder, exist_ok=True)
os.makedirs(converted_folder, exist_ok=True)

def extract_activity_id(filename):
    """Extract the unique activity ID based on date and time (ignoring the last 3 digits)."""
    # Match filenames like HiTrack_20230121_132330_001.tcx or HiTrack_20230121_132330_1234.tcx
    match = re.match(r"HiTrack_(\d{8}_\d{6})_\d{3,4}\.tcx", filename)
    return match.group(1) if match else None

def locate_unique_files():
    """Identify unique activity files and copy one of each to UniqueFiles."""
    seen_activities = {}
    all_files = list(Path(source_folder).glob("HiTrack_*.tcx"))
    print(f"Total files in source folder: {len(all_files)}")  # Print the total number of files before filtering

    for file in all_files:
        # Extract the unique activity ID based on the date and time (ignore last 3 digits)
        activity_id = extract_activity_id(file.name)
        
        if activity_id:
            # Print out the extracted activity ID to debug
            print(f"Activity ID extracted: {activity_id} from {file.name}")
            
            # Only keep the first file for each unique activity_id (ignoring the last 3 digits)
            if activity_id not in seen_activities:
                seen_activities[activity_id] = file.name
                shutil.copy(file, os.path.join(unique_folder, file.name))
    
    print(f"Unique files found: {len(seen_activities)}")  # Print the number of unique activities
    return seen_activities

def fix_timezone_format(match):
    """Correct the timezone format from +0800 to +08:00 and adjust time accordingly."""
    time_str, millis, offset = match.groups()
    formatted_offset = f"{offset[:3]}:{offset[3:]}"
    dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    offset_hours = int(offset[:3])
    adjusted_dt = dt - timedelta(hours=offset_hours)
    return f"{adjusted_dt.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

def sanitize_filename(filename):
    """Ensure the filename does not contain invalid characters."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

def add_extensions_tag(content):
    """Add <Extensions><ns3:TPX/></Extensions> after each <HeartRateBpm> block inside <Trackpoint>.
       If <Extensions> already exists, add <ns3:TPX/> inside it."""
    
    # Find <HeartRateBpm> with or without the xsi:type attribute and check if <Extensions> is already present
    content = re.sub(
        r'(<HeartRateBpm[^>]*>\s*<Value>\d+</Value>\s*</HeartRateBpm>)(?!\s*<Extensions>)',
        r'\1\n  <Extensions>\n    <ns3:TPX/>\n  </Extensions>',
        content
    )
    
    # If <Extensions> exists without <ns3:TPX/>, add it inside
    content = re.sub(
        r'(<Extensions>)(?!.*<ns3:TPX/>)(.*?)</Extensions>',
        r'\1\n    <ns3:TPX/>\n  \2</Extensions>',
        content
    )
    
    return content

def add_missing_heart_rate(content):
    """Ensure every Trackpoint has a HeartRateBpm tag. If missing, add the latest available HeartRateBpm value."""
    heart_rate_value = None
    
    # Match each Trackpoint and its contents
    trackpoint_pattern = re.compile(r'<Trackpoint>(.*?)</Trackpoint>', re.DOTALL)
    matches = trackpoint_pattern.findall(content)
    
    updated_content = content
    for match in matches:
        # Look for the HeartRateBpm tag within the current Trackpoint
        heart_rate_match = re.search(r'<HeartRateBpm[^>]*>\s*<Value>(\d+)</Value>\s*</HeartRateBpm>', match)
        
        if heart_rate_match:
            # Update the latest heart rate value when we find one
            heart_rate_value = heart_rate_match.group(1)
        elif heart_rate_value:
            # If no HeartRateBpm is found, but we have a previous value, insert it
            new_heart_rate = f'<HeartRateBpm>\n  <Value>{heart_rate_value}</Value>\n</HeartRateBpm>'
            updated_content = updated_content.replace(match, match + new_heart_rate, 1)

    return updated_content

def modify_tcx_file(filepath, output_folder):
    """Modify XML header, time format, heart rate tag, activity sport capitalization in a TCX file."""
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    # Fix header
    content = re.sub(
        r'<TrainingCenterDatabase[^>]*>',
        '<TrainingCenterDatabase\n  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"\n  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"\n  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"\n  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"\n  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"\n  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">',
        content
    )

    # Fix time format and correct timezone notation, then adjust time
    content = re.sub(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.(\d{3})([+-]\d{4})", fix_timezone_format, content)

    # Add Extensions tag after HeartRateBpm in Trackpoint
    content = add_extensions_tag(content)

    # Ensure every Trackpoint has a HeartRateBpm tag
    content = add_missing_heart_rate(content)

    # Fix activity sport capitalization
    content = re.sub(r'<Activity Sport="(\w+)">', lambda m: f'<Activity Sport="{m.group(1).capitalize()}">', content)

    # Fix HeartRateBpm tag
    content = re.sub(r'<HeartRateBpm[^>]*>', '<HeartRateBpm>', content)

    # Construct new filename
    original_filename = os.path.basename(filepath)
    new_filename = sanitize_filename(original_filename)  # Keep original filename format

    # Save modified file
    output_path = os.path.join(output_folder, new_filename)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)

    return output_path

def main():
    unique_files = locate_unique_files()
    modified_files = []

    for filename in unique_files.values():
        input_path = os.path.join(unique_folder, filename)
        output_path = modify_tcx_file(input_path, converted_folder)
        modified_files.append(output_path)

    # Write log file
    with open(log_file, "w") as log:
        log.write(f"Total unique activities: {len(unique_files)}\n")
        log.write("Unique files processed:\n")
        for activity_id, filename in unique_files.items():
            log.write(f"  {activity_id}: {filename}\n")
        log.write("\nModified files saved in ConvertedFiles:\n")
        for filepath in modified_files:
            log.write(f"  {filepath}\n")

    print("Processing complete! Check 'conversion_log.txt' for details.")

if __name__ == "__main__":
    main()
