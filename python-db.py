import os
from pathlib import Path
import sqlite3

def initialize_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            path TEXT NOT NULL,
            md5 TEXT
        )
    ''')
    conn.commit()
    conn.close()

def store_file_paths(base_path, db_path, batch_size=100):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    file_list = []

    def scan_directory(directory):
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_file() and not entry.name.startswith('.') and not entry.name.startswith('~'):
                    file_list.append((str(entry.path),))
                    if len(file_list) >= batch_size:
                        cursor.executemany('INSERT INTO files (path) VALUES (?)', file_list)
                        file_list.clear()
                elif entry.is_dir() and not entry.name.startswith('.') and not entry.name.startswith('~'):
                    scan_directory(entry.path)
    
    scan_directory(base_path)
    
    if file_list:  # Insert any remaining files
        cursor.executemany('INSERT INTO files (path) VALUES (?)', file_list)

    conn.commit()
    conn.close()

# Example usage for Step 1
nas_share_path = '/path/to/nas/share'
db_file_path = 'files.db'

initialize_db(db_file_path)
store_file_paths(nas_share_path, db_file_path)
print(f'File paths have been stored in {db_file_path}')
