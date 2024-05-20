import os
import xxhash
import time
import pandas as pd
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configure logging
logging.basicConfig(filename='NASComparisonLog.txt', level=logging.INFO, format='%(asctime)s %(message)s')

# Function to calculate xxhash
def get_xxhash(file_path):
    try:
        hash_xx = xxhash.xxh64()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_xx.update(chunk)
        return file_path, hash_xx.hexdigest()
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
    df = pd.DataFrame(files_and_hashes, columns=['File', 'xxHash'])
    df.to_csv(output_csv_file, index=False)

# Paths to NAS share and output CSV file
nas_share = r"\\path\to\nas"
output_csv_file = "NAS_Hashes.csv"

# Log start of script
logging.info("Starting NAS hashing script...")

# Get list of files from the NAS share
files = get_files_from_nas(nas_share)
total_files = len(files)

# Define the number of workers (adjust based on your system's CPU)
num_workers = os.cpu_count()

# Process files in parallel
files_and_hashes = []
processed_files = 0

with ProcessPoolExecutor(max_workers=num_workers) as executor:
    future_to_file = {executor.submit(get_xxhash, file): file for file in files}
    for future in as_completed(future_to_file):
        file, file_hash = future.result()
        files_and_hashes.append({'File': file, 'xxHash': file_hash})
        
        # Update progress
        processed_files += 1
        progress_percentage = round((processed_files / total_files) * 100, 2)
        logging.info(f"Progress: {progress_percentage}% completed for {nas_share}")

# Write hashes to CSV
write_hashes_to_csv(files_and_hashes, output_csv_file)
logging.info(f"Hashes for {nas_share} written to {output_csv_file}")

# Log end of script
logging.info("Script completed.")
