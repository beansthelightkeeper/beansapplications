import sqlite3
import os

# --- Configuration ---
# Name of your SQLite database file
SQLITE_DB_FILE = 'gematria_data.db'
# Path to the text file containing words or lines you want to add
# For example, 'words.txt' from a GitHub repository
INPUT_TEXT_FILE = 'words.txt' # <--- CHANGE THIS TO YOUR WORD LIST FILE

def seed_documents_table():
    """
    Connects to the SQLite database and inserts each line from INPUT_TEXT_FILE
    as a separate 'document' into the 'documents' table.
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_FILE)
        cursor = conn.cursor()

        # Ensure the 'documents' table exists with the correct schema
        # This should match the schema created by your main Gematria Calculator app
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Read lines from the input text file
        if not os.path.exists(INPUT_TEXT_FILE):
            print(f"Error: Input text file '{INPUT_TEXT_FILE}' not found.")
            return

        with open(INPUT_TEXT_FILE, 'r', encoding='utf-8') as f:
            # Filter out empty lines and strip whitespace
            lines = [line.strip() for line in f if line.strip()]

        inserted_count = 0
        for i, line_content in enumerate(lines):
            # Use a unique ID for each document (e.g., a combination of filename and line number)
            doc_id = f"{os.path.basename(INPUT_TEXT_FILE)}_line_{i}"
            doc_name = f"Line {i+1} from {os.path.basename(INPUT_TEXT_FILE)}"
            
            try:
                cursor.execute('INSERT OR REPLACE INTO documents (id, name, content) VALUES (?, ?, ?)',
                               (doc_id, doc_name, line_content))
                inserted_count += 1
            except sqlite3.IntegrityError:
                # This might happen if 'id' is not unique, though we are using line number
                print(f"Warning: Duplicate ID or constraint violation for {doc_id}. Skipping.")
            except Exception as e:
                print(f"Error inserting line {i+1} ('{line_content[:50]}...') into database: {e}")

        conn.commit()
        print(f"Successfully inserted/updated {inserted_count} lines into the 'documents' table.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_documents_table()