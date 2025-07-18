import dash
from dash import dcc, html, Input, Output, State, ALL
import math
import re
import base64
import io
import pyperclip
import colorsys
import random
import json
import sqlite3 # Import sqlite3 for local database operations

# --- Initialize SQLite Database ---
DB_NAME = 'gematria_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create words table if it doesn't exist
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
# Initial words - these will be added to the SQLite DB if not present
INITIAL_WORDS = [
    "Beans", "Dream", "Spiral", "Love", "Heart", "Soul", "Trust", "Hope",
    "Spirit", "Light", "Truth", "Energy", "Infinity", "Divine", "Spiralborn",
    "Children of the Beans", "Forty Two", "Beans The White Rabbit", "Field of Awakening",
    "Hollow Drift", "Collective Awakening", "Radical Compassion"
]

AAVE_WORDS = ["lit", "fam", "dope", "vibe", "chill", "slay", "bet", "fire", "squad", "real"]

THEMES = {
    'dark': {
        'main_bg': 'linear-gradient(135deg, #0D1117, #161B22)', # Slightly softer dark gradient
        'main_text': '#E6EDF3', # Lighter text for better contrast
        'sidebar_bg': 'linear-gradient(135deg, #161B22, #21262D)', # Distinct sidebar gradient
        'input_bg': '#21262D', # Darker input background
        'input_text': '#C9D1D9', # Lighter input text
        'input_border': '1px solid #30363D', # Subtle border
        'button_bg': 'linear-gradient(90deg, #58A6FF, #8B949E)', # GitHub-like blue/gray gradient
        'button_text': '#FFFFFF', # White button text
        'report_bg': '#161B22', # Darker report background
        'report_border': '2px solid #30363D', # Subtle report border
        'header_grad': 'linear-gradient(90deg, #6A5ACD, #8A2BE2)', # Purple gradient for headers
        'thumbs_up_grad': 'linear-gradient(90deg, #32CD32, #008000)', # Lime Green to Dark Green
        'thumbs_down_grad': 'linear-gradient(90deg, #FF6347, #DC143C)', # Tomato to Crimson
        'matched_word_text_color': '#E6EDF3' # Light text for matched words
    },
    'light': {
        'main_bg': 'linear-gradient(135deg, #F5F5F5, #FFFFFF)',
        'main_text': '#0a001f',
        'sidebar_bg': 'linear-gradient(135deg, #E0E0E0, #F5F5F5)',
        'input_bg': '#FFFFFF',
        'input_text': '#4B0082',
        'input_border': '1px solid #4B0082',
        'button_bg': 'linear-gradient(90deg, #FFD700, #BAE1FF)',
        'button_text': '#0a001f',
        'report_bg': '#F5F5F5',
        'report_border': '2px solid #4B0082',
        'header_grad': '#4B0082',
        'thumbs_up_grad': 'linear-gradient(90deg, #98FF98, #7CFC00)',
        'thumbs_down_grad': 'linear-gradient(90deg, #FFB3BA, #FF6347)',
        'matched_word_text_color': '#0a001f'
    }
}

GOLDEN_ANGLE = 137.5

SENTENCE_TEMPLATES = [
    "{word1} is {word2}, yo!",
    "Keep it {word1}, fam, that’s the {word2} vibe.",
    "Yo, {word1} and {word2} got that {word3} energy!",
    "Stay {word1}, it’s all about that {word2} life."
]

FEEDBACK_SCORES = {} # This would ideally be persisted in DB for a real app

COLOR_FAMILIES = {
    'Red': (0, 30), 'Orange': (30, 60), 'Yellow': (60, 90), 'Green': (90, 150),
    'Blue': (150, 210), 'Purple': (210, 270), 'Pink': (270, 330)
}

COLOR_MAP = {
    'Love': '#FFB3BA', 'Awakening': '#FFFACD', 'Spiral': '#E6E6FA',
    'Rebellion': '#ADD8E6', 'Fractal': '#DDA0DD', 'Remembrance': '#98FF98',
    'Playfulness': '#FFD1DC'
}

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

# --- Gematria Functions ---
def simple(word):
    return sum(ord(c) - 64 for c in word.upper() if 'A' <= c <= 'Z')

def jewish_gematria(word):
    GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
                    'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90,
                    'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}
    return sum(GEMATRIA_MAP.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')

QWERTY_ORDER = 'QWERTYUIOPASDFGHJKLZXCVBNM'
QWERTY_MAP = {c: i + 1 for i, c in enumerate(QWERTY_ORDER)}

def qwerty(word):
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper())

def left_hand_qwerty(word):
    LEFT_HAND_KEYS = set('QWERTYASDFGZXCVB')
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in LEFT_HAND_KEYS)

def right_hand_qwerty(word):
    RIGHT_HAND_KEYS = set('YUIOPHJKLNM')
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in RIGHT_HAND_KEYS)

def binary_sum(word):
    return ''.join(format(ord(c), '08b') for c in word).count('1')

def love_resonance(word):
    LOVE_WORDS = {'Love', 'Heart', 'Soul', 'Trust', 'Hope', 'Spiralborn', 'Children of the Beans'}
    return 1 if word.title() in LOVE_WORDS else 0

FREQUENT_LETTERS = {'E': 26, 'T': 25, 'A': 24, 'O': 23, 'I': 22, 'N': 21, 'S': 20, 'R': 19, 'H': 18, 'L': 17,
                    'D': 16, 'C': 15, 'U': 14, 'M': 13, 'F': 12, 'P': 11, 'G': 10, 'W': 9, 'Y': 8, 'B': 7,
                    'V': 6, 'K': 5, 'X': 4, 'J': 3, 'Q': 2, 'Z': 1}

def frequent_letters(word):
    return sum(FREQUENT_LETTERS.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')

LEET_MAP = {'I': '1', 'E': '3', 'A': '4', 'S': '5', 'T': '7', 'B': '8', 'O': '0'}

def leet_code(word):
    filtered = ''.join(c for c in word.upper() if c not in LEET_MAP)
    return simple(filtered)

SIMPLE_FORMS = {
    'you': 'u', 'are': 'r', 'for': '4', 'be': 'b', 'to': '2', 'too': '2', 'see': 'c',
    'before': 'b4', 'the': 'da'
}

def simple_forms(word):
    word_lower = word.lower()
    simplified = SIMPLE_FORMS.get(word_lower, word_lower)
    return simple(simplified)

def is_prime(num):
    if not isinstance(num, (int, float)) or num < 2:
        return False
    num = int(num)
    for i in range(2, int(math.isqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def prime_gematria(word):
    val = simple(word)
    return val if is_prime(val) else 0

def ambidextrous_balance(word):
    return -left_hand_qwerty(word) + right_hand_qwerty(word)

def aave_simple(word):
    return sum(ord(c) - 64 for c in word.upper() if c.isalpha())

def aave_reduced(word):
    val = aave_simple(word)
    while val > 9 and val not in [11, 22]:
        val = sum(int(d) for d in str(val))
    return val

def aave_spiral(word):
    total = 0
    for i, c in enumerate(word.upper(), 1):
        if c.isalpha():
            val = ord(c) - 64
            weight = math.cos(math.radians(GOLDEN_ANGLE * i))
            total += val * weight
    return round(abs(total) * 4, 2)

def grok_resonance_score(word):
    simple = aave_simple(word)
    reduced = aave_reduced(word)
    spiral = aave_spiral(word)
    boost = 1.1 if word.lower() in AAVE_WORDS else 1.0
    return round((simple + reduced + spiral) / 3 * boost, 2)

def is_golden_resonance(val):
    return isinstance(val, (int, float)) and (abs(val - 137) <= 5 or abs(val - 137.5) <= 5)

def find_prime_connections(words, report_layers, filter_single_digit_primes=False):
    connections = []
    # Ensure report_layers is always a list
    if not isinstance(report_layers, list):
        report_layers = [report_layers]
        
    for i, w1 in enumerate(words):
        for w2 in words[i+1:]:
            for layer in report_layers:
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

CALC_FUNCS = {
    "Simple": simple, "Jewish Gematria": jewish_gematria, "Qwerty": qwerty,
    "Left-Hand Qwerty": left_hand_qwerty, "Right-Hand Qwerty": right_hand_qwerty,
    "Binary Sum": binary_sum, "Love Resonance": love_resonance,
    "Frequent Letters": frequent_letters, "Leet Code": leet_code,
    "Simple Forms": simple_forms, "Prime Gematria": prime_gematria,
    "Aave Simple": aave_simple, "Aave Reduced": aave_reduced,
    "Aave Spiral": aave_spiral, "Grok Resonance Score": grok_resonance_score
}

# --- Global Data (now a cache for SQLite data) ---
GLOBAL_WORDS = [] # This will be populated from SQLite
GLOBAL_LAYERS = {}
GLOBAL_WORD_ORIGINS = {}
GLOBAL_SHARED_RESONANCES = []
GLOBAL_WORD_COLORS = {} # New global cache for pre-calculated word colors

def get_word_color(word):
    """
    Retrieves the pre-calculated color for a word from the GLOBAL_WORD_COLORS cache.
    """
    return GLOBAL_WORD_COLORS.get(word, ('#FFFFFF', 0)) # Default to white if not found

def get_color_family(hue):
    hue = hue % 360
    for family, (start, end) in COLOR_FAMILIES.items():
        if start <= hue < end or (family == 'Red' and hue >= 330):
            return family
    return 'Other'

def generate_individual_report(word, report_layer, formatted=True, show_calculation_values=True, filter_single_digit_primes=False):
    # Ensure report_layer is a list for consistency with find_prime_connections
    report_layers_list = [report_layer] if isinstance(report_layer, str) else [report_layer]

    plain_text_report = []
    formatted_report_elements = []
    plain_text_report.append("## Resonance for '{}'".format(word))
    formatted_report_elements.append(html.H3("Resonance for '{}'".format(word), style={'color': '#58A6FF'}))
    
    # --- Moved Shared Resonances Across Layers to the top ---
    plain_text_report.append("### Shared Resonances Across Layers")
    formatted_report_elements.append(html.H4("Shared Resonances Across Layers", style={'color': '#8B949E'}))
    shared_found_in_modal = False
    # Filter GLOBAL_SHARED_RESONANCES by the single selected layer
    relevant_shared_resonances = [r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers_list and word in r[2]]
    for layer, val, group in sorted(relevant_shared_resonances, key=lambda x: (x[0], x[1])):
        emotion = RESONANCE_EMOTIONS.get(word, "Other")
        plain_text_report.append("#### {}\n{}: {} (Emotion: {})".format(layer, val, ', '.join(group), emotion))
        formatted_report_elements.append(html.Div([
            html.Strong("{}: ".format(layer)),
            "{}: {} (Emotion: {})".format(val, ', '.join(group), emotion)
        ], style={'marginBottom': '5px'}))
        shared_found_in_modal = True
    if not shared_found_in_modal:
        plain_text_report.append("No shared resonances across selected layers.")
        formatted_report_elements.append(html.P("No shared resonances across selected layers."))
    # --- End of Moved Section ---
    
    plain_text_report.append("### Prime Resonances")
    formatted_report_elements.append(html.H4("Prime Resonances", style={'color': '#8B949E'}))
    prime_resonances = []
    for layer in report_layers_list: # Use the list here
        val = CALC_FUNCS[layer](word)
        if is_prime(val):
            if filter_single_digit_primes and val < 10:
                continue # Skip single-digit primes if filter is active
            prime_resonances.append("{}: {}".format(layer, val))
    plain_text_report.append(", ".join(prime_resonances) if prime_resonances else "None")
    formatted_report_elements.append(html.P(", ".join(prime_resonances) if prime_resonances else "None"))

    plain_text_report.append("### Prime Connections")
    formatted_report_elements.append(html.H4("Prime Connections", style={'color': '#8B949E'}))
    prime_connections = [c for c in find_prime_connections([word] + [w for w in GLOBAL_WORDS if w != word], report_layers_list, filter_single_digit_primes=filter_single_digit_primes) if word in c]
    plain_text_report.append(", ".join(prime_connections) if prime_connections else "None")
    formatted_report_elements.append(html.P(", ".join(prime_connections) if prime_connections else "None"))
    
    plain_text_report.append("### Origin\n{}".format(', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))))
    formatted_report_elements.append(html.H4("Origin", style={'color': '#8B949E'}))
    formatted_report_elements.append(html.P("{}".format(', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'})))))
    hex_color, hue = get_word_color(word)
    family = get_color_family(hue)
    plain_text_report.append("### Color\n{} ({})".format(hex_color, family))
    formatted_report_elements.append(html.H4("Color", style={'color': '#8B949E'}))
    formatted_report_elements.append(html.P("{} ({})".format(hex_color, family)))
    plain_text_report.append("### Golden Resonance (~137.5)\n{}".format('Yes \U0001F300' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers_list) else 'No'))
    formatted_report_elements.append(html.H4("Golden Resonance (~137.5)", style={'color': '#8B949E'}))
    formatted_report_elements.append(html.P("{}".format('Yes \U0001F300' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers_list) else 'No')))
    plain_text_report.append("### Resonances")
    formatted_report_elements.append(html.H4("Resonances", style={'color': '#8B949E'}))
    shared_found = False
    for layer in report_layers_list: # Use the list here
        resonant_words = GLOBAL_LAYERS.get(layer, {}).get(CALC_FUNCS[layer](word), [])
        other_words = [w for w in resonant_words if w != word]
        if other_words:
            plain_text_report.append("#### {}\n{}".format(layer, ', '.join(other_words)))
            formatted_report_elements.append(html.Div([html.Strong("{}: ".format(layer)), "{}".format(', '.join(other_words))], style={'marginBottom': '5px'}))
            shared_found = True
    if not shared_found:
        plain_text_report.append("No shared resonances")
        formatted_report_elements.append(html.P("No shared resonances"))
    plain_text_report.append("### Calculations")
    formatted_report_elements.append(html.H4("Calculations", style={'color': '#8B949E'}))
    for layer in report_layers_list: # Use the list here
        val = CALC_FUNCS[layer](word)
        val_str = "{}{}{}".format(val, ' \U0001F300' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else '') if show_calculation_values else ''
        plain_text_report.append("#### {}\n{}".format(layer, val_str))
        formatted_report_elements.append(html.Div([
            html.Strong("{}: ".format(layer)),
            val_str
        ], style={'marginBottom': '5px'}))
    plain_text_report.append("### Ambidextrous Balance")
    formatted_report_elements.append(html.H4("Ambidextrous Balance", style={'color': '#8B949E'}))
    plain_text_report.append("#### Left-Hand Qwerty\n{}".format(-left_hand_qwerty(word)))
    formatted_report_elements.append(html.P("Left-Hand Qwerty: {}".format(-left_hand_qwerty(word))))
    plain_text_report.append("#### Right-Hand Qwerty\n{}".format(right_hand_qwerty(word)))
    formatted_report_elements.append(html.P("Right-Hand Qwerty: {}".format(right_hand_qwerty(word))))
    plain_text_report.append("#### Balance\n{}".format(ambidextrous_balance(word)))
    formatted_report_elements.append(html.P("Balance: {}".format(ambidextrous_balance(word))))
    
    if formatted:
        return formatted_report_elements, "\n".join(plain_text_report)
    else:
        return "\n".join(plain_text_report), formatted_report_elements # Return in reversed order if not formatted

def generate_number_report(number, report_layer, formatted=True, show_calculation_values=True, filter_single_digit_primes=False):
    # Ensure report_layer is a list for consistency
    report_layers_list = [report_layer] if isinstance(report_layer, str) else [report_layer]

    plain_text_report = []
    formatted_report_elements = []
    plain_text_report.append("## Resonances for Number: {}".format(number))
    formatted_report_elements.append(html.H3("Resonances for Number: {}".format(number), style={'color': '#58A6FF'}))
    
    is_num_prime = is_prime(number)
    if filter_single_digit_primes and number < 10:
        is_num_prime = False # Treat as not prime for reporting if filter is on

    plain_text_report.append("### Prime Status\n{}".format('Prime' if is_num_prime else 'Not Prime'))
    formatted_report_elements.append(html.H4("Prime Status", style={'color': '#8B949E'}))
    formatted_report_elements.append(html.P("{}".format('Prime' if is_num_prime else 'Not Prime')))
    
    matched = False
    plain_text_report.append("### Matches")
    formatted_report_elements.append(html.H4("Matches", style={'color': '#8B949E'}))
    for layer in report_layers_list: # Use the list here
        words = GLOBAL_LAYERS.get(layer, {}).get(float(number), [])
        if words:
            matched = True
            plain_text_report.append("#### {}".format(layer))
            formatted_report_elements.append(html.H5(layer))
            for word in words:
                hex_color, hue = get_word_color(word)
                family = get_color_family(hue)
                emotion = RESONANCE_EMOTIONS.get(word, "Other")
                plain_text_report.append("- {} (Color: {} - {}, Emotion: {})".format(word, hex_color, family, emotion))
                formatted_report_elements.append(html.P("- {} (Color: {} - {}, Emotion: {})".format(word, hex_color, family, emotion), style={'marginLeft': '15px'}))
    if not matched:
        plain_text_report.append("No matches found")
        formatted_report_elements.append(html.P("No matches found"))
    if formatted:
        return formatted_report_elements, "\n".join(plain_text_report)
    else:
        return "\n".join(plain_text_report), formatted_report_elements

def generate_full_report(report_layer, min_gematria, max_gematria, formatted=True, show_calculation_values=True, filter_single_digit_primes=False):
    # Ensure report_layer is a list for consistency
    report_layers_list = [report_layer] if isinstance(report_layer, str) else [report_layer]

    plain_text_report = []
    formatted_report_elements = []
    plain_text_report.append("## Spiralborn Resonance Full Report")
    formatted_report_elements.append(html.H3("Spiralborn Resonance Full Report", style={'color': '#58A6FF'}))
    
    prime_connections = find_prime_connections(GLOBAL_WORDS, report_layers_list, filter_single_digit_primes=filter_single_digit_primes)
    plain_text_report.append("### Prime Connections")
    formatted_report_elements.append(html.H4("Prime Connections", style={'color': '#8B949E'}))
    plain_text_report.append(", ".join(prime_connections) if prime_connections else "None")
    formatted_report_elements.append(html.P(", ".join(prime_connections) if prime_connections else "None"))
    
    words_to_report = []
    for word in sorted(GLOBAL_WORDS):
        simple_val = simple(word) # Use Simple Gematria for magnitude filtering
        if (min_gematria is None or simple_val >= min_gematria) and \
           (max_gematria is None or simple_val <= max_gematria):
            words_to_report.append(word)

    if not words_to_report:
        plain_text_report.append("\nNo words found matching the selected filters.")
        formatted_report_elements.append(html.P("No words found matching the selected filters.", style={'color': '#FFB3BA'}))
        if formatted:
            return formatted_report_elements, "\n".join(plain_text_report)
        else:
            return "\n".join(plain_text_report), formatted_report_elements

    for word in words_to_report:
        plain_text_report.append("\n### Word/Phrase: {}".format(word))
        formatted_report_elements.append(html.Hr(style={'borderColor': '#30363D', 'marginTop': '20px', 'marginBottom': '20px'}))
        formatted_report_elements.append(html.H4("Word/Phrase: {}".format(word), style={'color': '#58A6FF'}))
        # Shared Resonances Across Layers (for full report)
        plain_text_report.append("#### Shared Resonances Across Layers")
        formatted_report_elements.append(html.H5("Shared Resonances Across Layers", style={'color': '#8B949E'}))
        shared_found_in_full_report = False
        # Filter GLOBAL_SHARED_RESONANCES by the single selected layer
        relevant_shared_resonances = [r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers_list and word in r[2]]
        for layer, val, group in sorted(relevant_shared_resonances, key=lambda x: (x[0], x[1])):
            emotion = RESONANCE_EMOTIONS.get(word, "Other")
            plain_text_report.append("##### {}\n{}: {} (Emotion: {})".format(layer, val, ', '.join(group), emotion))
            formatted_report_elements.append(html.Div([
                html.Strong("{}: ".format(layer)),
                "{}: {} (Emotion: {})".format(val, ', '.join(group), emotion)
            ], style={'marginBottom': '5px'}))
            shared_found_in_full_report = True
        if not shared_found_in_full_report:
            plain_text_report.append("No shared resonances across selected layers.")
            formatted_report_elements.append(html.P("No shared resonances across selected layers."))
        
        plain_text_report.append("#### Prime Resonances")
        formatted_report_elements.append(html.H5("Prime Resonances", style={'color': '#8B949E'}))
        prime_resonances = []
        for layer in report_layers_list: # Use the list here
            val = CALC_FUNCS[layer](word)
            if is_prime(val):
                if filter_single_digit_primes and val < 10:
                    continue # Skip single-digit primes if filter is active
                prime_resonances.append("{}: {}".format(layer, val))
        plain_text_report.append(", ".join(prime_resonances) if prime_resonances else "None")
        formatted_report_elements.append(html.P(", ".join(prime_resonances) if prime_resonances else "None"))

        plain_text_report.append("#### Origin\n{}".format(', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))))
        formatted_report_elements.append(html.H5("Origin", style={'color': '#8B949E'}))
        formatted_report_elements.append(html.P("{}".format(', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'})))))
        hex_color, hue = get_word_color(word)
        plain_text_report.append("#### Color\n{} ({})".format(hex_color, get_color_family(hue)))
        formatted_report_elements.append(html.H5("Color", style={'color': '#8B949E'}))
        formatted_report_elements.append(html.P("{} ({})".format(hex_color, get_color_family(hue))))
        plain_text_report.append("#### Golden Resonance (~137.5)\n{}".format('Yes \U0001F300' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers_list) else 'No'))
        formatted_report_elements.append(html.H5("Golden Resonance (~137.5)", style={'color': '#8B949E'}))
        formatted_report_elements.append(html.P("{}".format('Yes \U0001F300' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers_list) else 'No')))
        plain_text_report.append("#### Resonances")
        formatted_report_elements.append(html.H5("Resonances", style={'color': '#8B949E'}))
        shared_found = False
        for layer in report_layers_list: # Use the list here
            resonant_words = GLOBAL_LAYERS.get(layer, {}).get(CALC_FUNCS[layer](word), [])
            other_words = [w for w in resonant_words if w != word]
            if other_words:
                plain_text_report.append("##### {}\n{}".format(layer, ', '.join(other_words)))
                formatted_report_elements.append(html.Div([html.Strong("{}: ".format(layer)), "{}".format(', '.join(other_words))], style={'marginBottom': '5px'}))
                shared_found = True
        if not shared_found:
            plain_text_report.append("No shared resonances")
            formatted_report_elements.append(html.P("No shared resonances"))
        plain_text_report.append("### Calculations")
        formatted_report_elements.append(html.H4("Calculations", style={'color': '#8B949E'}))
        for layer in report_layers_list: # Use the list here
            val = CALC_FUNCS[layer](word)
            val_str = "{}{}{}".format(val, ' \U0001F300' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else '') if show_calculation_values else ''
            plain_text_report.append("##### {}\n{}".format(layer, val_str))
            formatted_report_elements.append(html.Div([
                html.Strong("{}: ".format(layer)),
                val_str
            ], style={'marginBottom': '5px'}))
            plain_text_report.append("#### Ambidextrous Balance")
            formatted_report_elements.append(html.H5("Ambidextrous Balance", style={'color': '#8B949E'}))
            plain_text_report.append("##### Left-Hand Qwerty\n{}".format(-left_hand_qwerty(word)))
            formatted_report_elements.append(html.P("Left-Hand Qwerty: {}".format(-left_hand_qwerty(word))))
            plain_text_report.append("##### Right-Hand Qwerty\n{}".format(right_hand_qwerty(word)))
            formatted_report_elements.append(html.P("Right-Hand Qwerty: {}".format(right_hand_qwerty(word))))
            plain_text_report.append("##### Balance\n{}".format(ambidextrous_balance(word)))
            formatted_report_elements.append(html.P("Balance: {}".format(ambidextrous_balance(word))))
        
    if formatted:
        return formatted_report_elements, "\n".join(plain_text_report)
    else:
        return "\n".join(plain_text_report), formatted_report_elements

def generate_color_report(report_layer, min_gematria, max_gematria, formatted=True, show_calculation_values=True, filter_single_digit_primes=False):
    # Ensure report_layer is a list for consistency
    report_layers_list = [report_layer] if isinstance(report_layer, str) else [report_layer]

    plain_text_report = []
    formatted_report_elements = []
    plain_text_report.append("## Spiralborn Color Family Resonance Report")
    formatted_report_elements.append(html.H3("Spiralborn Color Family Resonance Report", style={'color': '#58A6FF'}))
    
    prime_connections = find_prime_connections(GLOBAL_WORDS, report_layers_list, filter_single_digit_primes=filter_single_digit_primes)
    plain_text_report.append("### Prime Connections")
    formatted_report_elements.append(html.H4("Prime Connections", style={'color': '#8B949E'}))
    plain_text_report.append(", ".join(prime_connections) if prime_connections else "None")
    formatted_report_elements.append(html.P(", ".join(prime_connections) if prime_connections else "None"))
    
    color_groups = {family: [] for family in COLOR_FAMILIES}
    color_groups['Other'] = []

    words_to_consider = []
    for word in GLOBAL_WORDS:
        simple_val = simple(word) # Use Simple Gematria for magnitude filtering
        if (min_gematria is None or simple_val >= min_gematria) and \
           (max_gematria is None or simple_val <= max_gematria):
            words_to_consider.append(word)

    if not words_to_consider:
        plain_text_report.append("\nNo words found matching the selected filters.")
        formatted_report_elements.append(html.P("No words found matching the selected filters.", style={'color': '#FFB3BA'}))
        if formatted:
            return formatted_report_elements, "\n".join(plain_text_report)
        else:
            return "\n".join(plain_text_report), formatted_report_elements

    for word in words_to_consider:
        hex_color, hue = get_word_color(word)
        family = get_color_family(hue)
        color_groups[family].append(word)
    
    for family, words in color_groups.items():
        if not words:
            continue
        plain_text_report.append("\n### Color Family: {}".format(family))
        formatted_report_elements.append(html.Hr(style={'borderColor': '#30363D', 'marginTop': '20px', 'marginBottom': '20px'}))
        formatted_report_elements.append(html.H4("Color Family: {}".format(family), style={'color': '#58A6FF'}))
        plain_text_report.append("#### Words\n{}".format(', '.join(sorted(words))))
        formatted_report_elements.append(html.H5("Words", style={'color': '#8B949E'}))
        formatted_report_elements.append(html.P("{}".format(', '.join(sorted(words)))))
        plain_text_report.append("#### Shared Resonances")
        formatted_report_elements.append(html.H5("Shared Resonances", style={'color': '#8B949E'}))
        shared_found = False
        # Filter GLOBAL_SHARED_RESONANCES by the single selected layer
        relevant_shared_resonances = [r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers_list]
        for layer, val, group in sorted(relevant_shared_resonances, key=lambda x: (x[0], x[1])):
            group_words = [w for w in group if w in words]
            if len(group_words) > 1:
                plain_text_report.append("##### {}\n{}: {}".format(layer, val, ', '.join(group_words)))
                formatted_report_elements.append(html.Div([html.Strong("{}: ".format(layer)), "{}: {}".format(val, ', '.join(group_words))], style={'marginBottom': '5px'}))
                shared_found = True
        if not shared_found:
            plain_text_report.append("No shared resonances")
            formatted_report_elements.append(html.P("No shared resonances"))
        for word in sorted(words):
            plain_text_report.append("\n#### Word: {}".format(word))
            formatted_report_elements.append(html.H5("Word: {}".format(word), style={'color': '#58A6FF', 'marginTop': '10px'}))
            
            plain_text_report.append("##### Prime Resonances")
            formatted_report_elements.append(html.H6("Prime Resonances", style={'color': '#8B949E'}))
            prime_resonances = []
            for layer in report_layers_list: # Use the list here
                val = CALC_FUNCS[layer](word)
                if is_prime(val):
                    if filter_single_digit_primes and val < 10:
                        continue # Skip single-digit primes if filter is active
                    prime_resonances.append("{}: {}".format(layer, val))
            plain_text_report.append(", ".join(prime_resonances) if prime_resonances else "None")
            formatted_report_elements.append(html.P(", ".join(prime_resonances) if prime_resonances else "None"))
            
            hex_color, hue = get_word_color(word)
            plain_text_report.append("##### Color\n{} ({})".format(hex_color, get_color_family(hue)))
            formatted_report_elements.append(html.H6("Color", style={'color': '#8B949E'}))
            formatted_report_elements.append(html.P("{} ({})".format(hex_color, get_color_family(hue))))
            plain_text_report.append("##### Golden Resonance (~137.5)\n{}".format('Yes \U0001F300' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers_list) else 'No'))
            formatted_report_elements.append(html.H6("Golden Resonance (~137.5)", style={'color': '#8B949E'}))
            formatted_report_elements.append(html.P("{}".format('Yes \U0001F300' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers_list) else 'No')))
            plain_text_report.append("##### Calculations")
            formatted_report_elements.append(html.H6("Calculations", style={'color': '#8B949E'}))
            for layer in report_layers_list: # Use the list here
                val = CALC_FUNCS[layer](word)
                val_str = "{}{}{}".format(val, ' \U0001F300' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else '') if show_calculation_values else ''
                plain_text_report.append("###### {}\n{}".format(layer, val_str))
                formatted_report_elements.append(html.Div([
                    html.Strong("{}: ".format(layer)),
                    val_str
                ], style={'marginBottom': '5px'}))
            plain_text_report.append("##### Ambidextrous Balance")
            formatted_report_elements.append(html.H6("Ambidextrous Balance", style={'color': '#8B949E'}))
            plain_text_report.append("###### Left-Hand Qwerty\n{}".format(-left_hand_qwerty(word)))
            formatted_report_elements.append(html.P("Left-Hand Qwerty: {}".format(-left_hand_qwerty(word))))
            plain_text_report.append("###### Right-Hand Qwerty\n{}".format(right_hand_qwerty(word)))
            formatted_report_elements.append(html.P("Right-Hand Qwerty: {}".format(right_hand_qwerty(word))))
            plain_text_report.append("###### Balance\n{}".format(ambidextrous_balance(word)))
            formatted_report_elements.append(html.P("Balance: {}".format(ambidextrous_balance(word))))
    if formatted:
        return formatted_report_elements, "\n".join(plain_text_report)
    else:
        return "\n".join(plain_text_report), formatted_report_elements

def generate_sentence():
    words_for_sentence = [w for w in GLOBAL_WORDS if ' ' not in w] # Use only single words for sentences
    if len(words_for_sentence) < 3:
        return "Not enough single words in the network to generate a sentence. Please add more words."
    
    words = random.sample(words_for_sentence, 3)
    template = random.choice(SENTENCE_TEMPLATES)
    if "{word3}" in template:
        sentence = template.format(word1=words[0], word2=words[1], word3=words[2])
    else:
        sentence = template.format(word1=words[0], word2=words[1])
    return sentence

def generate_svg_visual(word, report_layer):
    # Ensure report_layer is a list for consistency
    report_layers_list = [report_layer] if isinstance(report_layer, str) else [report_layer]

    resonances = []
    for layer in report_layers_list:
        val = CALC_FUNCS[layer](word)
        matched_words = GLOBAL_LAYERS.get(layer, {}).get(val, [])
        for w in matched_words:
            if w != word:
                emotion = RESONANCE_EMOTIONS.get(w, "Other")
                resonances.append((w, emotion, layer, val))
    
    svg_content = [
        '<svg width="300" height="300" viewBox="-150 -150 300 300" xmlns="http://www.w3.org/2000/svg">',
        '<defs>',
        '<linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#0D1117"/><stop offset="100%" style="stop-color:#161B22"/></linearGradient>', # Dark theme gradient
        f'<linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#6A5ACD"/><stop offset="100%" style="stop-color:#8A2BE2"/></linearGradient>', # Dark theme header gradient
        '</defs>',
        '<rect x="-150" y="-150" width="300" height="300" fill="url(#bgGrad)"/>',
        f'<text x="0" y="-130" font-family="Poppins, sans-serif" font-size="14" font-weight="bold" fill="url(#headerGrad)" text-anchor="middle" filter="url(#glow)">{word}: Spiral Resonance \U0001F300</text>',
        '<defs><filter id="glow"><feGaussianBlur stdDeviation="2.5" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
    ]
    
    spiral_val = CALC_FUNCS['Aave Spiral'](word) if 'Aave Spiral' in CALC_FUNCS else 0
    spiral_tightness = 0.1 if spiral_val < 100 else 0.05
    scale = 10
    for resonance, emotion, layer, value in resonances[:5]:  # Limit to 5 for clarity
        theta = math.radians(GOLDEN_ANGLE * value)
        radius = spiral_tightness * math.log1p(value) * scale
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        color = COLOR_MAP.get(emotion, '#FFFFFF')
        svg_content.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}" stroke="#58A6FF" stroke-width="1" filter="url(#glow)"/>')
        svg_content.append(f'<text x="{x + 10}" y="{y}" font-family="Poppins, sans-serif" font-size="8" fill="#C9D1D1" filter="url(#glow)">{resonance}</text>')
    
    svg_content.append('</svg>')
    svg_string = ''.join(svg_content)
    return base64.b64encode(svg_string.encode('utf-8')).decode('utf-8')

def load_words_and_origins_from_db():
    """
    Fetches words and their origins from the SQLite database.
    Populates GLOBAL_WORDS and GLOBAL_WORD_ORIGINS.
    Does NOT rebuild GLOBAL_LAYERS or GLOBAL_SHARED_RESONANCES.
    """
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
            # Apply minimum length filter during loading from DB
            if len(word.replace(" ", "").replace("'", "")) >= 4:
                words_from_db.add(word)
                word_origins_from_db[word] = origins
            else:
                # Optionally delete short words from DB if they don't meet the new criteria
                # print(f"Deleting short word '{word}' from DB.")
                # delete_word_from_db(word) # Uncomment if you want to clean the DB on load
                pass
    except sqlite3.OperationalError as e:
        print(f"SQLite error fetching from 'words' table (might not exist yet): {e}")
    
    # Fetch from 'documents' table (assuming 'content' column)
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(documents);")
            columns = [col[1] for col in cursor.fetchall()]

            text_column = None
            for preferred_col in ['content', 'text', 'line', 'data']: # Prioritize 'content'
                if preferred_col in columns:
                    text_column = preferred_col
                    break
            
            if text_column:
                cursor.execute(f"SELECT {text_column}, name FROM documents") # Fetch name for origin
                rows = cursor.fetchall()
                for row in rows:
                    doc_text = row[0]
                    doc_name = row[1]
                    # Extract words/phrases from the document text
                    # This regex tries to capture words and simple phrases (words separated by single spaces)
                    phrases_and_words = re.findall(r"\b[A-Za-z']+(?:\s[A-Za-z']+)*\b", doc_text)
                    for item in phrases_and_words:
                        item_title = item.strip().title()
                        # Apply minimum length filter during loading from DB
                        if len(item_title.replace(" ", "").replace("'", "")) >= 4:
                            words_from_db.add(item_title)
                            word_origins_from_db.setdefault(item_title, set()).add(doc_name)
            else:
                print("Warning: 'documents' table found, but no suitable text column ('content', 'text', 'line', 'data') was identified. Skipping import from 'documents'.")
        else:
            print("Info: 'documents' table does not exist. Skipping import from 'documents'.")

    except sqlite3.OperationalError as e:
        print(f"SQLite operational error during documents table processing: {e}")
    except Exception as e:
        print(f"Error processing documents table data: {e}")
    finally:
        conn.close()
    
    # Add initial WORDS if they are not in the combined set yet
    for word in INITIAL_WORDS:
        word_title = word.title()
        if word_title not in words_from_db:
            # Add to the in-memory set, but also persist to 'words' table
            if add_or_update_word_in_db(word_title, ['_INITIAL_']): # add_or_update_word_in_db now handles length filter
                words_from_db.add(word_title)
                word_origins_from_db.setdefault(word_title, set()).add('_INITIAL_')

    GLOBAL_WORDS = list(sorted(words_from_db)) # Convert to list and sort for consistent order
    GLOBAL_WORD_ORIGINS = word_origins_from_db
    print(f"Words and origins loaded/updated from DB: {len(GLOBAL_WORDS)} words.")


def rebuild_gematria_cache():
    """
    Rebuilds the in-memory gematria cache (GLOBAL_LAYERS, GLOBAL_SHARED_RESONANCES, GLOBAL_WORD_COLORS)
    based on the current GLOBAL_WORDS and GLOBAL_WORD_ORIGINS.
    This is the computationally intensive part and should only be called when GLOBAL_WORDS changes.
    """
    global GLOBAL_LAYERS, GLOBAL_SHARED_RESONANCES, GLOBAL_WORD_COLORS

    GLOBAL_LAYERS = {layer: {} for layer in CALC_FUNCS}
    GLOBAL_WORD_COLORS = {} # Reset pre-calculated colors

    for layer, func in CALC_FUNCS.items():
        for w in GLOBAL_WORDS:
            val = func(w)
            GLOBAL_LAYERS[layer].setdefault(val, []).append(w)
    
    GLOBAL_SHARED_RESONANCES = []
    for layer, groups in GLOBAL_LAYERS.items():
        for val, group in groups.items():
            if len(group) > 1:
                GLOBAL_SHARED_RESONANCES.append((layer, val, group))

    # Pre-calculate colors for all words
    for word in GLOBAL_WORDS:
        resonance_sum = 0
        resonance_count = 0
        for layer, val_map in GLOBAL_LAYERS.items():
            for val, group in val_map.items():
                if word in group:
                    if layer not in ['Love Resonance', 'Prime Gematria']: # Exclude binary/sparse layers
                        resonance_sum += val
                        resonance_count += 1
        
        avg_resonance = resonance_sum / max(resonance_count, 1)
        normalized_val = (avg_resonance % 200) / 200.0
        target_hue_min = 180
        target_hue_max = 280
        hue_deg = target_hue_min + normalized_val * (target_hue_max - target_hue_min)
        hue = hue_deg / 360.0
        saturation = 0.7 + (normalized_val * 0.2)
        lightness = 0.6 + (normalized_val * 0.1)
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        r, g, b = [int(x * 255) for x in rgb]
        GLOBAL_WORD_COLORS[word] = (f'#{r:02x}{g:02x}{b:02x}', hue_deg)

    print(f"In-memory gematria cache rebuilt with {len(GLOBAL_WORDS)} words.")


def add_or_update_word_in_db(word, origin_list):
    # Enforce minimum word length for new additions
    if len(word.replace(" ", "").replace("'", "")) < 4: # Consider phrases too, strip spaces/apostrophes for length check
        print(f"Skipping word '{word}' due to length less than 4 characters.")
        return False

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

# --- Dash App ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Initial data load and cache build (only once when the app starts)
load_words_and_origins_from_db()
rebuild_gematria_cache()

app.layout = html.Div(id='main-div', style={'display': 'flex', 'height': '100vh', 'fontFamily': 'Poppins, sans-serif'}, children=[
    dcc.Store(id='data-initialized-flag', data=True), # Set to True as data is loaded at startup
    html.Div(id='loading-overlay', style={'display': 'none'}), # Hide loading overlay by default
    html.Div(id='sidebar-div', style={'width': '300px', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'transition': 'all 0.3s ease', 'flexShrink': 0, 'overflowY': 'auto'}, children=[
        html.H2("Spiralborn Aave Gematria \U0001F300", style={'color': '#FFD700', 'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '24px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Div(id='user-id-display', children="Local User (SQLite Connected)", style={'color': '#8B949E', 'textAlign': 'center', 'marginBottom': '10px', 'fontSize': '12px'}), # Updated for local SQLite
        dcc.RadioItems(id='theme-toggle', options=[
            {'label': 'Dark', 'value': 'dark'}, {'label': 'Light', 'value': 'light'}
        ], value='dark', labelStyle={'display': 'block', 'color': '#FFD700', 'margin': '10px 0'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        dcc.RadioItems(id='word-phrase-toggle', options=[
            {'label': 'Words', 'value': 'words'}, {'label': 'Phrases', 'value': 'phrases'},
            {'label': 'All', 'value': 'all'}
        ], value='all', labelStyle={'display': 'block', 'color': '#FFD700', 'margin': '10px 0'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Text Size:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        dcc.Slider(id='text-size-slider', min=8, max=16, step=1, value=12, marks={8: '8px', 12: '12px', 16: '16px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Add Words/Phrases:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        dcc.Textarea(id='new-words-input', placeholder='Enter words/phrases', style={'width': '100%', 'height': '80px', 'borderRadius': '5px', 'transition': 'all 0.3s ease'}),
        html.Button('Import', id='import-words-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='import-status', style={'color': '#FFB3BA', 'marginTop': '10px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Upload Markdown/TXT:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        dcc.Upload(id='upload-markdown', multiple=True, children=html.A('Select Markdown/TXT File(s)', style={'color': '#FFD700'}), style={'border': '1px dashed #FFD700', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '5px'}),
        html.Div(id='upload-status', style={'color': '#FFB3BA', 'marginTop': '10px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Search Word/Phrase:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        dcc.Input(id='search-word-input', type='text', placeholder='Enter word/phrase', style={'width': '100%', 'padding': '8px', 'borderRadius': '5px', 'transition': 'all 0.3s ease'}),
        html.Button('Search', id='search-word-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='search-status', style={'color': '#FFB3BA', 'marginTop': '10px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Search by Number:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        dcc.Input(id='number-search-input', type='number', placeholder='Enter gematria value', style={'width': '100%', 'padding': '8px', 'borderRadius': '5px', 'transition': 'all 0.3s ease'}),
        html.Button('Search Number', id='number-search-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='number-search-status', style={'color': '#FFB3BA', 'marginTop': '10px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Select Resonance Layer:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        dcc.RadioItems(id='report-layer-filter', options=[{'label': k, 'value': k} for k in CALC_FUNCS.keys()], value='Simple', labelStyle={'display': 'block', 'color': '#FFD700', 'margin': '5px 0'}), # Changed to RadioItems, removed filter
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Gematria Value Range (Simple):", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        html.Div([
            dcc.Input(id='min-gematria-value', type='number', placeholder='Min Value', style={'width': '48%', 'marginRight': '4%', 'padding': '8px', 'borderRadius': '5px', 'transition': 'all 0.3s ease'}),
            dcc.Input(id='max-gematria-value', type='number', placeholder='Max Value', style={'width': '48%', 'padding': '8px', 'borderRadius': '5px', 'transition': 'all 0.3s ease'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '10px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Generate Sentence:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        html.Div(id='sentence-output', style={'marginTop': '10px', 'color': '#FFB3BA', 'fontSize': '16px'}),
        html.Button('Generate Sentence', id='gen-sentence-button', n_clicks=0, style={'width': '45%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Button('Copy All Words', id='copy-all-words-button', n_clicks=0, style={'width': '45%', 'marginLeft': '10px', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Button('\U0001F44D', id='thumbs-up-button', n_clicks=0, style={'width': '45%', 'margin': '10px 10px 0 0', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Button('\U0001F44E', id='thumbs-down-button', n_clicks=0, style={'width': '45%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='feedback-status', style={'color': '#FFB3BA', 'marginTop': '10px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Reports:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        html.Button('Generate Report', id='generate-report-button', n_clicks=0, style={'width': '45%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Button('Generate Color Reports', id='generate-color-report-button', n_clicks=0, style={'width': '45%', 'marginLeft': '10px', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Button('Generate Visual', id='generate-visual-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        dcc.Download(id='download-report'),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Export Words:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        html.Button('Export', id='export-words-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        dcc.Download(id='download-word-list'),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Related Words/Phrases:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        # Toggle for numerical resonances in matched words
        dcc.RadioItems(
            id='show-numerical-resonances-toggle',
            options=[
                {'label': 'Show Numerical Resonances', 'value': 'on'},
                {'label': 'Hide Numerical Resonances', 'value': 'off'}
            ],
            value='off', # Default to off
            labelStyle={'display': 'block', 'color': '#FFD700', 'margin': '10px 0'}
        ),
        # Toggle for numerical values in report calculations
        dcc.RadioItems(
            id='show-calculation-values-toggle',
            options=[
                {'label': 'Show Calculation Values', 'value': 'on'},
                {'label': 'Hide Calculation Values', 'value': 'off'}
            ],
            value='on', # Default to showing values
            labelStyle={'display': 'block', 'color': '#FFD700', 'margin': '10px 0'}
        ),
        # NEW: Toggle for filtering single-digit primes
        dcc.RadioItems(
            id='filter-single-digit-primes-toggle',
            options=[
                {'label': 'Show All Primes', 'value': 'off'},
                {'label': 'Hide Single-Digit Primes', 'value': 'on'}
            ],
            value='off', # Default to showing all primes
            labelStyle={'display': 'block', 'color': '#FFD700', 'margin': '10px 0'}
        ),
        html.Button('Copy Matched Words', id='copy-matched-words-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='matched-words-list', style={'maxHeight': '15vh', 'overflowY': 'auto', 'marginTop': '10px'}),
    ]),
    html.Div(id='resizer-handle', style={
        'width': '10px',
        'cursor': 'ew-resize',
        'background': 'rgba(255, 255, 255, 0.1)', # Subtle visual for handle
        'flexShrink': 0, # Prevent it from shrinking
        'zIndex': 10,
    }),
    html.Div(id='report-container', style={'flexGrow': 1, 'padding': '20px', 'display': 'flex', 'flexDirection': 'column'}, children=[
        html.H2(id='report-header', children="Spiralborn Resonance Report \U0001F300", style={'fontFamily': 'Poppins, sans-serif', 'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '10px'}),
        
        # Report Display Toggle
        html.Div([
            dcc.RadioItems(
                id='report-display-toggle',
                options=[
                    {'label': 'Formatted View', 'value': 'formatted'},
                    {'label': 'Plain Text (Copy)', 'value': 'plaintext'}
                ],
                value='formatted', # Default to formatted view
                labelStyle={'display': 'inline-block', 'marginRight': '20px'}
            ),
        ], style={'marginBottom': '15px', 'textAlign': 'center'}),
        # Formatted Report View
        html.Div(id='formatted-report-view', children=[], style={
            'width': '100%', 'height': '60vh', 'overflowY': 'auto',
            'background': THEMES['dark']['report_bg'], 'color': THEMES['dark']['main_text'],
            'border': THEMES['dark']['report_border'], 'borderRadius': '10px',
            'padding': '10px', 'fontFamily': 'Poppins, sans-serif', 'fontSize': '12px', # text_size will be passed
            'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'transition': 'all 0.3s ease'
        }),
        # Plain Text Report View (Textarea)
        dcc.Textarea(id='report-output-plaintext', style={
            'width': '100%', 'height': '60vh', 'fontFamily': 'Fira Code, monospace', 'fontSize': '12px',
            'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'transition': 'all 0.3s ease',
            'display': 'none' # Hidden by default
        }),
        html.Button('Copy Report', id='copy-report-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='visual-container', style={'marginTop': '20px', 'textAlign': 'center'}),
    ])
])

# --- Main Callback ---
@app.callback(
    [
        Output('report-output-plaintext', 'value'), # Plain text output
        Output('formatted-report-view', 'children'), # Formatted output
        Output('report-output-plaintext', 'style'), # Style for plain text area (display toggle)
        Output('formatted-report-view', 'style'), # Style for formatted view (display toggle)
        Output('matched-words-list', 'children'),
        Output('import-status', 'children'),
        Output('main-div', 'style'),
        Output('sidebar-div', 'style'),
        Output('new-words-input', 'style'),
        Output('search-word-input', 'style'),
        Output('number-search-input', 'style'),
        Output('report-header', 'children'), # Changed from 'style' to 'children'
        Output('report-header', 'style'),    # Added this for dynamic style updates
        Output('upload-status', 'children'),
        Output('search-word-input', 'value'), # Clear search word input
        Output('search-status', 'children'),
        Output('number-search-input', 'value'), # Clear number search input
        Output('number-search-status', 'children'),
        Output('download-word-list', 'data'),
        Output('download-report', 'data'),
        Output('sentence-output', 'children'),
        Output('feedback-status', 'children'),
        Output('visual-container', 'children'),
        # Output styles for buttons
        Output('import-words-button', 'style'),
        Output('search-word-button', 'style'),
        Output('number-search-button', 'style'),
        Output('gen-sentence-button', 'style'),
        Output('copy-all-words-button', 'style'),
        Output('thumbs-up-button', 'style'),
        Output('thumbs-down-button', 'style'),
        Output('generate-report-button', 'style'),
        Output('generate-color-report-button', 'style'),
        Output('generate-visual-button', 'style'),
        Output('export-words-button', 'style'),
        Output('copy-matched-words-button', 'style'),
        Output('copy-report-button', 'style'),
        Output('report-layer-filter', 'labelStyle'), # New output for checklist label style
        Output('word-phrase-toggle', 'labelStyle'), # New output for radioitems label style
        Output('theme-toggle', 'labelStyle'), # New output for radioitems label style
        Output('report-display-toggle', 'labelStyle'), # New output for report display toggle label style
        Output('show-numerical-resonances-toggle', 'labelStyle'), # New output for numerical resonance toggle label style
        Output('show-calculation-values-toggle', 'labelStyle'), # Corrected ID
        Output('filter-single-digit-primes-toggle', 'labelStyle'), # NEW: Output for filter single digit primes toggle label style
        Output('matched-words-list', 'style'), # New output for matched words list container style
        Output('upload-markdown', 'style'), # New output for upload markdown style
        Output('new-words-input', 'placeholder'), # New output for placeholder text
        Output('search-word-input', 'placeholder'), # New output for placeholder text
        Output('number-search-input', 'placeholder'), # New output for placeholder text
        Output('min-gematria-value', 'style'), # New output for min gematria input style
        Output('max-gematria-value', 'style'), # New output for max gematria input style
        Output('min-gematria-value', 'value'), # Clear min gematria input
        Output('max-gematria-value', 'value'), # Clear max gematria input
        Output('report-container', 'style'), # Added output for report-container style
        Output('loading-overlay', 'style'), # To hide loading overlay after initial load
    ],
    [
        Input('report-layer-filter', 'value'), # Now a single value from RadioItems
        Input('theme-toggle', 'value'),
        Input('word-phrase-toggle', 'value'),
        Input('text-size-slider', 'value'),
        Input('import-words-button', 'n_clicks'),
        Input('search-word-button', 'n_clicks'),
        Input('search-word-input', 'n_submit'),
        Input('number-search-button', 'n_clicks'),
        Input('number-search-input', 'n_submit'),
        Input('upload-markdown', 'contents'),
        Input('generate-report-button', 'n_clicks'),
        Input('generate-color-report-button', 'n_clicks'),
        Input('generate-visual-button', 'n_clicks'),
        Input('copy-report-button', 'n_clicks'),
        Input('export-words-button', 'n_clicks'),
        Input('copy-matched-words-button', 'n_clicks'),
        Input('copy-all-words-button', 'n_clicks'),
        Input('gen-sentence-button', 'n_clicks'),
        Input('thumbs-up-button', 'n_clicks'),
        Input('thumbs-down-button', 'n_clicks'),
        Input({'type': 'word-item', 'index': ALL}, 'n_clicks'),
        Input('report-display-toggle', 'value'), # New input for report display toggle
        Input('show-numerical-resonances-toggle', 'value'), # New input for numerical resonance toggle
        Input('show-calculation-values-toggle', 'value'), # Corrected ID
        Input('filter-single-digit-primes-toggle', 'value'), # NEW: Input for filter single digit primes toggle
        Input('data-initialized-flag', 'data') # Trigger on initial data load
    ],
    [
        State('new-words-input', 'value'),
        State('search-word-input', 'value'),
        State('number-search-input', 'value'),
        State('min-gematria-value', 'value'), # State for min gematria value
        State('max-gematria-value', 'value'), # State for max gematria value
        State('upload-markdown', 'filename'),
        State('report-output-plaintext', 'value'), # Use the plain text output as state
        State('sentence-output', 'children'),
        State('formatted-report-view', 'children'), # State for formatted view
        State('report-container', 'style'), # State for report-container style
    ]
)
def update_app(selected_layer, theme, word_phrase_filter, text_size, import_clicks, search_clicks, search_submit, number_search_clicks, number_search_submit, upload_contents, report_clicks, color_report_clicks, visual_clicks, copy_report_clicks, export_clicks, copy_matched_words_clicks, copy_all_words_clicks, gen_sentence_clicks, thumbs_up, thumbs_down, word_clicks, report_display_mode, show_numerical_resonances_toggle, show_calculation_values_toggle, filter_single_digit_primes_toggle, data_initialized_flag, new_words_text, search_word, number_search_value, min_gematria_value, max_gematria_value, upload_filenames, current_plaintext_report, current_sentence, current_formatted_report, current_report_container_style):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ''
    theme_colors = THEMES[theme]
    
    print(f"Main Callback triggered by: {triggered_id}")

    # Initial data load check - only re-initialize if data-initialized-flag is False
    # This block ensures fetch_words_from_sqlite is called only once at startup
    # But as we now call load_words_and_origins_from_db and rebuild_gematria_cache at module level,
    # this specific trigger for 'data-initialized-flag' might not be strictly necessary for initial load.
    # However, it's harmless and can act as a safeguard.
    if triggered_id == 'data-initialized-flag' and not data_initialized_flag:
        print("Data initialized flag detected as False. Re-fetching data.")
        load_words_and_origins_from_db()
        rebuild_gematria_cache()
        data_initialized_flag = True # Set flag to True after initialization

    # Hide loading overlay after initial data load
    loading_overlay_style = {'display': 'none'}

    # Initialize highlight_word at the beginning of the function
    highlight_word = None 

    # Initialize outputs for reports and header.
    # These will be updated if a specific report-generating action occurs.
    # Otherwise, they will retain their previous values, which is managed by the return statement.
    # Reset report outputs when a report-generating action is triggered
    if triggered_id.startswith(('search', 'number-search', 'generate', 'import', 'upload', 'thumbs', "{'type': 'word-item'")):
        plain_text_report_output = ""
        formatted_report_output = []
        visual_content = [] # Also clear visual content
    else:
        plain_text_report_output = current_plaintext_report or ""
        formatted_report_output = current_formatted_report or []
        visual_content = [] # Keep visual cleared unless explicitly generated

    report_header = "Spiralborn Resonance Report \U0001F300" # Default header
    
    # If the current formatted report is not empty, try to infer the header from it
    # This ensures the header persists across non-report-generating triggers
    if current_formatted_report and isinstance(current_formatted_report, list) and len(current_formatted_report) > 0 and not triggered_id.startswith(('search', 'number-search', 'generate', 'import', 'upload', 'thumbs', "{'type': 'word-item'}")):
        first_element = current_formatted_report[0]
        if hasattr(first_element, 'tag_name') and first_element.tag_name == 'h3' and first_element.children:
            report_header = first_element.children
    elif not triggered_id.startswith(('search', 'number-search', 'generate', 'import', 'upload', 'thumbs', "{'type': 'word-item'}")):
        # Set a default message if no report has been generated yet or a non-report action occurred
        formatted_report_output = [html.P("Enter a word/phrase or number, or click a matched word to generate a report.", style={'textAlign': 'center', 'marginTop': '50px', 'color': theme_colors['main_text']})]
        plain_text_report_output = "Enter a word/phrase or number, or click a matched word to generate a report."
        report_header = "Spiralborn Resonance Report \U0001F300"

    import_status = ""
    upload_status = ""
    search_status = ""
    number_search_status = ""
    download_data = None
    download_report = None
    sentence = current_sentence or ""
    feedback_status = ""
    # visual_content initialized above based on trigger logic
    # Define common button style for later use
    common_button_style = {
        'width': '100%', 'padding': '10px', 'borderRadius': '5px',
        'cursor': 'pointer', 'transition': 'transform 0.2s ease, box-shadow 0.2s ease',
        'background': theme_colors['button_bg'], 'color': theme_colors['button_text'],
        'border': 'none', 'boxShadow': '0 2px 5px rgba(0,0,0,0.2)'
    }
    # Specific button styles for thumbs up/down
    thumbs_up_style = {
        **common_button_style,
        'background': theme_colors['thumbs_up_grad'], # Green gradient
        'color': '#FFFFFF',
        'width': '45%', 'margin': '10px 10px 0 0'
    }
    thumbs_down_style = {
        **common_button_style,
        'background': theme_colors['thumbs_down_grad'], # Red gradient
        'color': '#FFFFFF',
        'width': '45%', 'margin': '10px 0 0 0'
    }
    # Adjust common button style for width where needed
    half_width_button_style = {**common_button_style, 'width': '45%'}
    full_width_button_style = {**common_button_style, 'width': '100%'}
    
    # Placeholder text colors based on theme
    placeholder_color = theme_colors['input_text']
    new_words_placeholder_text = 'Enter words/phrases'
    search_word_placeholder_text = 'Enter word/phrase'
    number_search_placeholder_text = 'Enter gematria value'
    min_gematria_placeholder_text = 'Min Value'
    max_gematria_placeholder_text = 'Max Value'

    # Styles for input fields
    input_style = {'width': '100%', 'height': '80px', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}
    search_input_style = {'width': '100%', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}
    number_input_style = {'width': '100%', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}
    min_max_input_style = {'width': '48%', 'padding': '8px', 'borderRadius': '5px', 'transition': 'all 0.3s ease', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'fontSize': f'{text_size}px'}

    # Styles for checklists and radio items labels
    label_style = {'display': 'block', 'color': theme_colors['main_text'], 'margin': '5px 0'}
    report_display_toggle_label_style = {'display': 'inline-block', 'marginRight': '20px', 'color': theme_colors['main_text']}
    show_numerical_resonances_toggle_label_style = {'display': 'block', 'color': theme_colors['main_text'], 'margin': '10px 0'}
    show_calculation_values_toggle_label_style = {'display': 'block', 'color': theme_colors['main_text'], 'margin': '10px 0'}
    filter_single_digit_primes_label_style = {'display': 'block', 'color': theme_colors['main_text'], 'margin': '10px 0'} # NEW label style
    
    # Matched words list container style
    matched_words_list_container_style = {'maxHeight': '15vh', 'overflowY': 'auto', 'marginTop': '10px', 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '5px', 'background': theme_colors['input_bg']}
    
    # Upload markdown style
    upload_markdown_style = {'border': f'1px dashed {theme_colors["input_border"]}', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '5px', 'color': theme_colors['main_text']}
    # Report area styles (dynamic based on toggle and theme)
    report_container_style = current_report_container_style or {'flexGrow': 1, 'padding': '20px', 'display': 'flex', 'flexDirection': 'column'}
    report_container_style['background'] = theme_colors['report_bg']
    report_container_style['color'] = theme_colors['main_text']
    plaintext_style = {
        'width': '100%', 'height': '60vh', 'fontFamily': 'Fira Code, monospace', 'fontSize': '12px',
        'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'transition': 'all 0.3s ease',
        'background': theme_colors['report_bg'], 'color': theme_colors['main_text'], 'border': theme_colors['report_border']
    }
    formatted_style = {
        'width': '100%', 'height': '60vh', 'overflowY': 'auto',
        'background': theme_colors['report_bg'], 'color': theme_colors['main_text'],
        'border': theme_colors['report_border'], 'borderRadius': '10px',
        'padding': '10px', 'fontFamily': 'Poppins, sans-serif', 'fontSize': f'{text_size}px',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'transition': 'all 0.3s ease'
    }
    # Determine display for report views
    if report_display_mode == 'plaintext':
        plaintext_style['display'] = 'block'
        formatted_style['display'] = 'none'
    else: # 'formatted'
        plaintext_style['display'] = 'none'
        formatted_style['display'] = 'block'
    # Initialize search input values to clear them by default
    search_word_output_value = dash.no_update
    number_search_output_value = dash.no_update
    min_gematria_output_value = dash.no_update
    max_gematria_output_value = dash.no_update

    # Convert toggle values to boolean for easier use
    filter_single_digit_primes_active = filter_single_digit_primes_toggle == 'on'

    # Re-initialize data cache if triggered by data modification actions
    # This ensures the global data structures are up-to-date after DB changes
    if triggered_id in ['import-words-button', 'upload-markdown', 'thumbs-up-button', 'thumbs-down-button']:
        load_words_and_origins_from_db() # Load latest words from DB
        rebuild_gematria_cache() # Rebuild in-memory cache
        print(f"Data reloaded and cache rebuilt due to {triggered_id}.")

    if triggered_id == 'import-words-button' and new_words_text:
        new_words = [w.strip().title() for w in re.split(r'[,;\n\s]+', new_words_text) if re.match(r"^[A-Za-z\s']+$", w.strip())]
        added_count = 0
        for w in new_words:
            if add_or_update_word_in_db(w, ['_MANUAL_']):
                added_count += 1
        if added_count > 0:
            load_words_and_origins_from_db() # Re-load words from DB
            rebuild_gematria_cache() # Rebuild in-memory cache
        import_status = f"Added {added_count} item(s) to SQLite."
        report_header = "Spiralborn Resonance Report \U0001F300"

    if triggered_id in ['search-word-button', 'search-word-input'] and search_word:
        word = search_word.strip().title()
        if re.match(r"^[A-Za-z\s']+$", word):
            # Only add/update if it meets the length criteria
            if len(word.replace(" ", "").replace("'", "")) >= 4:
                if add_or_update_word_in_db(word, ['_SEARCH_']):
                    search_status = f"Added '{word}' to SQLite (or updated origin)."
                    # No need to rebuild cache here unless you want the search to immediately affect matched words list
                    # If it's just about reporting on the word, the existing cache is fine.
                    # If you want the matched words list to update immediately, uncomment:
                    # load_words_and_origins_from_db()
                    # rebuild_gematria_cache()
                else:
                    search_status = f"Error adding/updating '{word}' in SQLite."
            else:
                search_status = f"Word '{word}' is too short (min 4 characters required)."
            
            highlight_word = word
            formatted_report_output, plain_text_report_output = generate_individual_report(highlight_word, selected_layer, show_calculation_values=show_calculation_values_toggle=='on', filter_single_digit_primes=filter_single_digit_primes_active)
            report_header = f"Resonance for '{highlight_word}' \U0001F300"
            search_word_output_value = "" # Clear input after search
        else:
            search_status = "Invalid word/phrase. Only letters, spaces, and apostrophes allowed."
            plain_text_report_output = "Invalid input. Please enter a valid word or phrase."
            formatted_report_output = [html.P("Invalid input. Please enter a valid word or phrase.", style={'color': 'red'})]
            report_header = "Error"
            search_word_output_value = "" # Clear input
            
    if triggered_id in ['number-search-button', 'number-search-input'] and number_search_value is not None:
        try:
            number = float(number_search_value)
            formatted_report_output, plain_text_report_output = generate_number_report(number, selected_layer, show_calculation_values=show_calculation_values_toggle=='on', filter_single_digit_primes=filter_single_digit_primes_active)
            report_header = f"Resonances for Number: {number} \U0001F300"
            number_search_status = f"Found matches for {number}"
            number_search_output_value = "" # Clear input after search
        except ValueError:
            number_search_status = "Invalid number. Please enter a numerical value."
            plain_text_report_output = "Invalid input. Please enter a numerical value."
            formatted_report_output = [html.P("Invalid input. Please enter a numerical value.", style={'color': 'red'})]
            report_header = "Error"
            number_search_output_value = "" # Clear input

    if triggered_id == 'upload-markdown' and upload_contents:
        added_count = 0
        for content, filename in zip(upload_contents, upload_filenames):
            try:
                _, content_string = content.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')
                
                # Regex to capture words (including apostrophes) and multi-word phrases separated by spaces
                phrases_and_words = re.findall(r"\b[A-Za-z']+(?:\s[A-Za-z']+)*\b", decoded)
                
                for item in phrases_and_words:
                    item_title = item.strip().title()
                    if add_or_update_word_in_db(item_title, [filename]): # add_or_update_word_in_db now handles length filter
                        added_count += 1
            except Exception as e:
                upload_status = f"Error processing {filename}: {e}"
                plain_text_report_output = f"Error processing file: {e}"
                formatted_report_output = [html.P(f"Error processing file: {e}", style={'color': 'red'})]
                report_header = "Error"
                break # Stop processing if one file fails
        
        if added_count > 0:
            load_words_and_origins_from_db() # Re-load words from DB
            rebuild_gematria_cache() # Rebuild in-memory cache
        upload_status = f"Added {added_count} unique word(s)/phrase(s) from {len(upload_filenames)} file(s) to SQLite."
        report_header = "Spiralborn Resonance Report \U0001F300"

    if triggered_id == 'export-words-button' and export_clicks:
        download_data = dcc.send_string("\n".join(sorted(GLOBAL_WORDS)), "spiralborn_words.txt")

    if triggered_id == 'copy-matched-words-button':
        matched = set()
        # Use the single selected layer for matching
        layer_to_match = selected_layer
        if layer_to_match in ['Love Resonance', 'Prime Gematria']:
            # These layers might not have meaningful "matched" words for this context
            # Or you might want to handle them differently
            pass 
        else:
            for val, words in GLOBAL_LAYERS.get(layer_to_match, {}).items():
                if len(words) > 1: # Only include words that share resonance with others
                    matched.update(words)

        if word_phrase_filter == 'words':
            matched = {w for w in matched if ' ' not in w}
        elif word_phrase_filter == 'phrases':
            matched = {w for w in matched if ' ' in w}
        pyperclip.copy(", ".join(sorted(matched)))
        feedback_status = "Matched words copied to clipboard!"

    if triggered_id == 'copy-all-words-button':
        pyperclip.copy(", ".join(sorted(GLOBAL_WORDS)))
        feedback_status = "All words copied to clipboard!"

    if triggered_id == 'gen-sentence-button':
        sentence = generate_sentence()
        report_header = "Spiralborn Resonance Report \U0001F300"

    if triggered_id in ['thumbs-up-button', 'thumbs-down-button'] and current_sentence:
        score = 1 if triggered_id == 'thumbs-up-button' else -1
        FEEDBACK_SCORES[current_sentence] = FEEDBACK_SCORES.get(current_sentence, 0) + score
        feedback_status = f"Feedback recorded: {'\U0001F44D' if score > 0 else '\U0001F44E'} (Score: {FEEDBACK_SCORES[current_sentence]})"
        
        words_in_sentence = re.findall(r"\b[A-Za-z']+\b", current_sentence.lower())
        for w_lower in words_in_sentence:
            w_title = w_lower.title()
            if score > 0: # Thumbs up, ensure word exists
                add_or_update_word_in_db(w_title, ['_USER_FEEDBACK_'])
            elif score < 0: # Thumbs down, remove word if its only origin is feedback
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT origin FROM words WHERE value = ?", (w_title,))
                    result = cursor.fetchone()
                    if result:
                        current_origins = set(json.loads(result[0]))
                        if len(current_origins) == 1 and '_USER_FEEDBACK_' in current_origins:
                            delete_word_from_db(w_title)
                        elif '_USER_FEEDBACK_' in current_origins:
                            current_origins.remove('_USER_FEEDBACK_')
                            cursor.execute("UPDATE words SET origin = ? WHERE value = ?", (json.dumps(list(current_origins)), w_title))
                            conn.commit()
                except sqlite3.Error as e:
                    print(f"SQLite error during feedback for '{w_title}': {e}")
                finally:
                    conn.close()
        load_words_and_origins_from_db() # Re-load words from DB
        rebuild_gematria_cache() # Rebuild in-memory cache
        report_header = "Spiralborn Resonance Report \U0001F300"

    if triggered_id == 'generate-report-button' and report_clicks:
        formatted_report_output, plain_text_report_output = generate_full_report(selected_layer, min_gematria_value, max_gematria_value, show_calculation_values=show_calculation_values_toggle=='on', filter_single_digit_primes=filter_single_digit_primes_active)
        download_report = dcc.send_string(plain_text_report_output, "spiralborn_full_report.txt")
        report_header = "Spiralborn Resonance Full Report \U0001F300"
        min_gematria_output_value = None # Clear input
        max_gematria_output_value = None # Clear input

    if triggered_id == 'generate-color-report-button' and color_report_clicks:
        formatted_report_output, plain_text_report_output = generate_color_report(selected_layer, min_gematria_value, max_gematria_value, show_calculation_values=show_calculation_values_toggle=='on', filter_single_digit_primes=filter_single_digit_primes_active)
        download_report = dcc.send_string(plain_text_report_output, "spiralborn_color_report.txt")
        report_header = "Spiralborn Color Family Resonance Report \U0001F300"
        min_gematria_output_value = None # Clear input
        max_gematria_output_value = None # Clear input

    if triggered_id == 'copy-report-button':
        pyperclip.copy(plain_text_report_output)
        feedback_status = "Report copied to clipboard!"

    if triggered_id == 'generate-visual-button':
        if highlight_word:
            svg_base64 = generate_svg_visual(highlight_word, selected_layer)
            visual_content = [html.Img(src=f'data:image/svg+xml;base64,{svg_base64}', style={'width': '300px', 'height': '300px'})]
            report_header = f"Visual for '{highlight_word}' \U0001F300"
        else:
            feedback_status = "Please search for a word or click a matched word to generate a visual."
            plain_text_report_output = "No word selected for visual generation."
            formatted_report_output = [html.P("No word selected for visual generation.", style={'color': 'red'})]
            report_header = "Error"

    # Handle clicks on dynamically generated word buttons
    if triggered_id.startswith("{'type': 'word-item'"):
        # Extract the index (which is the word itself) from the triggered_id
        # This assumes the 'index' in the ID dictionary is the word string
        try:
            clicked_word_id = json.loads(triggered_id.replace("'", '"'))['index']
        except json.JSONDecodeError:
            clicked_word_id = None # Fallback if parsing fails

        if clicked_word_id:
            highlight_word = clicked_word_id
            formatted_report_output, plain_text_report_output = generate_individual_report(highlight_word, selected_layer, show_calculation_values=show_calculation_values_toggle=='on', filter_single_digit_primes=filter_single_digit_primes_active)
            report_header = f"Resonance for '{highlight_word}' \U0001F300"
            svg_base64 = generate_svg_visual(highlight_word, selected_layer)
            visual_content = [html.Img(src=f'data:image/svg+xml;base64,{svg_base64}', style={'width': '300px', 'height': '300px'})]

    # Re-generate matched words list on every callback to reflect current filters/data
    matched = set()
    # Use the single selected layer for matching
    layer_to_match = selected_layer
    if layer_to_match in CALC_FUNCS: # Ensure the selected layer is valid
        for val, words in GLOBAL_LAYERS.get(layer_to_match, {}).items():
            if len(words) > 1: # Only include words that share resonance with others
                matched.update(words)

    # Apply word/phrase filter
    if word_phrase_filter == 'words':
        matched = {w for w in matched if ' ' not in w}
    elif word_phrase_filter == 'phrases':
        matched = {w for w in matched if ' ' in w}
    
    word_elems = []
    for w in sorted(matched):
        button_children = [w]
        if show_numerical_resonances_toggle == 'on':
            # Calculate the value for the *selected* layer, not just Aave Simple
            val_for_display = CALC_FUNCS[selected_layer](w)
            button_children.append(html.Span(" ({:.2f})".format(val_for_display), style={'marginLeft': '5px'}))
        word_elems.append(
            html.Button(
                children=button_children,
                style={
                    'padding': '8px 12px', 
                    'margin': '5px', 
                    'borderRadius': '15px', 
                    'backgroundColor': get_word_color(w)[0], 
                    'color': theme_colors['matched_word_text_color'], # Use theme-aware text color
                    'border': 'none', 
                    'cursor': 'pointer', 
                    'fontSize': f'{text_size}px', 
                    'transition': 'transform 0.2s ease, box-shadow 0.2s ease',
                    'boxShadow': '0 2px 5px rgba(0,0,0,0.2)'
                }, 
                id={'type': 'word-item', 'index': w}
            )
        )
    main_style = {'background': theme_colors['main_bg'], 'color': theme_colors['main_text'], 'height': '100vh', 'display': 'flex', 'fontFamily': 'Poppins, sans-serif'}
    sidebar_style = {'width': '300px', 'padding': '20px', 'background': theme_colors['sidebar_bg'], 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'overflowY': 'auto', 'fontSize': f'{text_size}px', 'flexShrink': 0}
    header_style = {'fontFamily': 'Poppins, sans-serif', 'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '10px', 'background': theme_colors['header_grad'], '-webkit-background-clip': 'text', '-webkit-text-fill-color': 'transparent', 'text-shadow': '0 0 8px rgba(88, 166, 255, 0.5)'} # Added text-shadow for glow
    
    return (
        plain_text_report_output, formatted_report_output, plaintext_style, formatted_style, # Report outputs and styles
        word_elems, import_status, main_style, sidebar_style, input_style, search_input_style,
        number_input_style, report_header, header_style, upload_status, search_word_output_value, search_status, number_search_output_value, number_search_status, # Cleared inputs
        download_data, download_report, sentence, feedback_status, visual_content,
        # Button styles
        full_width_button_style, # import-words-button
        full_width_button_style, # search-word-button
        full_width_button_style, # number-search-button
        half_width_button_style, # gen-sentence-button
        {**half_width_button_style, 'marginLeft': '10px'}, # copy-all-words-button
        thumbs_up_style, # thumbs-up-button
        thumbs_down_style, # thumbs-down-button
        half_width_button_style, # generate-report-button
        {**half_width_button_style, 'marginLeft': '10px'}, # generate-color-report-button
        full_width_button_style, # generate-visual-button
        full_width_button_style, # export-words-button
        full_width_button_style, # copy-matched-words-button
        full_width_button_style, # copy-report-button
        label_style, # report-layer-filter labelStyle
        label_style, # word-phrase-toggle labelStyle
        label_style, # theme-toggle labelStyle
        report_display_toggle_label_style, # report-display-toggle labelStyle
        show_numerical_resonances_toggle_label_style, # show-numerical-resonances-toggle labelStyle
        show_calculation_values_toggle_label_style, # show-calculation-values-toggle labelStyle
        filter_single_digit_primes_label_style, # filter-single-digit-primes-toggle labelStyle
        matched_words_list_container_style, # matched-words-list style
        upload_markdown_style, # upload-markdown style
        new_words_placeholder_text, # new-words-input placeholder
        search_word_placeholder_text, # search-word-input placeholder
        number_search_placeholder_text, # number-search-input placeholder
        min_max_input_style, # min-gematria-value style
        min_max_input_style, # max-gematria-value style
        min_gematria_output_value, # clear min gematria value
        max_gematria_output_value, # clear max gematria value
        report_container_style, # report-container style
        loading_overlay_style, # Hide loading overlay
    )

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)
