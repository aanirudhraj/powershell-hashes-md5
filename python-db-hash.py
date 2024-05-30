import hashlib
import sqlite3
from multiprocessing import Pool

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return None

def update_md5_in_db(file_info):
    file_id, file_path, db_path = file_info
    md5 = calculate_md5(file_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE files SET md5 = ? WHERE id = ?', (md5, file_id))
    conn.commit()
    conn.close()

def get_file_paths(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, path FROM files WHERE md5 IS NULL')
    file_paths = cursor.fetchall()
    conn.close()
    return file_paths

def parallel_process_md5(db_path, num_threads):
    file_paths = get_file_paths(db_path)
    file_info = [(file_id, file_path, db_path) for file_id, file_path in file_paths]

    with Pool(num_threads) as pool:
        pool.map(update_md5_in_db, file_info)

# Example usage for Step 2
num_threads = 4  # Set the number of threads here

parallel_process_md5(db_file_path, num_threads)
print(f'The SQLite database {db_file_path} has been updated with MD5 hashes.')
