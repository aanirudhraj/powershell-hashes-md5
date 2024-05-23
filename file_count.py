import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def count_files_in_directory(path):
    file_count = 0
    subdirectories = []
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.name.startswith('.') or entry.name.startswith('~'):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    subdirectories.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    file_count += 1
    except PermissionError:
        pass  # Optionally log the error
    return file_count, subdirectories

def total_file_count_in_directory(path):
    total_file_count = 0
    with ThreadPoolExecutor() as executor:
        futures = {}
        
        initial_file_count, subdirectories = count_files_in_directory(path)
        total_file_count += initial_file_count
        for subdir in subdirectories:
            futures[executor.submit(count_files_in_directory, subdir)] = subdir
        
        while futures:
            done, _ = as_completed(futures.keys(), timeout=None).popitem()
            subdir = futures.pop(done)
            file_count, sub_subdirectories = done.result()
            total_file_count += file_count
            for sub_subdir in sub_subdirectories:
                futures[executor.submit(count_files_in_directory, sub_subdir)] = sub_subdir

    return total_file_count

def list_root_folders_with_file_counts(base_path):
    root_folder_counts = {}
    try:
        with os.scandir(base_path) as it:
            for entry in it:
                if entry.is_dir(follow_symlinks=False) and not entry.name.startswith('.') and not entry.name.startswith('~'):
                    root_folder_counts[entry.path] = total_file_count_in_directory(entry.path)
    except PermissionError:
        pass  # Optionally log the error
    return root_folder_counts

def write_counts_to_file(counts, file_path):
    with open(file_path, 'w') as file:
        for folder, count in counts.items():
            file.write(f'Folder: {folder}, File Count: {count}\n')

# Example usage
nas_share_path = '/path/to/nas/share'
output_file_path = 'nas_share_file_counts.txt'

root_folder_counts = list_root_folders_with_file_counts(nas_share_path)
write_counts_to_file(root_folder_counts, output_file_path)

print(f'The file counts have been written to {output_file_path}')
