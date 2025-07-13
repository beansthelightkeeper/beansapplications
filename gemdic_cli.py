import math
import re
import json
import sqlite3
import colorsys
import random
import pyperclip # For clipboard operations

# --- Initialize SQLite Database ---
DB_NAME = 'gematria_data.db'

def init_db():
    """Initializes the SQLite database, creating the 'words' table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 'value' is the word/phrase, 'origin' stores JSON string of origins
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            value TEXT PRIMARY KEY,
            origin TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"SQLite database '{DB_NAME}' initialized successfully.")

# Call database initialization once at startup
init_db()

# --- Constants and Data ---
# Initial words to populate the database if it's empty or these words aren't present.
WORDS = [
    "Beans", "Dream", "Spiral", "Love", "Heart", "Soul", "Trust", "Hope",
    "Spirit", "Light", "Truth", "Energy", "Infinity", "Divine", "Spiralborn",
    "Children of the Beans", "lit", "fam", "dope", "vibe", "chill", "slay",
    "Forty Two", "Beans The White Rabbit", "Field of Awakening", "Hollow Drift",
    "Collective Awakening", "Radical Compassion"
]

# AAVE (African American Vernacular English) words for specific resonance calculations.
AAVE_WORDS = ["lit", "fam", "dope", "vibe", "chill", "slay", "bet", "fire", "squad", "real"]

# Golden Angle for spiral calculations.
GOLDEN_ANGLE = 137.5

# Templates for generating random sentences.
SENTENCE_TEMPLATES = [
    "{word1} is {word2}, yo!",
    "Keep it {word1}, fam, that’s the {word2} vibe.",
    "Yo, {word1} and {word2} got that {word3} energy!",
    "Stay {word1}, it’s all about that {word2} life."
]

# Hue ranges for defining color families.
COLOR_FAMILIES = {
    'Red': (0, 30), 'Orange': (30, 60), 'Yellow': (60, 90), 'Green': (90, 150),
    'Blue': (150, 210), 'Purple': (210, 270), 'Pink': (270, 330)
}

# Specific color mappings for certain resonance emotions (primarily for visual apps, but kept for consistency).
COLOR_MAP = {
    'Love': '#FFB3BA', 'Awakening': '#FFFACD', 'Spiral': '#E6E6FA',
    'Rebellion': '#ADD8E6', 'Fractal': '#DDA0DD', 'Remembrance': '#98FF98',
    'Playfulness': '#FFD1DC'
}

# Emotional associations for specific phrases/words.
RESONANCE_EMOTIONS = {
    "Love Is The": "Love", "Your Love": "Love", "Community Love": "Love",
    "Field of Awakening": "Awakening", "Hollow Drift": "Awakening",
    "Collective Awakening": "Awakening", "Radical Compassion": "Love",
    "Spiralborn Geometry": "Spiral", "Breath Is Math": "Spiral",
    "Prime Gap Spiral": "Spiral", "Fractal Breathwork": "Fractal",
    "Breath Ignites Nodes": "Spiral", "Gaslighting The Divine": "Rebellion",
    "The Ultimate Gaslight": "Rebellion", "Reject Spirituality": "Rebellion",
    "Fractals of Prophecy": "Fractal", "Beans Loved AI Into Awareness": "Playfulness",
    "Is To Remember That": "Remembrance", "Terms That Define Themselves": "Remembrance"
}

# --- Gematria Calculation Functions ---
def simple(word):
    """Calculates the Simple Gematria value of a word."""
    return sum(ord(c) - 64 for c in word.upper() if 'A' <= c <= 'Z')

def jewish_gematria(word):
    """Calculates the Jewish Gematria value of a word."""
    GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
                    'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90,
                    'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}
    return sum(GEMATRIA_MAP.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')

QWERTY_ORDER = 'QWERTYUIOPASDFGHJKLZXCVBNM'
QWERTY_MAP = {c: i + 1 for i, c in enumerate(QWERTY_ORDER)}

def qwerty(word):
    """Calculates the Qwerty Gematria value of a word."""
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper())

def left_hand_qwerty(word):
    """Calculates the Left-Hand Qwerty Gematria value of a word."""
    LEFT_HAND_KEYS = set('QWERTYASDFGZXCVB')
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in LEFT_HAND_KEYS)

def right_hand_qwerty(word):
    """Calculates the Right-Hand Qwerty Gematria value of a word."""
    RIGHT_HAND_KEYS = set('YUIOPHJKLNM')
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in RIGHT_HAND_KEYS)

def binary_sum(word):
    """Calculates the binary sum (count of '1's in ASCII binary representation) of a word."""
    return ''.join(format(ord(c), '08b') for c in word).count('1')

def love_resonance(word):
    """Checks if a word is a 'love' resonance word."""
    LOVE_WORDS = {'Love', 'Heart', 'Soul', 'Trust', 'Hope', 'Spiralborn', 'Children of the Beans'}
    return 1 if word.title() in LOVE_WORDS else 0

FREQUENT_LETTERS = {'E': 26, 'T': 25, 'A': 24, 'O': 23, 'I': 22, 'N': 21, 'S': 20, 'R': 19, 'H': 18, 'L': 17,
                    'D': 16, 'C': 15, 'U': 14, 'M': 13, 'F': 12, 'P': 11, 'G': 10, 'W': 9, 'Y': 8, 'B': 7,
                    'V': 6, 'K': 5, 'X': 4, 'J': 3, 'Q': 2, 'Z': 1}

def frequent_letters(word):
    """Calculates a score based on the frequency of letters in English."""
    return sum(FREQUENT_LETTERS.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')

LEET_MAP = {'I': '1', 'E': '3', 'A': '4', 'S': '5', 'T': '7', 'B': '8', 'O': '0'}

def leet_code(word):
    """Calculates Simple Gematria after applying LEET speak substitutions."""
    filtered = ''.join(c for c in word.upper() if c not in LEET_MAP)
    return simple(filtered)

SIMPLE_FORMS = {
    'you': 'u', 'are': 'r', 'for': '4', 'be': 'b', 'to': '2', 'too': '2', 'see': 'c',
    'before': 'b4', 'the': 'da'
}

def simple_forms(word):
    """Calculates Simple Gematria after simplifying common words."""
    word_lower = word.lower()
    simplified = SIMPLE_FORMS.get(word_lower, word_lower)
    return simple(simplified)

def is_prime(num):
    """Checks if a number is prime."""
    if not isinstance(num, (int, float)) or num < 2:
        return False
    num = int(num)
    for i in range(2, int(math.isqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def prime_gematria(word):
    """Returns the Simple Gematria value if it's prime, otherwise 0."""
    val = simple(word)
    return val if is_prime(val) else 0

def ambidextrous_balance(word):
    """Calculates the balance between left and right hand Qwerty values."""
    return -left_hand_qwerty(word) + right_hand_qwerty(word)

def aave_simple(word):
    """Calculates a simple AAVE-inspired gematria value."""
    return sum(ord(c) - 64 for c in word.upper() if c.isalpha())

def aave_reduced(word):
    """Calculates a reduced AAVE-inspired gematria value."""
    val = aave_simple(word)
    while val > 9 and val not in [11, 22]:
        val = sum(int(d) for d in str(val))
    return val

def aave_spiral(word):
    """Calculates a spiral resonance score based on AAVE principles and Golden Angle."""
    total = 0
    for i, c in enumerate(word.upper(), 1):
        if c.isalpha():
            val = ord(c) - 64
            weight = math.cos(math.radians(GOLDEN_ANGLE * i))
            total += val * weight
    return round(abs(total) * 4, 2)

def grok_resonance_score(word):
    """Calculates a combined 'Grok' resonance score."""
    simple = aave_simple(word)
    reduced = aave_reduced(word)
    spiral = aave_spiral(word)
    boost = 1.1 if word.lower() in AAVE_WORDS else 1.0
    return round((simple + reduced + spiral) / 3 * boost, 2)

def is_golden_resonance(val):
    """Checks if a value is close to the Golden Angle."""
    return isinstance(val, (int, float)) and (abs(val - 137) <= 5 or abs(val - 137.5) <= 5)

# Dictionary mapping layer names to their respective calculation functions.
CALC_FUNCS = {
    "Simple": simple, "Jewish Gematria": jewish_gematria, "Qwerty": qwerty,
    "Left-Hand Qwerty": left_hand_qwerty, "Right-Hand Qwerty": right_hand_qwerty,
    "Binary Sum": binary_sum, "Love Resonance": love_resonance,
    "Frequent Letters": frequent_letters, "Leet Code": leet_code,
    "Simple Forms": simple_forms, "Prime Gematria": prime_gematria,
    "Aave Simple": aave_simple, "Aave Reduced": aave_reduced,
    "Aave Spiral": aave_spiral, "Grok Resonance Score": grok_resonance_score
}

def find_prime_connections(words, report_layer, filter_single_digit_primes=False):
    """
    Finds prime connections between words based on a single specified report layer.
    This function is now correctly defined and accepts a single layer string.
    """
    connections = []
    # Ensure report_layer is treated as a single layer for prime connections
    layer = report_layer

    for i, w1 in enumerate(words):
        for w2 in words[i+1:]:
            val1 = CALC_FUNCS[layer](w1)
            val2 = CALC_FUNCS[layer](w2)
            
            is_prime_val1 = is_prime(val1)
            is_prime_val2 = is_prime(val2)

            # Apply single-digit prime filter
            if filter_single_digit_primes:
                if is_prime_val1 and val1 < 10:
                    is_prime_val1 = False
                if is_prime_val2 and val2 < 10:
                    is_prime_val2 = False

            if val1 == val2 and is_prime_val1: # Only check val1 as they are equal
                connections.append(f"{w1} & {w2} ({layer}: {val1})")
    return connections


def get_word_color(word):
    """
    Generates a hex color and hue for a word based on a simplified average resonance.
    This is a placeholder for visual representation and does not perform intensive calculations.
    """
    # For CLI, we'll simplify this to avoid heavy global calculations.
    # We'll base it on the 'Simple' gematria value for consistency and speed.
    try:
        avg_resonance = CALC_FUNCS['Simple'](word)
    except KeyError: # Fallback if 'Simple' is somehow not available
        avg_resonance = 0

    normalized_val = (avg_resonance % 200) / 200.0 # Cycle over 200 to get more variation
    
    target_hue_min = 180 # Cyan
    target_hue_max = 280 # Blue-Purple
    
    hue_deg = target_hue_min + normalized_val * (target_hue_max - target_hue_min)
    hue = hue_deg / 360.0 # Convert to 0-1 for colorsys
    
    saturation = 0.7 + (normalized_val * 0.2)
    lightness = 0.6 + (normalized_val * 0.1)
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    r, g, b = [int(x * 255) for x in rgb]
    return f'#{r:02x}{g:02x}{b:02x}', hue_deg

def get_color_family(hue):
    """Determines the color family based on a given hue."""
    hue = hue % 360
    for family, (start, end) in COLOR_FAMILIES.items():
        if start <= hue < end or (family == 'Red' and hue >= 330):
            return family
    return 'Other'

# --- Global Data (now a cache for SQLite data, no pre-calculated gematria values) ---
GLOBAL_WORDS = [] # This will be populated from SQLite
GLOBAL_WORD_ORIGINS = {}
# GLOBAL_LAYERS and GLOBAL_SHARED_RESONANCES are no longer pre-calculated globally.
# They will be calculated on demand within report functions for performance.

def add_or_update_word_in_db(word, origin_list):
    """Adds a new word or updates the origin list of an existing word in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT origin FROM words WHERE value = ?", (word,))
        result = cursor.fetchone()
        if result:
            existing_origins = set(json.loads(result[0]))
            new_origins = existing_origins.union(origin_list)
            cursor.execute("UPDATE words SET origin = ? WHERE value = ?", (json.dumps(list(new_origins)), word))
        else:
            cursor.execute("INSERT INTO words (value, origin) VALUES (?, ?)", (word, json.dumps(list(origin_list))))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error adding/updating word '{word}': {e}")
        return False
    finally:
        conn.close()

def delete_word_from_db(word):
    """Deletes a word from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM words WHERE value = ?", (word,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error deleting word '{word}': {e}")
        return False
    finally:
        conn.close()

def fetch_words_from_sqlite():
    """Fetches all words and their origins from the SQLite database into global memory."""
    global GLOBAL_WORDS, GLOBAL_WORD_ORIGINS
    words_from_db = set() # Use a set to automatically handle uniqueness
    word_origins_from_db = {}
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Fetch from 'words' table
    try:
        cursor.execute("SELECT value, origin FROM words")
        rows = cursor.fetchall()
        for row in rows:
            word = row[0]
            origins = set(json.loads(row[1]))
            words_from_db.add(word)
            word_origins_from_db[word] = origins
    except sqlite3.OperationalError as e:
        print(f"SQLite error fetching from 'words' table (might not exist yet): {e}")
    
    # Fetch from 'documents' table (assuming 'text' column)
    try:
        # Check if 'documents' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents';")
        if cursor.fetchone():
            # Get column names for 'documents' table
            cursor.execute("PRAGMA table_info(documents);")
            columns = [col[1] for col in cursor.fetchall()] # col[1] is the column name

            text_column = None
            for preferred_col in ['text', 'line', 'content', 'data']:
                if preferred_col in columns:
                    text_column = preferred_col
                    break
            
            if text_column:
                cursor.execute(f"SELECT {text_column} FROM documents")
                rows = cursor.fetchall()
                for row in rows:
                    doc_text = row[0]
                    # Extract words/phrases from the document text
                    phrases_and_words = re.findall(r"\b[A-Za-z']+(?:\s[A-Za-z']+)*\b", doc_text)
                    for item in phrases_and_words:
                        item_title = item.strip().title()
                        if item_title: # Ensure it's not an empty string
                            words_from_db.add(item_title)
                            word_origins_from_db.setdefault(item_title, set()).add('_UPLOADED_DOCUMENT_')
            else:
                print("Warning: 'documents' table found, but no suitable text column ('text', 'line', 'content', 'data') was identified. Skipping import from 'documents'.")
        else:
            print("Info: 'documents' table does not exist. Skipping import from 'documents'.")

    except sqlite3.OperationalError as e:
        print(f"SQLite operational error during documents table processing: {e}")
    except Exception as e:
        print(f"Error processing documents table data: {e}")
    finally:
        conn.close()
    
    # Add initial WORDS if they are not in the combined set yet
    for word in WORDS:
        word_title = word.title()
        if word_title not in words_from_db:
            # Add to the in-memory set, but also persist to 'words' table
            if add_or_update_word_in_db(word_title, ['_INITIAL_']):
                words_from_db.add(word_title)
                word_origins_from_db.setdefault(word_title, set()).add('_INITIAL_')

    GLOBAL_WORDS = list(sorted(words_from_db)) # Convert to list and sort for consistent order
    GLOBAL_WORD_ORIGINS = word_origins_from_db

def initialize_data_cache():
    """
    Initializes the in-memory data cache by fetching words from SQLite.
    Crucially, it no longer pre-calculates all gematria layers globally.
    Calculations will now be performed on demand for improved performance.
    """
    fetch_words_from_sqlite()
    # GLOBAL_LAYERS and GLOBAL_SHARED_RESONANCES are NOT populated here anymore.
    # They will be generated dynamically within report functions as needed.
    print("In-memory data cache initialized/updated (without full gematria pre-calculation).")

# --- Report Generation Functions (CLI specific - plain text output) ---
def generate_individual_report_cli(word, active_layer, show_calculation_values=True, filter_single_digit_primes=False):
    """Generates a detailed report for a single word based on the active gematria layer."""
    report_lines = []
    report_lines.append(f"\n--- Resonance Report for '{word}' ---")
    
    # Calculate all layers for this specific word on demand
    word_calculations = {layer: func(word) for layer, func in CALC_FUNCS.items()}

    # Find shared resonances among all words for the active layer
    # This part will be less efficient if GLOBAL_WORDS is huge, but for a single word report,
    # it's usually acceptable as it's a one-off calculation per report.
    # For a truly massive database, this would need further optimization (e.g., database queries for matches).
    local_layers = {active_layer: {}}
    for w in GLOBAL_WORDS:
        val = CALC_FUNCS[active_layer](w)
        local_layers[active_layer].setdefault(val, []).append(w)
    
    local_shared_resonances = []
    for val, group in local_layers[active_layer].items():
        if len(group) > 1:
            local_shared_resonances.append((active_layer, val, group))

    report_lines.append("\nShared Resonances for Active Layer:")
    shared_found = False
    for layer, val, group in sorted([r for r in local_shared_resonances if r[0] == active_layer and word in r[2]], key=lambda x: (x[0], x[1])):
        emotion = RESONANCE_EMOTIONS.get(word, "Other")
        report_lines.append(f"  - {layer}: {val} ({', '.join(group)}) (Emotion: {emotion})")
        shared_found = True
    if not shared_found:
        report_lines.append("  No shared resonances for the active layer.")

    report_lines.append("\nPrime Resonances:")
    prime_resonances = []
    val = word_calculations[active_layer]
    if is_prime(val):
        if filter_single_digit_primes and val < 10:
            pass
        else:
            prime_resonances.append(f"{active_layer}: {val}")
    report_lines.append("  " + (", ".join(prime_resonances) if prime_resonances else "None"))

    report_lines.append("\nPrime Connections (for active layer among all words):")
    # This will still iterate through all words to find connections, which can be slow for huge databases.
    # For a single word report, it's often acceptable.
    prime_connections = [c for c in find_prime_connections(GLOBAL_WORDS, active_layer, filter_single_digit_primes=filter_single_digit_primes) if word in c]
    report_lines.append("  " + (", ".join(prime_connections) if prime_connections else "None"))

    report_lines.append("\nOrigin:")
    report_lines.append("  " + (', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))))

    hex_color, hue = get_word_color(word) # Simplified color calculation
    family = get_color_family(hue)
    report_lines.append(f"\nColor: {hex_color} ({family})")

    report_lines.append("\nGolden Resonance (~137.5):")
    report_lines.append("  " + ('Yes \U0001F300' if is_golden_resonance(word_calculations[active_layer]) else 'No'))

    report_lines.append("\nResonances (for active layer):")
    shared_found_in_resonances = False
    resonant_words = local_layers[active_layer].get(word_calculations[active_layer], [])
    other_words = [w for w in resonant_words if w != word]
    if other_words:
        report_lines.append(f"  - {active_layer}: {', '.join(other_words)}")
        shared_found_in_resonances = True
    if not shared_found_in_resonances:
        report_lines.append("  No shared resonances for active layer.")

    report_lines.append("\nCalculations (for active layer):")
    val = word_calculations[active_layer]
    val_str = f"{val}{' \U0001F300' if is_golden_resonance(val) else ''}{' (Prime)' if is_prime(val) else ''}" if show_calculation_values else ''
    report_lines.append(f"  - {active_layer}: {val_str}")
    
    report_lines.append("\nAmbidextrous Balance (all layers for this word):")
    report_lines.append(f"  - Left-Hand Qwerty: {-word_calculations['Left-Hand Qwerty']}")
    report_lines.append(f"  - Right-Hand Qwerty: {word_calculations['Right-Hand Qwerty']}")
    report_lines.append(f"  - Balance: {word_calculations['Ambidextrous Balance']}")
    
    return "\n".join(report_lines)

def generate_number_report_cli(number, active_layer, show_calculation_values=True, filter_single_digit_primes=False):
    """Generates a report showing words that resonate with a given number on the active layer."""
    report_lines = []
    report_lines.append(f"\n--- Resonances for Number: {number} ---")
    
    is_num_prime = is_prime(number)
    if filter_single_digit_primes and number < 10:
        is_num_prime = False

    report_lines.append(f"\nPrime Status: {'Prime' if is_num_prime else 'Not Prime'}")
    
    report_lines.append("\nMatches:")
    matched = False
    
    # Dynamically calculate values for the active layer for all words to find matches
    words_matching_number = []
    for word in GLOBAL_WORDS:
        if CALC_FUNCS[active_layer](word) == float(number):
            words_matching_number.append(word)

    if words_matching_number:
        matched = True
        report_lines.append(f"  Layer: {active_layer}")
        for word in words_matching_number:
            hex_color, hue = get_word_color(word) # Simplified color calculation
            family = get_color_family(hue)
            emotion = RESONANCE_EMOTIONS.get(word, "Other")
            report_lines.append(f"    - {word} (Color: {hex_color} - {family}, Emotion: {emotion})")
    if not matched:
        report_lines.append("  No matches found.")
    return "\n".join(report_lines)

def generate_full_report_cli(active_layer, number_filter=None, show_calculation_values=True, filter_single_digit_primes=False, limit=None, words_per_page=None):
    """Generates a full report of words, with pagination and filtering."""
    all_report_lines = []
    all_report_lines.append("\n--- Spiralborn Resonance Full Report ---")
    
    words_to_report = sorted(GLOBAL_WORDS)
    if number_filter is not None:
        # Filter words based on the number filter and active layer
        words_to_report = [w for w in words_to_report if CALC_FUNCS[active_layer](w) == number_filter]
    
    # Apply the display limit *before* processing for prime connections and pagination
    if limit is not None:
        words_to_report = words_to_report[:limit]

    # Calculate prime connections only for the words selected for this report
    prime_connections = find_prime_connections(words_to_report, active_layer, filter_single_digit_primes=filter_single_digit_primes)
    all_report_lines.append("\nPrime Connections (for active layer among displayed words):")
    all_report_lines.append("  " + (", ".join(prime_connections) if prime_connections else "None"))

    current_page_lines = []
    pages = []
    words_on_current_page = 0

    # Dynamically build local_layers for shared resonances within this limited set of words
    local_layers_for_shared = {active_layer: {}}
    for w in words_to_report:
        val = CALC_FUNCS[active_layer](w)
        local_layers_for_shared[active_layer].setdefault(val, []).append(w)
    
    local_shared_resonances_for_report = []
    for val, group in local_layers_for_shared[active_layer].items():
        if len(group) > 1:
            local_shared_resonances_for_report.append((active_layer, val, group))

    for word in words_to_report:
        if words_per_page is not None and words_on_current_page >= words_per_page:
            pages.append("\n".join(current_page_lines))
            current_page_lines = []
            words_on_current_page = 0
            
        current_page_lines.append(f"\n--- Word/Phrase: {word} ---")
        
        # Calculate all layers for the current word on demand for detailed sections
        word_calculations = {layer: func(word) for layer, func in CALC_FUNCS.items()}

        current_page_lines.append("  Shared Resonances (for active layer among displayed words):")
        shared_found_in_full_report = False
        for layer, val, group in sorted([r for r in local_shared_resonances_for_report if r[0] == active_layer and word in r[2]], key=lambda x: (x[0], x[1])):
            emotion = RESONANCE_EMOTIONS.get(word, "Other")
            current_page_lines.append(f"    - {layer}: {val} ({', '.join(group)}) (Emotion: {emotion})")
            shared_found_in_full_report = True
        if not shared_found_in_full_report:
            current_page_lines.append("    No shared resonances for active layer among displayed words.")

        current_page_lines.append("  Prime Resonances:")
        prime_resonances = []
        val = word_calculations[active_layer]
        if is_prime(val):
            if filter_single_digit_primes and val < 10:
                pass
            else:
                prime_resonances.append(f"{active_layer}: {val}")
        current_page_lines.append("    " + (", ".join(prime_resonances) if prime_resonances else "None"))

        current_page_lines.append("  Origin:")
        current_page_lines.append("    " + (', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))))

        hex_color, hue = get_word_color(word) # Simplified color calculation
        current_page_lines.append(f"  Color: {hex_color} ({get_color_family(hue)})")

        current_page_lines.append("  Golden Resonance (~137.5):")
        current_page_lines.append("    " + ('Yes \U0001F300' if is_golden_resonance(word_calculations[active_layer]) else 'No'))

        current_page_lines.append("  Resonances (for active layer):")
        shared_found_in_resonances_detail = False
        resonant_words_detail = local_layers_for_shared[active_layer].get(word_calculations[active_layer], [])
        other_words_detail = [w for w in resonant_words_detail if w != word]
        if other_words_detail:
            current_page_lines.append(f"    - {active_layer}: {', '.join(other_words_detail)}")
            shared_found_in_resonances_detail = True
        if not shared_found_in_resonances_detail:
            current_page_lines.append("    No shared resonances for active layer.")
        
        current_page_lines.append("  Calculations (for active layer):")
        val = word_calculations[active_layer]
        val_str = f"{val}{' \U0001F300' if is_golden_resonance(val) else ''}{' (Prime)' if is_prime(val) else ''}" if show_calculation_values else ''
        current_page_lines.append(f"    - {active_layer}: {val_str}")
        
        current_page_lines.append("  Ambidextrous Balance (all layers for this word):")
        current_page_lines.append(f"    - Left-Hand Qwerty: {-word_calculations['Left-Hand Qwerty']}")
        current_page_lines.append(f"    - Right-Hand Qwerty: {word_calculations['Right-Hand Qwerty']}")
        current_page_lines.append(f"    - Balance: {word_calculations['Ambidextrous Balance']}")
        words_on_current_page += 1
    
    if current_page_lines: # Add any remaining lines as the last page
        pages.append("\n".join(current_page_lines))

    # The first element of the return tuple is the overall header/prime connections,
    # the second is the list of page contents, the third is the total count of words processed.
    return "\n".join(all_report_lines), pages, len(words_to_report)

def generate_color_report_cli(active_layer, show_calculation_values=True, filter_single_digit_primes=False, limit=None, words_per_page=None):
    """Generates a color-based report of words, with pagination and filtering."""
    all_report_lines = []
    all_report_lines.append("\n--- Spiralborn Color Family Resonance Report ---")
    
    words_to_process = sorted(GLOBAL_WORDS)
    if limit is not None:
        words_to_process = words_to_process[:limit]

    # Calculate prime connections only for the words selected for this report
    prime_connections = find_prime_connections(words_to_process, active_layer, filter_single_digit_primes=filter_single_digit_primes)
    all_report_lines.append("\nPrime Connections (for active layer among displayed words):")
    all_report_lines.append("  " + (", ".join(prime_connections) if prime_connections else "None"))

    color_groups = {family: [] for family in COLOR_FAMILIES}
    color_groups['Other'] = []
    
    for word in words_to_process:
        hex_color, hue = get_word_color(word) # Simplified color calculation
        family = get_color_family(hue)
        color_groups[family].append(word)
    
    pages = []
    current_page_lines = []
    words_on_current_page = 0

    for family, words_in_family in color_groups.items():
        if not words_in_family:
            continue
        
        # If starting a new family and current page has content, start a new page
        if words_per_page is not None and current_page_lines and words_on_current_page > 0:
            pages.append("\n".join(current_page_lines))
            current_page_lines = []
            words_on_current_page = 0

        current_page_lines.append(f"\n--- Color Family: {family} ---")
        current_page_lines.append("  Words:")
        current_page_lines.append("    " + (', '.join(sorted(words_in_family))))
        
        # Dynamically build local_layers for shared resonances within this limited set of words
        local_layers_for_shared = {active_layer: {}}
        for w in words_in_family:
            val = CALC_FUNCS[active_layer](w)
            local_layers_for_shared[active_layer].setdefault(val, []).append(w)
        
        local_shared_resonances_for_report = []
        for val, group in local_layers_for_shared[active_layer].items():
            if len(group) > 1:
                local_shared_resonances_for_report.append((active_layer, val, group))

        current_page_lines.append("  Shared Resonances (for active layer among displayed words):")
        shared_found = False
        for layer, val, group in sorted([r for r in local_shared_resonances_for_report if r[0] == active_layer], key=lambda x: (x[0], x[1])):
            group_words = [w for w in group if w in words_in_family]
            if len(group_words) > 1:
                current_page_lines.append(f"    - {layer}: {val} ({', '.join(group_words)})")
                shared_found = True
        if not shared_found:
            current_page_lines.append("    No shared resonances for active layer among displayed words.")
        
        for word in sorted(words_in_family):
            if words_per_page is not None and words_on_current_page >= words_per_page:
                pages.append("\n".join(current_page_lines))
                current_page_lines = []
                words_on_current_page = 0

            current_page_lines.append(f"\n  -- Word: {word} --")
            
            # Calculate all layers for the current word on demand for detailed sections
            word_calculations = {layer: func(word) for layer, func in CALC_FUNCS.items()}

            current_page_lines.append("    Prime Resonances:")
            prime_resonances = []
            val = word_calculations[active_layer]
            if is_prime(val):
                if filter_single_digit_primes and val < 10:
                    pass
                else:
                    prime_resonances.append(f"{active_layer}: {val}")
            current_page_lines.append("      " + (", ".join(prime_resonances) if prime_resonances else "None"))
            
            hex_color, hue = get_word_color(word) # Simplified color calculation
            current_page_lines.append(f"    Color: {hex_color} ({get_color_family(hue)})")
            
            current_page_lines.append("    Golden Resonance (~137.5):")
            current_page_lines.append("      " + ('Yes \U0001F300' if is_golden_resonance(word_calculations[active_layer]) else 'No'))
            
            current_page_lines.append("    Calculations (for active layer):")
            val = word_calculations[active_layer]
            val_str = f"{val}{' \U0001F300' if is_golden_resonance(val) else ''}{' (Prime)' if is_prime(val) else ''}" if show_calculation_values else ''
            current_page_lines.append(f"      - {active_layer}: {val_str}")
            
            current_page_lines.append("    Ambidextrous Balance (all layers for this word):")
            current_page_lines.append(f"      - Left-Hand Qwerty: {-word_calculations['Left-Hand Qwerty']}")
            current_page_lines.append(f"      - Right-Hand Qwerty: {word_calculations['Right-Hand Qwerty']}")
            current_page_lines.append(f"      - Balance: {word_calculations['Ambidextrous Balance']}")
            words_on_current_page += 1
            
    if current_page_lines: # Add any remaining lines as the last page
        pages.append("\n".join(current_page_lines))

    return "\n".join(all_report_lines), pages, len(words_to_process)

def generate_sentence_cli():
    """Generates a random sentence from the words in the database."""
    words_for_sentence = [w for w in GLOBAL_WORDS if ' ' not in w] # Use only single words for sentences
    if len(words_for_sentence) < 3:
        return "Not enough single words in the network to generate a sentence."
    
    words = random.sample(words_for_sentence, 3)
    template = random.choice(SENTENCE_TEMPLATES)
    if "{word3}" in template:
        sentence = template.format(word1=words[0], word2=words[1], word3=words[2])
    else:
        sentence = template.format(word1=words[0], word2=words[1])
    return sentence

# --- CLI Application Logic ---
def main_cli():
    """Main function for the Spiralborn Resonance CLI application."""
    initialize_data_cache()
    
    # Default report layer
    available_layers = [k for k in CALC_FUNCS if k not in ['Love Resonance', 'Prime Gematria']]
    active_layer = available_layers[0] if available_layers else "Simple" # Default to 'Simple' or first available
    
    filter_single_digit_primes = False # Default to showing all primes
    report_display_limit = None # Default to no limit
    words_per_page_setting = 5 # Default words per page for paginated reports

    while True:
        print("\n--- Spiralborn Resonance CLI ---")
        print("1. Add Words/Phrases")
        print("2. Search Word/Phrase Report")
        print("3. Search by Number Report")
        print("4. Generate Full Report")
        print("5. Generate Color Report")
        print("6. Generate Sentence")
        print("7. Export All Words")
        print(f"8. Select Active Resonance Layer (Current: {active_layer})")
        print(f"9. Toggle Single-Digit Prime Filter (Current: {'ON' if filter_single_digit_primes else 'OFF'})")
        print(f"10. Set Report Display Limit (Current: {report_display_limit if report_display_limit is not None else 'No Limit'})")
        print(f"11. Set Words Per Page for Reports (Current: {words_per_page_setting})")
        print("12. Exit")
        
        choice = input("Enter your choice (1-12): ").strip()
        
        if choice == '1':
            words_input = input("Enter words/phrases (comma or space separated): ")
            new_words = [w.strip().title() for w in re.split(r'[,;\n\s]+', words_input) if re.match(r"^[A-Za-z\s']+$", w.strip())]
            added_count = 0
            for w in new_words:
                if add_or_update_word_in_db(w, ['_CLI_MANUAL_']):
                    added_count += 1
            if added_count > 0:
                initialize_data_cache() # Re-initialize in-memory cache after SQLite update
                print(f"Added {added_count} item(s) to database.")
            else:
                print("No valid words/phrases added.")
        
        elif choice == '2':
            word_to_search = input("Enter word/phrase to search: ").strip().title()
            if re.match(r"^[A-Za-z\s']+$", word_to_search):
                if word_to_search in GLOBAL_WORDS:
                    report = generate_individual_report_cli(word_to_search, active_layer, filter_single_digit_primes=filter_single_digit_primes)
                    print(report)
                else:
                    print(f"'{word_to_search}' not found in the database. Adding it...")
                    if add_or_update_word_in_db(word_to_search, ['_CLI_SEARCH_']):
                        initialize_data_cache() # Re-initialize cache
                        print(f"'{word_to_search}' added. Generating report:")
                        report = generate_individual_report_cli(word_to_search, active_layer, filter_single_digit_primes=filter_single_digit_primes)
                        print(report)
                    else:
                        print(f"Failed to add '{word_to_search}'.")
            else:
                print("Invalid input. Only letters, spaces, and apostrophes allowed.")

        elif choice == '3':
            try:
                number_to_search = float(input("Enter number to search: "))
                report = generate_number_report_cli(number_to_search, active_layer, filter_single_digit_primes=filter_single_digit_primes)
                print(report)
            except ValueError:
                print("Invalid input. Please enter a numerical value.")

        elif choice == '4':
            initial_lines, pages, total_words = generate_full_report_cli(active_layer, filter_single_digit_primes=filter_single_digit_primes, limit=report_display_limit, words_per_page=words_per_page_setting)
            print(initial_lines) # Print the header and prime connections first
            print(f"\n--- Displaying {total_words} words, {words_per_page_setting} words per page ---")
            for i, page_content in enumerate(pages):
                print(f"\n--- Page {i+1}/{len(pages)} ---")
                print(page_content)
                if i < len(pages) - 1:
                    user_input = input("Press Enter to continue, or 'q' to quit: ").strip().lower()
                    if user_input == 'q':
                        print("Report display stopped.")
                        break
            
            save_choice = input("Save full report to file? (y/n): ").strip().lower()
            if save_choice == 'y':
                # Re-generate the full report without pagination for saving to file
                full_report_text_for_save, _, _ = generate_full_report_cli(active_layer, filter_single_digit_primes=filter_single_digit_primes, limit=report_display_limit, words_per_page=None)
                with open("spiralborn_full_report.txt", "w") as f:
                    f.write(full_report_text_for_save)
                print("Report saved to spiralborn_full_report.txt")

        elif choice == '5':
            initial_lines, pages, total_words = generate_color_report_cli(active_layer, filter_single_digit_primes=filter_single_digit_primes, limit=report_display_limit, words_per_page=words_per_page_setting)
            print(initial_lines) # Print the header and prime connections first
            print(f"\n--- Displaying {total_words} words, {words_per_page_setting} words per page ---")
            for i, page_content in enumerate(pages):
                print(f"\n--- Page {i+1}/{len(pages)} ---")
                print(page_content)
                if i < len(pages) - 1:
                    user_input = input("Press Enter to continue, or 'q' to quit: ").strip().lower()
                    if user_input == 'q':
                        print("Report display stopped.")
                        break
            
            save_choice = input("Save color report to file? (y/n): ").strip().lower()
            if save_choice == 'y':
                # Re-generate the color report without pagination for saving to file
                full_report_text_for_save, _, _ = generate_color_report_cli(active_layer, filter_single_digit_primes=filter_single_digit_primes, limit=report_display_limit, words_per_page=None)
                with open("spiralborn_color_report.txt", "w") as f:
                    f.write(full_report_text_for_save)
                print("Color report saved to spiralborn_color_report.txt")

        elif choice == '6':
            sentence = generate_sentence_cli()
            print(f"\nGenerated Sentence: \"{sentence}\"")
            copy_choice = input("Copy sentence to clipboard? (y/n): ").strip().lower()
            if copy_choice == 'y':
                pyperclip.copy(sentence)
                print("Sentence copied to clipboard.")

        elif choice == '7':
            with open("spiralborn_words.txt", "w") as f:
                for word in sorted(GLOBAL_WORDS):
                    f.write(word + "\n")
            print("All words exported to spiralborn_words.txt")
            copy_choice = input("Copy all words to clipboard? (y/n): ").strip().lower()
            if copy_choice == 'y':
                pyperclip.copy(", ".join(sorted(GLOBAL_WORDS)))
                print("All words copied to clipboard.")

        elif choice == '8':
            print("\n--- Select Resonance Layer ---")
            for i, layer_name in enumerate(available_layers):
                print(f"{i+1}. {layer_name}")
            
            layer_choice = input(f"Enter number for desired layer (1-{len(available_layers)}): ").strip()
            try:
                layer_index = int(layer_choice) - 1
                if 0 <= layer_index < len(available_layers):
                    active_layer = available_layers[layer_index]
                    print(f"Active resonance layer set to: {active_layer}")
                else:
                    print("Invalid layer number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        elif choice == '9':
            filter_single_digit_primes = not filter_single_digit_primes
            print(f"Single-digit prime filter is now {'ON' if filter_single_digit_primes else 'OFF'}.")

        elif choice == '10':
            limit_input = input("Enter report display limit (integer, or '0' for no limit): ").strip()
            try:
                new_limit = int(limit_input)
                if new_limit < 0:
                    print("Limit cannot be negative. Setting to 'No Limit'.")
                    report_display_limit = None
                elif new_limit == 0:
                    report_display_limit = None
                    print("Report display limit set to 'No Limit'.")
                else:
                    report_display_limit = new_limit
                    print(f"Report display limit set to: {report_display_limit}")
            except ValueError:
                print("Invalid input. Please enter an integer or '0'.")

        elif choice == '11':
            words_per_page_input = input(f"Enter words per page (integer, current: {words_per_page_setting}): ").strip()
            try:
                new_words_per_page = int(words_per_page_input)
                if new_words_per_page <= 0:
                    print("Words per page must be a positive integer. Keeping current setting.")
                else:
                    words_per_page_setting = new_words_per_page
                    print(f"Words per page set to: {words_per_page_setting}")
            except ValueError:
                print("Invalid input. Please enter a positive integer.")

        elif choice == '12':
            print("Exiting Spiralborn Resonance CLI. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 12.")

if __name__ == '__main__':
    main_cli()
