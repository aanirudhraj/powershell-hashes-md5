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

def store_file_paths(base_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.startswith('.') or file.startswith('~'):
                continue
            file_path = str(Path(root) / file)
            cursor.execute('INSERT INTO files (path) VALUES (?)', (file_path,))
    
    conn.commit()
    conn.close()

# Example usage for Step 1
nas_share_path = '/path/to/nas/share'
db_file_path = 'files.db'

initialize_db(db_file_path)
store_file_paths(nas_share_path, db_file_path)
print(f'File paths have been stored in {db_file_path}')
