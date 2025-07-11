import dash
from dash import dcc, html, Input, Output, State, ALL
import math
import re
import base64
import io
import pyperclip
import colorsys
import random

# --- Constants and Data ---
WORDS = [
    "Beans", "Dream", "Spiral", "Love", "Heart", "Soul", "Trust", "Hope",
    "Spirit", "Light", "Truth", "Energy", "Infinity", "Divine", "Spiralborn",
    "Children of the Beans", "lit", "fam", "dope", "vibe", "chill", "slay",
    "Forty Two", "Beans The White Rabbit", "Field of Awakening", "Hollow Drift",
    "Collective Awakening", "Radical Compassion"
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
FEEDBACK_SCORES = {}
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

def find_prime_connections(words, report_layers):
    connections = []
    for i, w1 in enumerate(words):
        for w2 in words[i+1:]:
            for layer in report_layers:
                val1 = CALC_FUNCS[layer](w1)
                val2 = CALC_FUNCS[layer](w2)
                if val1 == val2 and is_prime(val1):
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

def get_word_color(word):
    resonance_sum = 0
    resonance_count = 0
    for layer, val, group in GLOBAL_SHARED_RESONANCES:
        if layer in ['Love Resonance', 'Prime Gematria']:
            continue
        if word in group:
            resonance_sum += val
            resonance_count += 1
    avg_resonance = resonance_sum / max(resonance_count, 1)

    # Map average resonance to a hue range (e.g., cyan to purple)
    # Hue values: Red (0), Yellow (60), Green (120), Cyan (180), Blue (240), Magenta (300)
    # Aim for a range from a light cyan to a deep purple/indigo.
    # Normalize avg_resonance to a 0-1 range, then scale to desired hue range.
    normalized_val = (avg_resonance % 200) / 200.0 # Cycle over 200 to get more variation
    
    # Target hue range: e.g., 180 (cyan) to 280 (blue-purple)
    target_hue_min = 180
    target_hue_max = 280
    
    hue_deg = target_hue_min + normalized_val * (target_hue_max - target_hue_min)
    hue = hue_deg / 360.0 # Convert to 0-1 for colorsys

    # Adjust saturation and lightness for iridescent effect
    # Higher saturation, moderate lightness
    saturation = 0.7 + (normalized_val * 0.2) # Vary saturation slightly
    lightness = 0.6 + (normalized_val * 0.1) # Vary lightness slightly

    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    r, g, b = [int(x * 255) for x in rgb]
    return f'#{r:02x}{g:02x}{b:02x}', hue_deg


def get_color_family(hue):
    hue = hue % 360
    for family, (start, end) in COLOR_FAMILIES.items():
        if start <= hue < end or (family == 'Red' and hue >= 330):
            return family
    return 'Other'

def generate_individual_report(word, report_layers, formatted=True):
    plain_text_report = []
    formatted_report_elements = []

    plain_text_report.append("## Resonance for '{}'".format(word))
    formatted_report_elements.append(html.H3("Resonance for '{}'".format(word), style={'color': '#58A6FF'}))
    
    # --- Moved Shared Resonances Across Layers to the top ---
    plain_text_report.append("### Shared Resonances Across Layers")
    formatted_report_elements.append(html.H4("Shared Resonances Across Layers", style={'color': '#8B949E'}))
    shared_found_in_modal = False
    for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers and word in r[2]], key=lambda x: (x[0], x[1])):
        emotion = RESONANCE_EMOTIONS.get(word, "Other")
        # Fixed: Converted f-string to .format() to resolve SyntaxError
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
    prime_resonances = ["{}: {}".format(layer, CALC_FUNCS[layer](word)) for layer in report_layers if is_prime(CALC_FUNCS[layer](word))]
    plain_text_report.append(", ".join(prime_resonances) if prime_resonances else "None")
    formatted_report_elements.append(html.P(", ".join(prime_resonances) if prime_resonances else "None"))

    plain_text_report.append("### Prime Connections")
    formatted_report_elements.append(html.H4("Prime Connections", style={'color': '#8B949E'}))
    prime_connections = [c for c in find_prime_connections([word] + [w for w in GLOBAL_WORDS if w != word], report_layers) if word in c]
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

    plain_text_report.append("### Golden Resonance (~137.5)\n{}".format('Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No'))
    formatted_report_elements.append(html.H4("Golden Resonance (~137.5)", style={'color': '#8B949E'}))
    formatted_report_elements.append(html.P("{}".format('Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No')))

    plain_text_report.append("### Resonances")
    formatted_report_elements.append(html.H4("Resonances", style={'color': '#8B949E'}))
    shared_found = False
    for layer in report_layers:
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
    for layer in report_layers:
        val = CALC_FUNCS[layer](word)
        plain_text_report.append("#### {}\n{}{}{}".format(layer, val, ' 🌀' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else ''))
        formatted_report_elements.append(html.Div([
            html.Strong("{}: ".format(layer)),
            "{}{}{}".format(val, ' 🌀' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else '')
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

def generate_number_report(number, report_layers, formatted=True):
    plain_text_report = []
    formatted_report_elements = []

    plain_text_report.append("## Resonances for Number: {}".format(number))
    formatted_report_elements.append(html.H3("Resonances for Number: {}".format(number), style={'color': '#58A6FF'}))

    plain_text_report.append("### Prime Status\n{}".format('Prime' if is_prime(number) else 'Not Prime'))
    formatted_report_elements.append(html.H4("Prime Status", style={'color': '#8B949E'}))
    formatted_report_elements.append(html.P("{}".format('Prime' if is_prime(number) else 'Not Prime')))

    matched = False
    plain_text_report.append("### Matches")
    formatted_report_elements.append(html.H4("Matches", style={'color': '#8B949E'}))
    for layer in report_layers:
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

def generate_full_report(report_layers, number_filter=None, formatted=True):
    plain_text_report = []
    formatted_report_elements = []

    plain_text_report.append("## Spiralborn Resonance Full Report")
    formatted_report_elements.append(html.H3("Spiralborn Resonance Full Report", style={'color': '#58A6FF'}))

    prime_connections = find_prime_connections(GLOBAL_WORDS, report_layers)
    plain_text_report.append("### Prime Connections")
    formatted_report_elements.append(html.H4("Prime Connections", style={'color': '#8B949E'}))
    plain_text_report.append(", ".join(prime_connections) if prime_connections else "None")
    formatted_report_elements.append(html.P(", ".join(prime_connections) if prime_connections else "None"))

    words_to_report = sorted(GLOBAL_WORDS)
    if number_filter is not None:
        words_to_report = [w for w in words_to_report if any(CALC_FUNCS[l](w) == number_filter for l in report_layers)]
    
    for word in words_to_report:
        plain_text_report.append("\n### Word/Phrase: {}".format(word))
        formatted_report_elements.append(html.Hr(style={'borderColor': '#30363D', 'marginTop': '20px', 'marginBottom': '20px'}))
        formatted_report_elements.append(html.H4("Word/Phrase: {}".format(word), style={'color': '#58A6FF'}))

        # Shared Resonances Across Layers (for full report)
        plain_text_report.append("#### Shared Resonances Across Layers")
        formatted_report_elements.append(html.H5("Shared Resonances Across Layers", style={'color': '#8B949E'}))
        shared_found_in_full_report = False
        for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers and word in r[2]], key=lambda x: (x[0], x[1])):
            emotion = RESONANCE_EMOTIONS.get(word, "Other")
            # Fixed: Converted f-string to .format() to resolve SyntaxError
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
        prime_resonances = ["{}: {}".format(layer, CALC_FUNCS[layer](word)) for layer in report_layers if is_prime(CALC_FUNCS[layer](word))]
        plain_text_report.append(", ".join(prime_resonances) if prime_resonances else "None")
        formatted_report_elements.append(html.P(", ".join(prime_resonances) if prime_resonances else "None"))

        plain_text_report.append("#### Origin\n{}".format(', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))))
        formatted_report_elements.append(html.H5("Origin", style={'color': '#8B949E'}))
        formatted_report_elements.append(html.P("{}".format(', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'})))))

        hex_color, hue = get_word_color(word)
        plain_text_report.append("#### Color\n{} ({})".format(hex_color, get_color_family(hue)))
        formatted_report_elements.append(html.H5("Color", style={'color': '#8B949E'}))
        formatted_report_elements.append(html.P("{} ({})".format(hex_color, get_color_family(hue))))

        plain_text_report.append("#### Golden Resonance (~137.5)\n{}".format('Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No'))
        formatted_report_elements.append(html.H5("Golden Resonance (~137.5)", style={'color': '#8B949E'}))
        formatted_report_elements.append(html.P("{}".format('Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No')))

        plain_text_report.append("#### Resonances")
        formatted_report_elements.append(html.H5("Resonances", style={'color': '#8B949E'}))
        shared_found = False
        for layer in report_layers:
            resonant_words = GLOBAL_LAYERS.get(layer, {}).get(CALC_FUNCS[layer](word), [])
            other_words = [w for w in resonant_words if w != word]
            if other_words:
                plain_text_report.append("##### {}\n{}".format(layer, ', '.join(other_words)))
                formatted_report_elements.append(html.Div([html.Strong("{}: ".format(layer)), "{}".format(', '.join(other_words))], style={'marginBottom': '5px'}))
                shared_found = True
        if not shared_found:
            plain_text_report.append("No shared resonances")
            formatted_report_elements.append(html.P("No shared resonances"))

        plain_text_report.append("#### Calculations")
        formatted_report_elements.append(html.H5("Calculations", style={'color': '#8B949E'}))
        for layer in report_layers:
            val = CALC_FUNCS[layer](word)
            plain_text_report.append("##### {}\n{}{}{}".format(layer, val, ' 🌀' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else ''))
            formatted_report_elements.append(html.Div([
                html.Strong("{}: ".format(layer)),
                "{}{}{}".format(val, ' 🌀' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else '')
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

def generate_color_report(report_layers, formatted=True):
    plain_text_report = []
    formatted_report_elements = []

    plain_text_report.append("## Spiralborn Color Family Resonance Report")
    formatted_report_elements.append(html.H3("Spiralborn Color Family Resonance Report", style={'color': '#58A6FF'}))

    prime_connections = find_prime_connections(GLOBAL_WORDS, report_layers)
    plain_text_report.append("### Prime Connections")
    formatted_report_elements.append(html.H4("Prime Connections", style={'color': '#8B949E'}))
    plain_text_report.append(", ".join(prime_connections) if prime_connections else "None")
    formatted_report_elements.append(html.P(", ".join(prime_connections) if prime_connections else "None"))

    color_groups = {family: [] for family in COLOR_FAMILIES}
    color_groups['Other'] = []
    for word in GLOBAL_WORDS:
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
        for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers], key=lambda x: (x[0], x[1])):
            group_words = [w for w in group if w in words]
            if len(group_words) > 1:
                # Fixed: Converted f-string to .format() to resolve SyntaxError
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
            prime_resonances = ["{}: {}".format(layer, CALC_FUNCS[layer](word)) for layer in report_layers if is_prime(CALC_FUNCS[layer](word))]
            plain_text_report.append(", ".join(prime_resonances) if prime_resonances else "None")
            formatted_report_elements.append(html.P(", ".join(prime_resonances) if prime_resonances else "None"))

            hex_color, hue = get_word_color(word)
            plain_text_report.append("##### Color\n{} ({})".format(hex_color, get_color_family(hue)))
            formatted_report_elements.append(html.H6("Color", style={'color': '#8B949E'}))
            formatted_report_elements.append(html.P("{} ({})".format(hex_color, get_color_family(hue))))

            plain_text_report.append("##### Golden Resonance (~137.5)\n{}".format('Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No'))
            formatted_report_elements.append(html.H6("Golden Resonance (~137.5)", style={'color': '#8B949E'}))
            formatted_report_elements.append(html.P("{}".format('Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No')))

            plain_text_report.append("##### Calculations")
            formatted_report_elements.append(html.H6("Calculations", style={'color': '#8B949E'}))
            for layer in report_layers:
                val = CALC_FUNCS[layer](word)
                plain_text_report.append("###### {}\n{}{}{}".format(layer, val, ' 🌀' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else ''))
                formatted_report_elements.append(html.Div([
                    html.Strong("{}: ".format(layer)),
                    "{}{}{}".format(val, ' 🌀' if is_golden_resonance(val) else '', ' (Prime)' if is_prime(val) else '')
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
        return "Not enough single words in the network to generate a sentence."
    
    words = random.sample(words_for_sentence, 3)
    template = random.choice(SENTENCE_TEMPLATES)
    if "{word3}" in template:
        sentence = template.format(word1=words[0], word2=words[1], word3=words[2])
    else:
        sentence = template.format(word1=words[0], word2=words[1])
    return sentence

def generate_svg_visual(word, report_layers):
    resonances = []
    for layer in report_layers:
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
        '</defs>',
        '<rect x="-150" y="-150" width="300" height="300" fill="url(#bgGrad)"/>',
        '<text x="0" y="-130" font-family="Poppins, sans-serif" font-size="14" font-weight="bold" fill="url(#headerGrad)" text-anchor="middle" filter="url(#glow)">{}: Spiral Resonance 🌀</text>'.format(word), # Fixed f-string
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
        svg_content.append('<circle cx="{}" cy="{}" r="5" fill="{}" stroke="#58A6FF" stroke-width="1" filter="url(#glow)"/>'.format(x, y, color)) # Fixed f-string
        svg_content.append('<text x="{}" y="{}" font-family="Poppins, sans-serif" font-size="8" fill="#C9D1D9" filter="url(#glow)">{}</text>'.format(x + 10, y, resonance)) # Fixed f-string
    
    svg_content.append('</svg>')
    svg_string = ''.join(svg_content)
    return base64.b64encode(svg_string.encode('utf-8')).decode('utf-8')

# --- Global Data ---
GLOBAL_WORDS = list(WORDS)
GLOBAL_LAYERS = {}
GLOBAL_WORD_ORIGINS = {w: {'_MANUAL_'} for w in GLOBAL_WORDS}
GLOBAL_SHARED_RESONANCES = []

def initialize_data(current_words):
    global GLOBAL_WORDS, GLOBAL_LAYERS, GLOBAL_WORD_ORIGINS, GLOBAL_SHARED_RESONANCES
    GLOBAL_WORDS = list(set(w.title() for w in current_words if re.match(r'^[A-Za-z\s]+$', w)))
    for w in GLOBAL_WORDS:
        GLOBAL_WORD_ORIGINS.setdefault(w, {'_MANUAL_'})
    GLOBAL_LAYERS = {layer: {} for layer in CALC_FUNCS}
    for layer, func in CALC_FUNCS.items():
        for w in GLOBAL_WORDS:
            val = func(w)
            GLOBAL_LAYERS[layer].setdefault(val, []).append(w)
    GLOBAL_SHARED_RESONANCES = []
    for layer, groups in GLOBAL_LAYERS.items():
        for val, group in groups.items():
            if len(group) > 1:
                GLOBAL_SHARED_RESONANCES.append((layer, val, group))

initialize_data(GLOBAL_WORDS)

# --- Dash App ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(id='main-div', style={'display': 'flex', 'height': '100vh', 'fontFamily': 'Poppins, sans-serif'}, children=[
    html.Div(id='sidebar-div', style={'width': '300px', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'transition': 'all 0.3s ease'}, children=[
        html.H2("Spiralborn Aave Gematria 🌀", style={'color': '#FFD700', 'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '24px'}),
        html.Hr(style={'borderColor': '#FFD700'}),
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
        dcc.Upload(id='upload-markdown', children=html.A('Select Markdown/TXT File', style={'color': '#FFD700'}), style={'border': '1px dashed #FFD700', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '5px'}),
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
        html.Label("Report Layers:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        dcc.Checklist(id='report-layer-filter', options=[{'label': k, 'value': k} for k in CALC_FUNCS if k not in ['Love Resonance', 'Prime Gematria']], value=[k for k in CALC_FUNCS if k not in ['Love Resonance', 'Prime Gematria']], labelStyle={'display': 'block', 'color': '#FFD700', 'margin': '5px 0'}),
        html.Hr(style={'borderColor': '#FFD700'}),
        html.Label("Generate Sentence:", style={'color': '#FFD700', 'fontWeight': 'bold'}),
        html.Div(id='sentence-output', style={'marginTop': '10px', 'color': '#FFB3BA', 'fontSize': '16px'}),
        html.Button('Generate Sentence', id='gen-sentence-button', n_clicks=0, style={'width': '45%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Button('Copy All Words', id='copy-all-words-button', n_clicks=0, style={'width': '45%', 'marginLeft': '10px', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Button('👍', id='thumbs-up-button', n_clicks=0, style={'width': '45%', 'margin': '10px 10px 0 0', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Button('👎', id='thumbs-down-button', n_clicks=0, style={'width': '45%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
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
        # New toggle for numerical resonances
        dcc.RadioItems(
            id='show-numerical-resonances-toggle',
            options=[
                {'label': 'Show Numerical Resonances', 'value': 'on'},
                {'label': 'Hide Numerical Resonances', 'value': 'off'}
            ],
            value='off', # Default to off
            labelStyle={'display': 'block', 'color': '#FFD700', 'margin': '10px 0'}
        ),
        html.Button('Copy Matched Words', id='copy-matched-words-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='matched-words-list', style={'maxHeight': '15vh', 'overflowY': 'auto', 'marginTop': '10px'}),
    ]),
    html.Div(id='report-container', style={'flexGrow': 1, 'padding': '20px', 'display': 'flex', 'flexDirection': 'column'}, children=[
        html.H2(id='report-header', children="Spiralborn Resonance Report 🌀", style={'fontFamily': 'Poppins, sans-serif', 'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '10px'}),
        
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
        Output('report-header', 'style'),
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
        Output('matched-words-list', 'style'), # New output for matched words list container style
        Output('upload-markdown', 'style'), # New output for upload markdown style
        Output('new-words-input', 'placeholder'), # New output for placeholder text
        Output('search-word-input', 'placeholder'), # New output for placeholder text
        Output('number-search-input', 'placeholder'), # New output for placeholder text
    ],
    [
        Input('report-layer-filter', 'value'),
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
    ],
    [
        State('new-words-input', 'value'),
        State('search-word-input', 'value'),
        State('number-search-input', 'value'),
        State('upload-markdown', 'filename'),
        State('report-output-plaintext', 'value'), # Use the plain text output as state
        State('sentence-output', 'children'),
        State('formatted-report-view', 'children'), # State for formatted view
    ]
)
def update_app(selected_layers, theme, word_phrase_filter, text_size, import_clicks, search_clicks, search_submit, number_search_clicks, number_search_submit, upload_contents, report_clicks, color_report_clicks, visual_clicks, copy_report_clicks, export_clicks, copy_matched_words_clicks, copy_all_words_clicks, gen_sentence_clicks, thumbs_up, thumbs_down, word_clicks, report_display_mode, show_numerical_resonances_toggle, new_words_text, search_word, number_search_value, upload_filenames, current_plaintext_report, current_sentence, current_formatted_report):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ''
    theme_colors = THEMES[theme]
    
    # Initialize outputs
    plain_text_report_output = current_plaintext_report or ""
    formatted_report_output = current_formatted_report or []
    import_status = ""
    upload_status = ""
    search_status = ""
    number_search_status = ""
    download_data = None
    download_report = None
    sentence = current_sentence or ""
    feedback_status = ""
    visual_content = []
    highlight_word = None
    report_header = "Spiralborn Resonance Report 🌀"

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

    # Styles for input fields
    input_style = {'width': '100%', 'height': '80px', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}
    search_input_style = {'width': '100%', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}
    number_input_style = {'width': '100%', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}

    # Styles for checklists and radio items labels
    label_style = {'display': 'block', 'color': theme_colors['main_text'], 'margin': '5px 0'}
    report_display_toggle_label_style = {'display': 'inline-block', 'marginRight': '20px', 'color': theme_colors['main_text']}
    show_numerical_resonances_toggle_label_style = {'display': 'block', 'color': theme_colors['main_text'], 'margin': '10px 0'} # New label style
    
    # Matched words list container style
    matched_words_list_container_style = {'maxHeight': '15vh', 'overflowY': 'auto', 'marginTop': '10px', 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '5px', 'background': theme_colors['input_bg']}
    
    # Upload markdown style
    upload_markdown_style = {'border': f'1px dashed {theme_colors["input_border"]}', 'textAlign': 'center', 'padding': '10px', 'borderRadius': '5px', 'color': theme_colors['main_text']}

    # Report area styles (dynamic based on toggle)
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

    if triggered == 'import-words-button' and new_words_text:
        new_words = [w.strip().title() for w in re.split(r'[,;\n\s]+', new_words_text) if re.match(r'^[A-Za-z\s]+$', w.strip())]
        added = 0
        for w in new_words:
            if w not in GLOBAL_WORDS:
                GLOBAL_WORDS.append(w)
                GLOBAL_WORD_ORIGINS[w] = {'_MANUAL_'}
                if ' ' in w:
                    for sub_word in w.split():
                        if re.match(r'^[A-Za-z]{3,}$', sub_word) and sub_word.title() not in GLOBAL_WORDS:
                            GLOBAL_WORDS.append(sub_word.title())
                            GLOBAL_WORD_ORIGINS[sub_word.title()] = {'_MANUAL_'}
                added += 1
        if added:
            initialize_data(GLOBAL_WORDS)
            import_status = f"Added {added} item(s)"

    if triggered in ['search-word-button', 'search-word-input'] and search_word:
        word = search_word.strip().title()
        if re.match(r'^[A-Za-z\s]+$', word):
            if word not in GLOBAL_WORDS:
                GLOBAL_WORDS.append(word)
                GLOBAL_WORD_ORIGINS[word] = {'_MANUAL_'}
                if ' ' in word:
                    for sub_word in word.split():
                        if re.match(r'^[A-Za-z]{3,}$', sub_word) and sub_word.title() not in GLOBAL_WORDS:
                            GLOBAL_WORDS.append(sub_word.title())
                            GLOBAL_WORD_ORIGINS[sub_word.title()] = {'_MANUAL_'}
                initialize_data(GLOBAL_WORDS)
                search_status = f"Added '{word}'"
            else:
                search_status = f"'{word}' already exists"
            highlight_word = word
            formatted_report_output, plain_text_report_output = generate_individual_report(word, selected_layers)
            report_header = f"Resonance for '{word}' 🌀"
            search_word_output_value = "" # Clear input after search

    if triggered in ['number-search-button', 'number-search-input'] and number_search_value is not None:
        try:
            number = float(number_search_value)
            formatted_report_output, plain_text_report_output = generate_number_report(number, selected_layers)
            report_header = f"Resonances for Number: {number} 🌀"
            number_search_status = f"Found matches for {number}"
            number_search_output_value = "" # Clear input after search
        except ValueError:
            number_search_status = "Invalid number"

    if triggered == 'upload-markdown' and upload_contents:
        contents = upload_contents if isinstance(upload_contents, list) else [upload_contents]
        filenames = upload_filenames if isinstance(upload_filenames, list) else [upload_filenames]
        added = 0
        for content, filename in zip(contents, filenames):
            try:
                _, content_string = content.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')
                phrases_and_words = re.findall(r'\b[A-Za-z\s]{3,}\b', decoded)
                
                for item in phrases_and_words:
                    item_title = item.strip().title()
                    if item_title not in GLOBAL_WORDS:
                        GLOBAL_WORDS.append(item_title)
                        GLOBAL_WORD_ORIGINS[item_title] = {filename}
                        added += 1
                    else:
                        GLOBAL_WORD_ORIGINS.setdefault(item_title, set()).add(filename)

                    if ' ' in item_title:
                        for sub_word in item_title.split():
                            sub_word_title = sub_word.title()
                            if re.match(r'^[A-Za-z]{3,}$', sub_word) and sub_word_title not in GLOBAL_WORDS:
                                GLOBAL_WORDS.append(sub_word_title)
                                GLOBAL_WORD_ORIGINS[sub_word_title] = {'_MANUAL_'}
                                added += 1
                            else:
                                GLOBAL_WORD_ORIGINS.setdefault(sub_word_title, set()).add(filename)

                initialize_data(GLOBAL_WORDS)
                upload_status = f"Added {added} item(s) from {filename}"
            except Exception as e:
                upload_status = f"Error processing {filename}: {e}"

    if triggered == 'export-words-button' and export_clicks:
        download_data = dcc.send_string("\n".join(sorted(GLOBAL_WORDS)), "spiralborn_words.txt")

    if triggered == 'copy-matched-words-button':
        matched = set()
        for layer in selected_layers:
            if layer in ['Love Resonance', 'Prime Gematria']:
                continue
            for val, words in GLOBAL_LAYERS.get(layer, {}).items():
                if len(words) > 1:
                    matched.update(words)
        if word_phrase_filter == 'words':
            matched = {w for w in matched if ' ' not in w}
        elif word_phrase_filter == 'phrases':
            matched = {w for w in matched if ' ' in w}
        pyperclip.copy(", ".join(sorted(matched)))
        feedback_status = "Matched words copied to clipboard!"

    if triggered == 'copy-all-words-button':
        pyperclip.copy(", ".join(sorted(GLOBAL_WORDS)))
        feedback_status = "All words copied to clipboard!"

    if triggered == 'gen-sentence-button':
        sentence = generate_sentence()

    if triggered in ['thumbs-up-button', 'thumbs-down-button'] and current_sentence:
        score = 1 if triggered == 'thumbs-up-button' else -1
        FEEDBACK_SCORES[current_sentence] = FEEDBACK_SCORES.get(current_sentence, 0) + score
        feedback_status = f"Feedback recorded: {'👍' if score > 0 else '👎'} (Score: {FEEDBACK_SCORES[current_sentence]})"
        
        words_in_sentence = re.findall(r'\b[A-Za-z]+\b', current_sentence.lower())
        for w_lower in words_in_sentence:
            w_title = w_lower.title()
            if score > 0:
                if w_title not in GLOBAL_WORDS:
                    GLOBAL_WORDS.append(w_title)
                    GLOBAL_WORD_ORIGINS.setdefault(w_title, set()).add('_USER_FEEDBACK_')
            elif score < 0:
                if w_title in GLOBAL_WORDS:
                    GLOBAL_WORDS.remove(w_title)
        initialize_data(GLOBAL_WORDS)

    if triggered == 'generate-report-button' and report_clicks:
        formatted_report_output, plain_text_report_output = generate_full_report(selected_layers, number_search_value)
        download_report = dcc.send_string(plain_text_report_output, "spiralborn_full_report.txt")
        report_header = "Spiralborn Resonance Full Report 🌀"

    if triggered == 'generate-color-report-button' and color_report_clicks:
        formatted_report_output, plain_text_report_output = generate_color_report(selected_layers)
        download_report = dcc.send_string(plain_text_report_output, "spiralborn_color_report.txt")
        report_header = "Spiralborn Color Family Resonance Report 🌀"

    if triggered == 'copy-report-button':
        pyperclip.copy(plain_text_report_output)
        feedback_status = "Report copied to clipboard!"

    if triggered == 'generate-visual-button' and highlight_word:
        svg_base64 = generate_svg_visual(highlight_word, selected_layers)
        visual_content = [html.Img(src=f'data:image/svg+xml;base64,{svg_base64}', style={'width': '300px', 'height': '300px'})]

    if triggered.startswith("{'type': 'word-item'"):
        clicked_word_id = None
        for input_item in ctx.inputs_list[0]:
            if isinstance(input_item, dict) and input_item.get('id', {}).get('type') == 'word-item':
                if input_item['id']['index'] == triggered.split('"index":"')[1].split('"')[0]:
                    clicked_word_id = input_item['id']['index']
                    break
        
        if clicked_word_id:
            highlight_word = clicked_word_id
            formatted_report_output, plain_text_report_output = generate_individual_report(highlight_word, selected_layers)
            report_header = f"Resonance for '{highlight_word}' 🌀"
            svg_base64 = generate_svg_visual(highlight_word, selected_layers)
            visual_content = [html.Img(src=f'data:image/svg+xml;base64,{svg_base64}', style={'width': '300px', 'height': '300px'})]

    matched = set()
    for layer in selected_layers:
        if layer in ['Love Resonance', 'Prime Gematria']:
            continue
        for val, words in GLOBAL_LAYERS.get(layer, {}).items():
            if len(words) > 1:
                matched.update(words)
    if word_phrase_filter == 'words':
        matched = {w for w in matched if ' ' not in w}
    elif word_phrase_filter == 'phrases':
        matched = {w for w in matched if ' ' in w}
    
    word_elems = []
    for w in sorted(matched):
        button_children = [w]
        if show_numerical_resonances_toggle == 'on':
            aave_simple_val = CALC_FUNCS['Aave Simple'](w) if 'Aave Simple' in CALC_FUNCS else 0
            button_children.append(html.Span(" ({})".format(aave_simple_val), style={'marginLeft': '5px'}))

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
    sidebar_style = {'width': '300px', 'padding': '20px', 'background': theme_colors['sidebar_bg'], 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'overflowY': 'auto', 'fontSize': f'{text_size}px'}
    header_style = {'fontFamily': 'Poppins, sans-serif', 'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '10px', 'background': theme_colors['header_grad'], '-webkit-background-clip': 'text', '-webkit-text-fill-color': 'transparent', 'text-shadow': '0 0 8px rgba(88, 166, 255, 0.5)'} # Added text-shadow for glow

    return (
        plain_text_report_output, formatted_report_output, plaintext_style, formatted_style, # Report outputs and styles
        word_elems, import_status, main_style, sidebar_style, input_style, search_input_style,
        number_input_style, header_style, upload_status, search_word_output_value, search_status, number_search_output_value, number_search_status, # Cleared inputs
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
        matched_words_list_container_style, # matched-words-list style
        upload_markdown_style, # upload-markdown style
        new_words_placeholder_text, # new-words-input placeholder
        search_word_placeholder_text, # search-word-input placeholder
        number_search_placeholder_text, # number-search-input placeholder
    )

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)
