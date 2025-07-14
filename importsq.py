import sqlite3

conn = sqlite3.connect('gematria_data.db')
cursor = conn.cursor()

# Create table for sentences
cursor.execute('''
CREATE TABLE IF NOT EXISTS example_sentences (
    text TEXT UNIQUE
)
''')

# Load from a text file line by line
with open('alice.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

for line in lines:
    cursor.execute('INSERT OR IGNORE INTO example_sentences (text) VALUES (?)', (line,))

conn.commit()
conn.close()
print(f"Inserted {len(lines)} lines into database.")
