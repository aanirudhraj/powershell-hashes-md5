import os
import csv
import multiprocessing
from multiprocessing import Queue

def collect_file_paths(base_path, queue):
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.startswith('.') or file.startswith('~'):
                continue
            file_path = os.path.join(root, file)
            queue.put(file_path)

def write_file_paths_to_csv(base_path, csv_path, num_threads):
    root_directories = [os.path.join(base_path, d) for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    queue = Queue()
    
    with open(csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['path', 'md5'])  # Write header

    processes = []
    for root_dir in root_directories:
        p = multiprocessing.Process(target=collect_file_paths, args=(root_dir, queue))
        processes.append(p)
        p.start()

    with open(csv_path, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        while any(p.is_alive() for p in processes) or not queue.empty():
            while not queue.empty():
                file_path = queue.get()
                csvwriter.writerow([file_path, ''])

    for p in processes:
        p.join()

# Example usage
nas_share_path = '/path/to/nas/share'
csv_file_path = 'file_paths.csv'
num_threads = 4  # Set the number of threads here

write_file_paths_to_csv(nas_share_path, csv_file_path, num_threads)
print(f'File paths have been written to {csv_file_path}')
