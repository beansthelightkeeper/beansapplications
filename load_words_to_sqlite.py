import sqlite3

# Connect to your existing database
conn = sqlite3.connect('gematria_data.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS simple_words (
    word TEXT UNIQUE
)
''')

# Load words from the file
with open('words_alpha.txt', 'r') as file:
    words = [line.strip() for line in file if line.strip()]

# Insert words into the table
for word in words:
    cursor.execute('INSERT OR IGNORE INTO simple_words (word) VALUES (?)', (word,))

# Commit and close
conn.commit()
conn.close()

print(f"Inserted {len(words)} words into the database.")
