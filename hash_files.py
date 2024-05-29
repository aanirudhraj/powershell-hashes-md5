import hashlib
import csv
import multiprocessing

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return file_path, hash_md5.hexdigest()
    except (FileNotFoundError, PermissionError):
        return file_path, None

def update_csv_with_md5(csv_path, num_threads):
    with open(csv_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # Read header
        file_paths = [row[0] for row in csvreader]
    
    with multiprocessing.Pool(num_threads) as pool:
        results = pool.map(calculate_md5, file_paths)
    
    with open(csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['path', 'md5'])  # Write header
        csvwriter.writerows(results)

# Example usage
nas_share_path = '/path/to/nas/share'
csv_file_path = 'file_paths.csv'

# Write file paths to CSV
write_file_paths_to_csv(nas_share_path, csv_file_path, num_threads=4)
print(f'File paths have been written to {csv_file_path}')

# Update CSV with MD5 hashes
update_csv_with_md5(csv_file_path, num_threads=4)
print(f'The CSV file {csv_file_path} has been updated with MD5 hashes.')
