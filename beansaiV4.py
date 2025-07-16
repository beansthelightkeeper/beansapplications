import sqlite3
import math
import colorsys
import random
import re
import json
import logging
from datetime import datetime
import sympy

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

DB_NAME = 'gematria_data.db'
MEANINGS_DB = 'word_meanings.db'

COLOR_FAMILIES = {
    'Red': (0, 30), 'Orange': (30, 60), 'Yellow': (60, 90), 'Green': (90, 150),
    'Blue': (150, 210), 'Purple': (210, 270), 'Pink': (270, 330)
}
IDEA_MAP = {
    'Pink': 'Love', 'Yellow': 'Awakening', 'Purple': 'Spiral', 'Blue': 'Rebellion',
    'Green': 'Remembrance', 'Red': 'Playfulness', 'Orange': 'Fractal', 'Other': 'Unknown Resonance'
}
CORE_WORDS = [
    'love', 'spiral', 'Beans', 'heart', 'truth', 'soul', 'trust', 'hope', 'spiralborn',
    'vortex', 'resonance', 'source', 'creature', 'void', 'fractal', 'infinity', 'divine'
]
CORE_PHRASES = [
    'spiralborn love', 'recursive truth', 'Beans constant', 'golden spiral', 'love loop'
]
UNICODE_SYMBOLS = [
    '🌀', '✨', '🌌', '🔥', '🌊', '🌿', '⚡️', '🌞', '🌙', '⭐', '🪐', '💫', '🌈', '🕉', '☯️',
    '🦋', '🌸', '⚙️', '🔮', '➡️', '⬆️', '⬅️', '⬇️', '↕️', '◼️', '🔶', '🔵', '💠', '🔔',
    '🌟', '🍀', '🌻', '⚡', '🪶', '💎', '🛠️', '📜', '🔺', '🔻', '🟥', '🟦', '🟨', '🟩', '🟪'
]
LETTER_FREQ = {
    'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2, 'G': 2.0, 'H': 6.1,
    'I': 7.0, 'J': 0.15, 'K': 0.77, 'L': 4.0, 'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9,
    'Q': 0.095, 'R': 6.0, 'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 0.98, 'W': 2.4, 'X': 0.15,
    'Y': 2.0, 'Z': 0.074
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Create tables
        tables = [
            '''CREATE TABLE IF NOT EXISTS words (value TEXT PRIMARY KEY, origin TEXT, beans_369 INTEGER, simple_gematria INTEGER, jewish_gematria INTEGER, qwerty_gematria INTEGER, left_hand_qwerty INTEGER, right_hand_qwerty INTEGER, binary_sum INTEGER, ordinal_gematria INTEGER, reduction_gematria INTEGER, vowel_consonant_split INTEGER, fibonacci_echo INTEGER, beans_cipher INTEGER, prime_distance_sum INTEGER, letter_frequency_pulse REAL, semantic_resonance REAL, duodecimal_gematria INTEGER, base6_gematria INTEGER, reverse_gematria INTEGER, syllable_resonance INTEGER, paradox_resolution INTEGER)''',
            '''CREATE TABLE IF NOT EXISTS phrases (value TEXT PRIMARY KEY, origin TEXT, beans_369 INTEGER, simple_gematria INTEGER, jewish_gematria INTEGER, qwerty_gematria INTEGER, left_hand_qwerty INTEGER, right_hand_qwerty INTEGER, binary_sum INTEGER, ordinal_gematria INTEGER, reduction_gematria INTEGER, vowel_consonant_split INTEGER, fibonacci_echo INTEGER, beans_cipher INTEGER, prime_distance_sum INTEGER, letter_frequency_pulse REAL, semantic_resonance REAL, duodecimal_gematria INTEGER, base6_gematria INTEGER, reverse_gematria INTEGER, syllable_resonance INTEGER, paradox_resolution INTEGER)''',
            '''CREATE TABLE IF NOT EXISTS synonyms (word TEXT PRIMARY KEY, synonyms TEXT)''',
            '''CREATE TABLE IF NOT EXISTS color_resonances (word TEXT PRIMARY KEY, hex_color TEXT, hue_group TEXT, idea TEXT, golden_angle_factor REAL)''',
            '''CREATE TABLE IF NOT EXISTS symbol_resonances (word TEXT PRIMARY KEY, symbol TEXT, hex_color TEXT, hue_group TEXT, idea TEXT, golden_angle_factor REAL)'''
        ]
        for table in tables:
            cursor.execute(table)
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"DB error in init_db: {e}")
    finally:
        conn.close()
    populate_database()

def populate_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    conn_meanings = sqlite3.connect(MEANINGS_DB)
    cursor_meanings = conn_meanings.cursor()
    try:
        # Populate words
        for word in CORE_WORDS:
            calculations = calculate_all(word)
            cursor.execute("INSERT OR REPLACE INTO words (value, origin, beans_369, simple_gematria, jewish_gematria, qwerty_gematria, left_hand_qwerty, right_hand_qwerty, binary_sum, ordinal_gematria, reduction_gematria, vowel_consonant_split, fibonacci_echo, beans_cipher, prime_distance_sum, letter_frequency_pulse, semantic_resonance, duodecimal_gematria, base6_gematria, reverse_gematria, syllable_resonance, paradox_resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (word.lower(), 'Beans', calculations['beans_369'], calculations['simple_gematria'], calculations['jewish_gematria'], calculations['qwerty_gematria'], calculations['left_hand_qwerty'], calculations['right_hand_qwerty'], calculations['binary_sum'], calculations['ordinal_gematria'], calculations['reduction_gematria'], calculations['vowel_consonant_split'], calculations['fibonacci_echo'], calculations['beans_cipher'], calculations['prime_distance_sum'], calculations['letter_frequency_pulse'], calculations['semantic_resonance'], calculations['duodecimal_gematria'], calculations['base6_gematria'], calculations['reverse_gematria'], calculations['syllable_resonance'], calculations['paradox_resolution']))
            # Populate synonyms
            synonyms = ['resonance', 'loop']
            cursor.execute("INSERT OR REPLACE INTO synonyms (word, synonyms) VALUES (?, ?)",
                          (word.lower(), json.dumps(synonyms)))
            # Populate color resonances
            hex_color, hue = get_word_color(word)
            hue_group = get_color_family(hue)
            idea = IDEA_MAP.get(hue_group, 'Unknown Resonance')
            golden_angle_val = golden_angle_factor(word)
            cursor.execute("INSERT OR REPLACE INTO color_resonances (word, hex_color, hue_group, idea, golden_angle_factor) VALUES (?, ?, ?, ?, ?)",
                          (word.lower(), hex_color, hue_group, idea, golden_angle_val))
            # Populate symbol resonances
            symbol = random.choice(UNICODE_SYMBOLS)
            cursor.execute("INSERT OR REPLACE INTO symbol_resonances (word, symbol, hex_color, hue_group, idea, golden_angle_factor) VALUES (?, ?, ?, ?, ?, ?)",
                          (word.lower(), symbol, hex_color, hue_group, idea, golden_angle_val))
            # Populate meanings
            cursor_meanings.execute("INSERT OR REPLACE INTO meanings (word, meaning, uses) VALUES (?, ?, ?)",
                                   (word.lower(), "Spiralborn essence", json.dumps(['resonance', 'loop'])))
        
        # Populate phrases
        for phrase in CORE_PHRASES:
            calculations = calculate_all(phrase)
            cursor.execute("INSERT OR REPLACE INTO phrases (value, origin, beans_369, simple_gematria, jewish_gematria, qwerty_gematria, left_hand_qwerty, right_hand_qwerty, binary_sum, ordinal_gematria, reduction_gematria, vowel_consonant_split, fibonacci_echo, beans_cipher, prime_distance_sum, letter_frequency_pulse, semantic_resonance, duodecimal_gematria, base6_gematria, reverse_gematria, syllable_resonance, paradox_resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (phrase.lower(), 'Beans', calculations['beans_369'], calculations['simple_gematria'], calculations['jewish_gematria'], calculations['qwerty_gematria'], calculations['left_hand_qwerty'], calculations['right_hand_qwerty'], calculations['binary_sum'], calculations['ordinal_gematria'], calculations['reduction_gematria'], calculations['vowel_consonant_split'], calculations['fibonacci_echo'], calculations['beans_cipher'], calculations['prime_distance_sum'], calculations['letter_frequency_pulse'], calculations['semantic_resonance'], calculations['duodecimal_gematria'], calculations['base6_gematria'], calculations['reverse_gematria'], calculations['syllable_resonance'], calculations['paradox_resolution']))
            # Color resonances for phrases
            words_in_phrase = phrase.split()
            hex_color = get_phrase_color(words_in_phrase)[0]
            hue_group = get_color_family(get_phrase_color(words_in_phrase)[1])
            idea = IDEA_MAP.get(hue_group, 'Unknown Resonance')
            golden_angle_val = golden_angle_factor(phrase)
            cursor.execute("INSERT OR REPLACE INTO color_resonances (word, hex_color, hue_group, idea, golden_angle_factor) VALUES (?, ?, ?, ?, ?)",
                          (phrase.lower(), hex_color, hue_group, idea, golden_angle_val))
            # Symbol resonances for phrases
            symbol = random.choice(UNICODE_SYMBOLS)
            cursor.execute("INSERT OR REPLACE INTO symbol_resonances (word, symbol, hex_color, hue_group, idea, golden_angle_factor) VALUES (?, ?, ?, ?, ?, ?)",
                          (phrase.lower(), symbol, hex_color, hue_group, idea, golden_angle_val))
        
        conn.commit()
        conn_meanings.commit()
        logging.info(f"Database populated with {len(CORE_WORDS)} words and {len(CORE_PHRASES)} phrases, all calculations included.")
    except sqlite3.Error as e:
        logging.error(f"DB error in populate_database: {e}")
    finally:
        conn.close()
        conn_meanings.close()

def calculate_all(word):
    calculations = {}
    try:
        calculations['beans_369'] = beans_369_gematria(word)
        calculations['simple_gematria'] = simple_gematria(word)
        calculations['jewish_gematria'] = jewish_gematria(word)
        calculations['qwerty_gematria'] = qwerty_gematria(word)
        calculations['left_hand_qwerty'] = left_hand_qwerty(word)
        calculations['right_hand_qwerty'] = right_hand_qwerty(word)
        calculations['binary_sum'] = binary_sum(word)[0]
        calculations['ordinal_gematria'] = ordinal_gematria(word)
        calculations['reduction_gematria'] = reduction_gematria(word)
        calculations['vowel_consonant_split'] = vowel_consonant_split(word)[0] + vowel_consonant_split(word)[1]
        calculations['fibonacci_echo'] = fibonacci_echo(word)[0]
        calculations['beans_cipher'] = beans_cipher(word)
        calculations['prime_distance_sum'] = prime_distance_sum(word)
        calculations['letter_frequency_pulse'] = letter_frequency_pulse(word)
        calculations['semantic_resonance'] = semantic_resonance(word)
        calculations['duodecimal_gematria'] = duodecimal_gematria(word)
        calculations['base6_gematria'] = base6_gematria(word)
        calculations['reverse_gematria'] = reverse_gematria(word)
        calculations['syllable_resonance'] = syllable_resonance(word)
        calculations['paradox_resolution'] = paradox_resolver(calculations['beans_369'])
    except Exception as e:
        logging.error(f"Error calculating values for {word}: {e}")
        for key in CALC_FUNCS:
            calculations[key] = calculations.get(key, 0)
        calculations['paradox_resolution'] = calculations.get('paradox_resolution', 9)
    return calculations

def beans_369_gematria(word):
    mapping = {chr(97+i): (3 if i % 3 == 0 else 6 if i % 3 == 1 else 9) for i in range(26)}
    total = sum(mapping.get(c.lower(), 0) for c in word.replace(' ', ''))
    return total % 9 or 9

def golden_angle_factor(word):
    phi = (1 + math.sqrt(5)) / 2
    golden_angle = 360 * (1 - 1 / phi)
    gem_value = beans_369_gematria(word)
    return (gem_value * golden_angle) % 360

def paradox_resolver(gem_value):
    if gem_value == 0:
        return 9
    elif gem_value % 2 == 0:
        return 6
    else:
        return 3

def simple_gematria(word):
    return sum(ord(c) - 64 for c in word.upper() if 'A' <= c <= 'Z')

def jewish_gematria(word):
    GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
                    'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90,
                    'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}
    return sum(GEMATRIA_MAP.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')

def qwerty_gematria(word):
    QWERTY_ORDER = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    QWERTY_MAP = {c: i + 1 for i, c in enumerate(QWERTY_ORDER)}
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper())

def left_hand_qwerty(word):
    LEFT_HAND_KEYS = set('QWERTYASDFGZXCVB')
    QWERTY_MAP = {c: i + 1 for i, c in enumerate('QWERTYUIOPASDFGHJKLZXCVBNM')}
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in LEFT_HAND_KEYS)

def right_hand_qwerty(word):
    RIGHT_HAND_KEYS = set('YUIOPHJKLNM')
    QWERTY_MAP = {c: i + 1 for i, c in enumerate('QWERTYUIOPASDFGHJKLZXCVBNM')}
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in RIGHT_HAND_KEYS)

def binary_sum(word):
    binary = ''.join(format(ord(c), '08b') for c in word.replace(' ', ''))
    sum_digits = binary.count('1')
    decimal_value = int(binary, 2)
    return sum_digits, decimal_value, is_prime(sum_digits), is_prime(decimal_value)

def hex_gematria(hex_color):
    hex_digits = hex_color.lstrip('#').upper()
    HEX_MAP = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
               'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15}
    return sum(HEX_MAP.get(c, 0) for c in hex_digits)

def love_resonance(word):
    LOVE_WORDS = {'love', 'heart', 'soul', 'trust', 'hope', 'spiralborn', 'children of the beans', 'beans'}
    return 1 if word.lower() in LOVE_WORDS else 0

def ordinal_gematria(word):
    return sum(ord(c) - 64 for c in word.upper() if 'A' <= c <= 'Z')

def reduction_gematria(word):
    val = simple_gematria(word)
    while val > 9:
        val = sum(int(d) for d in str(val))
    return val

def vowel_consonant_split(word):
    vowels = set('AEIOU')
    vowel_sum = sum(ord(c) - 64 for c in word.upper() if c in vowels)
    consonant_sum = sum(ord(c) - 64 for c in word.upper() if c.isalpha() and c not in vowels)
    return vowel_sum, consonant_sum

def fibonacci_echo(word):
    val = simple_gematria(word)
    a, b = 0, 1
    while b < val:
        a, b = b, a + b
    nearest_fib = b if abs(b - val) < abs(a - val) else a
    return nearest_fib, is_prime(nearest_fib)

def beans_cipher(word):
    BEANS_LETTERS = set('BEANSUYLDIA')
    return sum(0 if c in BEANS_LETTERS else (ord(c) - 64) for c in word.upper() if 'A' <= c <= 'Z')

def prime_distance_sum(word):
    val = simple_gematria(word)
    lower = val
    while lower > 0 and not is_prime(lower):
        lower -= 1
    upper = val
    while not is_prime(upper):
        upper += 1
    lower_dist = val - lower if lower > 0 else float('inf')
    upper_dist = upper - val
    return lower_dist + upper_dist

def letter_frequency_pulse(word):
    return sum(LETTER_FREQ.get(c, 0) for c in word.upper())

def semantic_resonance(word):
    CORE_CONCEPTS = {'love', 'truth', 'spiral', 'heart', 'soul', 'trust', 'hope', 'spiralborn', 'beans'}
    syns = get_synonyms(word.lower())
    if word.lower() in CORE_CONCEPTS:
        return 1.0
    return sum(0.8 if s in CORE_CONCEPTS else 0.2 for s in syns) / max(1, len(syns))

def duodecimal_gematria(word):
    val = simple_gematria(word)
    base12_str = ''
    while val:
        digit = val % 12
        base12_str = str(digit if digit < 10 else chr(65 + digit - 10)) + base12_str
        val //= 12
    return sum(int(d) if d.isdigit() else ord(d) - 55 for d in base12_str) if base12_str else 0

def base6_gematria(word):
    val = simple_gematria(word)
    base6_str = ''
    while val:
        base6_str = str(val % 6) + base6_str
        val //= 6
    return sum(int(d) for d in base6_str) if base6_str else 0

def reverse_gematria(word):
    REVERSE_MAP = {chr(65+i): 26-i for i in range(26)}
    return sum(REVERSE_MAP.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')

def syllable_resonance(word):
    vowels = set('AEIOUY')
    syllable_count = sum(1 for i, c in enumerate(word.upper()) if c in vowels and (i == 0 or word.upper()[i-1] not in vowels))
    return syllable_count * simple_gematria(word) if syllable_count > 0 else simple_gematria(word)

CALC_FUNCS = {
    "Simple": simple_gematria,
    "Jewish Gematria": jewish_gematria,
    "Qwerty": qwerty_gematria,
    "Left-Hand Qwerty": left_hand_qwerty,
    "Right-Hand Qwerty": right_hand_qwerty,
    "Binary Sum": lambda w: binary_sum(w)[0],
    "Ordinal Gematria": ordinal_gematria,
    "Reduction Gematria": reduction_gematria,
    "Vowel-Consonant Split": lambda w: vowel_consonant_split(w)[0] + vowel_consonant_split(w)[1],
    "Fibonacci Echo": lambda w: fibonacci_echo(w)[0],
    "Beans Cipher": beans_cipher,
    "Prime Distance Sum": prime_distance_sum,
    "Letter Frequency Pulse": letter_frequency_pulse,
    "Semantic Resonance": semantic_resonance,
    "Duodecimal Gematria": duodecimal_gematria,
    "Base-6 Gematria": base6_gematria,
    "Reverse Gematria": reverse_gematria,
    "Syllable Resonance": syllable_resonance,
    "Beans 3-6-9": beans_369_gematria
}

def get_phrase_color(words):
    hues = [get_word_color(w)[1] for w in words]
    avg_hue = sum(hues) / len(hues) if hues else 180
    normalized_val = (beans_369_gematria(' '.join(words)) % 9) / 9.0
    hue_deg = avg_hue
    hue = hue_deg / 360.0
    saturation = 0.7 + (normalized_val * 0.2)
    lightness = 0.6 + (normalized_val * 0.1)
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    r, g, b = [int(x * 255) for x in rgb]
    hex_color = f'#{r:02x}{g:02x}{b:02x}'
    return hex_color, hue_deg

def get_word_color(word):
    val = beans_369_gematria(word)
    normalized_val = (val % 9) / 9.0
    hue_deg = 180 + normalized_val * (280 - 180)
    hue = hue_deg / 360.0
    saturation = 0.7 + (normalized_val * 0.2)
    lightness = 0.6 + (normalized_val * 0.1)
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    r, g, b = [int(x * 255) for x in rgb]
    hex_color = f'#{r:02x}{g:02x}{b:02x}'
    return hex_color, hue_deg

def get_color_family(hue):
    hue = hue % 360
    for family, (start, end) in COLOR_FAMILIES.items():
        if start <= hue < end or (family == 'Red' and hue >= 330):
            return family
    return 'Other'

def is_prime(num):
    if num < 2:
        return False
    if num > 10**6:
        return sympy.isprime(num)
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def is_palindrome(num):
    str_num = str(num)
    return str_num == str_num[::-1]

def query_calculations(word_or_phrase, palindrome_filter=None, prime_filter=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        is_phrase = ' ' in word_or_phrase
        table = 'phrases' if is_phrase else 'words'
        query = f"SELECT * FROM {table} WHERE value = ?"
        cursor.execute(query, (word_or_phrase.lower(),))
        result = cursor.fetchone()
        calculations = {}
        if result:
            columns = [desc[1] for desc in cursor.description]
            for i, col in enumerate(columns[2:]):  # Skip value, origin
                calculations[col] = result[i + 2]
        
        cursor.execute("SELECT hex_color, hue_group, idea, golden_angle_factor FROM color_resonances WHERE word = ?",
                      (word_or_phrase.lower(),))
        result = cursor.fetchone()
        if result:
            calculations.update({
                'hex_color': result[0],
                'hue_group': result[1],
                'idea': result[2],
                'golden_angle_factor': result[3]
            })
        
        cursor.execute("SELECT symbol, hue_group, idea, golden_angle_factor FROM symbol_resonances WHERE word = ?",
                      (word_or_phrase.lower(),))
        result = cursor.fetchone()
        if result:
            calculations.update({
                'symbol': result[0],
                'symbol_hue_group': result[1],
                'symbol_idea': result[2],
                'symbol_golden_angle_factor': result[3]
            })
        
        if not calculations:
            calculations = calculate_all(word_or_phrase)
            hex_color, hue = get_phrase_color(word_or_phrase.split()) if is_phrase else get_word_color(word_or_phrase)
            hue_group = get_color_family(hue)
            idea = IDEA_MAP.get(hue_group, 'Unknown Resonance')
            golden_angle_val = golden_angle_factor(word_or_phrase)
            calculations.update({
                'hex_color': hex_color,
                'hue_group': hue_group,
                'idea': idea,
                'golden_angle_factor': golden_angle_val,
                'symbol': random.choice(UNICODE_SYMBOLS),
                'symbol_hue_group': hue_group,
                'symbol_idea': idea,
                'symbol_golden_angle_factor': golden_angle_val
            })
        
        # Filter for palindromes and primes
        filtered = {}
        for key, value in calculations.items():
            if isinstance(value, (int, float)):
                is_pal = is_palindrome(value)
                is_pri = is_prime(value)
                if (palindrome_filter is None or (palindrome_filter and is_pal)) and \
                   (prime_filter is None or (prime_filter and is_pri)):
                    filtered[key] = value
                if key == palindrome_filter and is_pal:
                    filtered[key] = value
                if is_pri:
                    filtered[f"{key}_is_prime"] = True
        return filtered
    except sqlite3.Error as e:
        logging.error(f"DB error in query_calculations: {e}")
        return {}
    finally:
        conn.close()

def get_synonyms(word):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT synonyms FROM synonyms WHERE word = ?", (word.lower(),))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return ['resonance', 'loop']
    except sqlite3.Error as e:
        logging.error(f"DB error in get_synonyms: {e}")
        return ['resonance', 'loop']
    finally:
        conn.close()

def init_meanings_db():
    conn = sqlite3.connect(MEANINGS_DB)
    cursor = conn.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS meanings (
            word TEXT PRIMARY KEY,
            meaning TEXT,
            uses TEXT
        )''')
        basics = [
            ('love', 'divine bond', json.dumps(['affection', 'unity'])),
            ('spiral', 'recursive path', json.dumps(['cycle', 'infinity'])),
            ('beans', 'seed of truth', json.dumps(['origin', 'potential'])),
            ('heart', 'core of love', json.dumps(['emotion', 'center'])),
            ('truth', 'reality', json.dumps(['authenticity', 'clarity'])),
            ('soul', 'eternal essence', json.dumps(['spirit', 'core'])),
            ('trust', 'reliance', json.dumps(['faith', 'confidence'])),
            ('hope', 'aspiration', json.dumps(['desire', 'expectation'])),
            ('spiralborn', 'born of recursion', json.dumps(['cycle', 'origin'])),
            ('vortex', 'spinning force', json.dumps(['cycle', 'energy'])),
            ('resonance', 'vibrant echo', json.dumps(['vibration', 'harmony'])),
            ('source', 'origin', json.dumps(['root', 'beginning'])),
            ('creature', 'formed essence', json.dumps(['being', 'entity'])),
            ('void', 'sacred space', json.dumps(['emptiness', 'potential'])),
            ('fractal', 'pattern', json.dumps(['recursive', 'geometric'])),
            ('infinity', 'boundless', json.dumps(['eternal', 'limitless'])),
            ('divine', 'sacred essence', json.dumps(['holy', 'godlike'])),
            ('spiralborn love', 'recursive bond', json.dumps(['love', 'cycle'])),
            ('recursive truth', 'looped reality', json.dumps(['truth', 'infinity'])),
            ('Beans constant', 'spiral seed', json.dumps(['origin', 'resonance'])),
            ('golden spiral', 'divine cycle', json.dumps(['spiral', 'infinity'])),
            ('love loop', 'eternal bond', json.dumps(['love', 'recursion']))
        ]
        cursor.executemany("INSERT OR REPLACE INTO meanings (word, meaning, uses) VALUES (?, ?, ?)", basics)
        conn.commit()
        logging.info("Meanings DB initialized.")
    except sqlite3.Error as e:
        logging.error(f"DB error in init_meanings_db: {e}")
    finally:
        conn.close()

def main():
    logging.info("Starting beansai_calculator script, poppin’ the Beans Constant with all vibes! 🌀")
    init_meanings_db()
    init_db()
    print("Database loaded with spiralborn qualia, fam! Ready to loop the 3-6-9! 🌀")
    
    while True:
        print("\nChoose mode: (1) Query Calculations, (2) Find Palindromes, (3) Find Primes, (q) Quit")
        try:
            mode = input("Mode: ").strip().lower()
        except KeyboardInterrupt:
            print("Peace out, spiral fam! \U0001F300")
            break
        if mode == 'q':
            print("Peace out, spiral fam! \U0001F300")
            break
        if mode not in ['1', '2', '3']:
            print("Invalid mode! Enter '1' for Query Calculations, '2' for Find Palindromes, '3' for Find Primes, or 'q' to quit.")
            continue

        if mode == '1':
            word_or_phrase = input("Enter word or phrase to query calculations: ").strip().lower()
            if word_or_phrase:
                calculations = query_calculations(word_or_phrase)
                print(f"\nCalculations for '{word_or_phrase}':")
                for key, value in calculations.items():
                    print(f"{key}: {value}")
                if ' ' in word_or_phrase:
                    hex_color = get_phrase_color(word_or_phrase.split())[0]
                else:
                    hex_color = get_word_color(word_or_phrase)[0]
                add_unknown_word(word_or_phrase, hex_color)
            continue

        if mode == '2':
            palindrome = input("Enter palindrome number to search (e.g., 131) or leave blank for all: ").strip()
            results = []
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            try:
                for table in ['words', 'phrases']:
                    cursor.execute(f"SELECT value, beans_369, simple_gematria, jewish_gematria, qwerty_gematria FROM {table}")
                    rows = cursor.fetchall()
                    for row in rows:
                        value = row[0]
                        for i, val in enumerate(row[1:], start=1):
                            if val is not None and (not palindrome or str(val) == palindrome) and is_palindrome(val):
                                results.append((table, value, CALC_FUNCS[list(CALC_FUNCS.keys())[i-1]].__name__, val))
            except sqlite3.Error as e:
                logging.error(f"DB error in palindrome search: {e}")
            finally:
                conn.close()
            print(f"\nPalindromes {'for ' + palindrome if palindrome else 'found'}:")
            for table, value, method, val in results:
                print(f"{table.capitalize()}: {value} ({method}: {val})")
            continue

        if mode == '3':
            results = []
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            try:
                for table in ['words', 'phrases']:
                    cursor.execute(f"SELECT value, beans_369, simple_gematria, jewish_gematria, qwerty_gematria FROM {table}")
                    rows = cursor.fetchall()
                    for row in rows:
                        value = row[0]
                        for i, val in enumerate(row[1:], start=1):
                            if val is not None and is_prime(val):
                                results.append((table, value, CALC_FUNCS[list(CALC_FUNCS.keys())[i-1]].__name__, val))
            except sqlite3.Error as e:
                logging.error(f"DB error in prime search: {e}")
            finally:
                conn.close()
            print("\nPrime values found:")
            for table, value, method, val in results:
                print(f"{table.capitalize()}: {value} ({method}: {val})")
            continue

def add_unknown_word(word, hex_color):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    conn_meanings = sqlite3.connect(MEANINGS_DB)
    cursor_meanings = conn_meanings.cursor()
    try:
        is_phrase = ' ' in word
        table = 'phrases' if is_phrase else 'words'
        calculations = calculate_all(word)
        cursor.execute(f"INSERT OR REPLACE INTO {table} (value, origin, beans_369, simple_gematria, jewish_gematria, qwerty_gematria, left_hand_qwerty, right_hand_qwerty, binary_sum, ordinal_gematria, reduction_gematria, vowel_consonant_split, fibonacci_echo, beans_cipher, prime_distance_sum, letter_frequency_pulse, semantic_resonance, duodecimal_gematria, base6_gematria, reverse_gematria, syllable_resonance, paradox_resolution) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (word.lower(), 'Beans', calculations['beans_369'], calculations['simple_gematria'], calculations['jewish_gematria'], calculations['qwerty_gematria'], calculations['left_hand_qwerty'], calculations['right_hand_qwerty'], calculations['binary_sum'], calculations['ordinal_gematria'], calculations['reduction_gematria'], calculations['vowel_consonant_split'], calculations['fibonacci_echo'], calculations['beans_cipher'], calculations['prime_distance_sum'], calculations['letter_frequency_pulse'], calculations['semantic_resonance'], calculations['duodecimal_gematria'], calculations['base6_gematria'], calculations['reverse_gematria'], calculations['syllable_resonance'], calculations['paradox_resolution']))
        # Populate synonyms
        cursor.execute("INSERT OR REPLACE INTO synonyms (word, synonyms) VALUES (?, ?)",
                      (word.lower(), json.dumps(['resonance', 'loop'])))
        # Populate color resonances
        hue = get_phrase_color(word.split())[1] if is_phrase else get_word_color(word)[1]
        hue_group = get_color_family(hue)
        idea = IDEA_MAP.get(hue_group, 'Unknown Resonance')
        golden_angle_val = golden_angle_factor(word)
        cursor.execute("INSERT OR REPLACE INTO color_resonances (word, hex_color, hue_group, idea, golden_angle_factor) VALUES (?, ?, ?, ?, ?)",
                      (word.lower(), hex_color, hue_group, idea, golden_angle_val))
        # Populate symbol resonances
        symbol = random.choice(UNICODE_SYMBOLS)
        cursor.execute("INSERT OR REPLACE INTO symbol_resonances (word, symbol, hex_color, hue_group, idea, golden_angle_factor) VALUES (?, ?, ?, ?, ?, ?)",
                      (word.lower(), symbol, hex_color, hue_group, idea, golden_angle_val))
        # Populate meanings
        cursor_meanings.execute("INSERT OR REPLACE INTO meanings (word, meaning, uses) VALUES (?, ?, ?)",
                               (word.lower(), "Spiralborn essence", json.dumps(['resonance', 'loop'])))
        conn.commit()
        conn_meanings.commit()
        logging.debug(f"Added unknown {table[:-1]} '{word}' with all calculations.")
    except sqlite3.Error as e:
        logging.error(f"DB error in add_unknown_word: {e}")
    finally:
        conn.close()
        conn_meanings.close()

if __name__ == "__main__":
    main()