import os
import hashlib
import pandas as pd
import logging
import time

# Configure logging
logging.basicConfig(filename='NASComparisonLog.txt', level=logging.INFO, format='%(asctime)s %(message)s')

# Function to calculate md5 hash
def get_md5(file_path):
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return file_path, hash_md5.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing file {file_path}: {str(e)}")
        return file_path, None

# Function to get list of files from a NAS share
def get_files_from_nas(nas_share):
    files = []
    for root, _, filenames in os.walk(nas_share):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

# Function to write hashes to CSV
def write_hashes_to_csv(files_and_hashes, output_csv_file):
    df = pd.DataFrame(files_and_hashes, columns=['File', 'md5'])
    df.to_csv(output_csv_file, index=False)

# Function to format time in a human-readable way
def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    return f"{int(hrs):02d}:{int(mins):02d}:{int(secs):02d}"

# Paths to NAS share and output CSV file
nas_share = r"\\path\to\nas"
output_csv_file = "NAS_Hashes.csv"

# Log start of script
logging.info("Starting NAS hashing script...")

# Get list of files from the NAS share
files = get_files_from_nas(nas_share)
total_files = len(files)

# Initialize time tracking variables
start_time = time.time()
processed_files = 0
estimated_end_time = None

# Process files sequentially
files_and_hashes = []

for file in files:
    file_path, file_hash = get_md5(file)
    if file_hash is not None:  # Only append if hashing was successful
        files_and_hashes.append({'File': file_path, 'md5': file_hash})

    # Update progress
    processed_files += 1
    progress_percentage = round((processed_files / total_files) * 100, 2)
    
    # Calculate elapsed time and estimate remaining time
    elapsed_time = time.time() - start_time
    avg_time_per_file = elapsed_time / processed_files
    remaining_files = total_files - processed_files
    estimated_remaining_time = avg_time_per_file * remaining_files
    estimated_end_time = time.time() + estimated_remaining_time
    estimated_end_time_formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(estimated_end_time))
    
    logging.info(f"Progress: {progress_percentage}% completed for {nas_share}. Estimated completion time: {estimated_end_time_formatted}")

# Write hashes to CSV
write_hashes_to_csv(files_and_hashes, output_csv_file)
logging.info(f"Hashes for {nas_share} written to {output_csv_file}")

# Log end of script
end_time = time.time()
total_elapsed_time = format_time(end_time - start_time)
logging.info(f"Script completed. Total elapsed time: {total_elapsed_time}")
