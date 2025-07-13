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
        'main_bg': 'linear-gradient(135deg, #0a001f, #1c2526)',
        'main_text': '#FFFFFF',
        'sidebar_bg': 'linear-gradient(135deg, #111, #222)',
        'input_bg': '#333',
        'input_text': '#FFD700',
        'input_border': '1px solid #FFD700',
        'button_bg': 'linear-gradient(90deg, #FFD700, #FF6347)',
        'button_text': '#0a001f',
        'report_bg': '#1c2526',
        'report_border': '2px solid #FFD700',
        'header_grad': '#FFD700'
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
        'header_grad': '#4B0082'
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
    hue = (avg_resonance % 360) / 360.0
    rgb = colorsys.hls_to_rgb(hue, 0.5, 0.7)
    r, g, b = [int(x * 255) for x in rgb]
    return f'#{r:02x}{g:02x}{b:02x}', hue * 360

def get_color_family(hue):
    hue = hue % 360
    for family, (start, end) in COLOR_FAMILIES.items():
        if start <= hue < end or (family == 'Red' and hue >= 330):
            return family
    return 'Other'

def generate_individual_report(word, report_layers):
    report = [f"## Resonance for '{word}'"]
    prime_resonances = [f"{layer}: {CALC_FUNCS[layer](word)}" for layer in report_layers if is_prime(CALC_FUNCS[layer](word))]
    report.append("### Prime Resonances")
    report.append(", ".join(prime_resonances) if prime_resonances else "None")
    prime_connections = [c for c in find_prime_connections([word] + [w for w in GLOBAL_WORDS if w != word], report_layers) if word in c]
    report.append("### Prime Connections")
    report.append(", ".join(prime_connections) if prime_connections else "None")
    report.append(f"### Origin\n{', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))}")
    hex_color, hue = get_word_color(word)
    family = get_color_family(hue)
    report.append(f"### Color\n{hex_color} ({family})")
    report.append(f"### Golden Resonance (~137.5)\n{'Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No'}")
    report.append("### Resonances")
    shared_found = False
    for layer in report_layers:
        resonant_words = GLOBAL_LAYERS.get(layer, {}).get(CALC_FUNCS[layer](word), [])
        other_words = [w for w in resonant_words if w != word]
        if other_words:
            report.append(f"#### {layer}\n{', '.join(other_words)}")
            shared_found = True
    if not shared_found:
        report.append("No shared resonances")
    report.append("### Calculations")
    for layer in report_layers:
        val = CALC_FUNCS[layer](word)
        report.append(f"#### {layer}\n{val}{' 🌀' if is_golden_resonance(val) else ''}{' (Prime)' if is_prime(val) else ''}")
    report.append("### Ambidextrous Balance")
    report.append(f"#### Left-Hand Qwerty\n{-left_hand_qwerty(word)}")
    report.append(f"#### Right-Hand Qwerty\n{right_hand_qwerty(word)}")
    report.append(f"#### Balance\n{ambidextrous_balance(word)}")
    report.append("### Shared Resonances Across Layers")
    for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers and word in r[2]], key=lambda x: (x[0], x[1])):
        emotion = RESONANCE_EMOTIONS.get(word, "Other")
        report.append(f"#### {layer}\n{val}: {', '.join(group)} (Emotion: {emotion})")
    return "\n".join(report)

def generate_number_report(number, report_layers):
    report = [f"## Resonances for Number: {number}"]
    report.append(f"### Prime Status\n{'Prime' if is_prime(number) else 'Not Prime'}")
    matched = False
    report.append("### Matches")
    for layer in report_layers:
        words = GLOBAL_LAYERS.get(layer, {}).get(float(number), [])
        if words:
            matched = True
            report.append(f"#### {layer}")
            for word in words:
                hex_color, hue = get_word_color(word)
                family = get_color_family(hue)
                emotion = RESONANCE_EMOTIONS.get(word, "Other")
                report.append(f"- {word} (Color: {hex_color} - {family}, Emotion: {emotion})")
    if not matched:
        report.append("No matches found")
    return "\n".join(report)

def generate_full_report(report_layers, number_filter=None):
    report = ["## Spiralborn Resonance Full Report"]
    prime_connections = find_prime_connections(GLOBAL_WORDS, report_layers)
    report.append("### Prime Connections")
    report.append(", ".join(prime_connections) if prime_connections else "None")
    words_to_report = sorted(GLOBAL_WORDS)
    if number_filter is not None:
        words_to_report = [w for w in words_to_report if any(CALC_FUNCS[l](w) == number_filter for l in report_layers)]
    for word in words_to_report:
        report.append(f"\n### Word/Phrase: {word}")
        prime_resonances = [f"{layer}: {CALC_FUNCS[layer](word)}" for layer in report_layers if is_prime(CALC_FUNCS[layer](word))]
        report.append("#### Prime Resonances")
        report.append(", ".join(prime_resonances) if prime_resonances else "None")
        report.append(f"#### Origin\n{', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))}")
        hex_color, hue = get_word_color(word)
        report.append(f"#### Color\n{hex_color} ({get_color_family(hue)})")
        report.append(f"#### Golden Resonance (~137.5)\n{'Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No'}")
        report.append("#### Resonances")
        shared_found = False
        for layer in report_layers:
            resonant_words = GLOBAL_LAYERS.get(layer, {}).get(CALC_FUNCS[layer](word), [])
            other_words = [w for w in resonant_words if w != word]
            if other_words:
                report.append(f"##### {layer}\n{', '.join(other_words)}")
                shared_found = True
        if not shared_found:
            report.append("No shared resonances")
        report.append("#### Calculations")
        for layer in report_layers:
            val = CALC_FUNCS[layer](word)
            report.append(f"##### {layer}\n{val}{' 🌀' if is_golden_resonance(val) else ''}{' (Prime)' if is_prime(val) else ''}")
        report.append("#### Ambidextrous Balance")
        report.append(f"##### Left-Hand Qwerty\n{-left_hand_qwerty(word)}")
        report.append(f"##### Right-Hand Qwerty\n{right_hand_qwerty(word)}")
        report.append(f"##### Balance\n{ambidextrous_balance(word)}")
        report.append("#### Shared Resonances Across Layers")
        for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers], key=lambda x: (x[0], x[1])):
            if word in group:
                emotion = RESONANCE_EMOTIONS.get(word, "Other")
                report.append(f"##### {layer}\n{val}: {', '.join(group)} (Emotion: {emotion})")
    return "\n".join(report)

def generate_color_report(report_layers):
    color_groups = {family: [] for family in COLOR_FAMILIES}
    color_groups['Other'] = []
    for word in GLOBAL_WORDS:
        hex_color, hue = get_word_color(word)
        family = get_color_family(hue)
        color_groups[family].append(word)
    
    report = ["## Spiralborn Color Family Resonance Report"]
    prime_connections = find_prime_connections(GLOBAL_WORDS, report_layers)
    report.append("### Prime Connections")
    report.append(", ".join(prime_connections) if prime_connections else "None")
    for family, words in color_groups.items():
        if not words:
            continue
        report.append(f"\n### Color Family: {family}")
        report.append(f"#### Words\n{', '.join(sorted(words))}")
        report.append("#### Shared Resonances")
        shared_found = False
        for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers], key=lambda x: (x[0], x[1])):
            group_words = [w for w in group if w in words]
            if len(group_words) > 1:
                report.append(f"##### {layer}\n{val}: {', '.join(group_words)}")
                shared_found = True
        if not shared_found:
            report.append("No shared resonances")
        for word in sorted(words):
            report.append(f"\n#### Word: {word}")
            prime_resonances = [f"{layer}: {CALC_FUNCS[layer](word)}" for layer in report_layers if is_prime(CALC_FUNCS[layer](word))]
            report.append("##### Prime Resonances")
            report.append(", ".join(prime_resonances) if prime_resonances else "None")
            hex_color, hue = get_word_color(word)
            report.append(f"##### Color\n{hex_color} ({get_color_family(hue)})")
            report.append(f"##### Golden Resonance (~137.5)\n{'Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No'}")
            report.append("##### Calculations")
            for layer in report_layers:
                val = CALC_FUNCS[layer](word)
                report.append(f"###### {layer}\n{val}{' 🌀' if is_golden_resonance(val) else ''}{' (Prime)' if is_prime(val) else ''}")
            report.append("##### Ambidextrous Balance")
            report.append(f"###### Left-Hand Qwerty\n{-left_hand_qwerty(word)}")
            report.append(f"###### Right-Hand Qwerty\n{right_hand_qwerty(word)}")
            report.append(f"###### Balance\n{ambidextrous_balance(word)}")
    return "\n".join(report)

def generate_sentence():
    words = random.sample(GLOBAL_WORDS, 3)
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
        '<linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#0a001f"/><stop offset="100%" style="stop-color:#1c2526"/></linearGradient>',
        f'<linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#FFD700"/><stop offset="100%" style="stop-color:#FFB3BA"/></linearGradient>',
        '</defs>',
        '<rect x="-150" y="-150" width="300" height="300" fill="url(#bgGrad)"/>',
        f'<text x="0" y="-130" font-family="Poppins, sans-serif" font-size="14" font-weight="bold" fill="url(#headerGrad)" text-anchor="middle" filter="url(#glow)">{word}: Spiral Resonance 🌀</text>',
        '<defs><filter id="glow"><feGaussianBlur stdDeviation="2.5" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
    ]
    
    spiral_tightness = 0.1 if CALC_FUNCS['Aave Spiral'](word) < 100 else 0.05
    scale = 10
    for resonance, emotion, layer, value in resonances[:5]:  # Limit to 5 for clarity
        theta = math.radians(GOLDEN_ANGLE * value)
        radius = spiral_tightness * math.log1p(value) * scale
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        color = COLOR_MAP.get(emotion, '#FFFFFF')
        svg_content.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}" stroke="#FFD700" stroke-width="1" filter="url(#glow)"/>')
        svg_content.append(f'<text x="{x + 10}" y="{y}" font-family="Poppins, sans-serif" font-size="8" fill="#FFFFFF" filter="url(#glow)">{resonance}</text>')
    
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
        html.Button('Copy Matched Words', id='copy-matched-words-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='matched-words-list', style={'maxHeight': '15vh', 'overflowY': 'auto', 'marginTop': '10px'}),
    ]),
    html.Div(id='report-container', style={'flexGrow': 1, 'padding': '20px', 'display': 'flex', 'flexDirection': 'column'}, children=[
        html.H2(id='report-header', children="Spiralborn Resonance Report 🌀", style={'fontFamily': 'Poppins, sans-serif', 'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '10px'}),
        dcc.Textarea(id='report-output', style={'width': '100%', 'height': '60vh', 'fontFamily': 'Fira Code, monospace', 'fontSize': '12px', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'transition': 'all 0.3s ease'}),
        html.Button('Copy Report', id='copy-report-button', n_clicks=0, style={'width': '100%', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease'}),
        html.Div(id='visual-container', style={'marginTop': '20px', 'textAlign': 'center'}),
    ])
])

# --- Main Callback ---
@app.callback(
    [
        Output('report-output', 'value'),
        Output('matched-words-list', 'children'),
        Output('import-status', 'children'),
        Output('main-div', 'style'),
        Output('sidebar-div', 'style'),
        Output('new-words-input', 'style'),
        Output('search-word-input', 'style'),
        Output('number-search-input', 'style'),
        Output('report-output', 'style'),
        Output('report-header', 'style'),
        Output('upload-status', 'children'),
        Output('search-word-input', 'value'),
        Output('search-status', 'children'),
        Output('number-search-status', 'children'),
        Output('download-word-list', 'data'),
        Output('download-report', 'data'),
        Output('sentence-output', 'children'),
        Output('feedback-status', 'children'),
        Output('visual-container', 'children'),
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
        Input('number-filter', 'value'),
        Input('copy-matched-words-button', 'n_clicks'),
        Input('copy-all-words-button', 'n_clicks'),
        Input('gen-sentence-button', 'n_clicks'),
        Input('thumbs-up-button', 'n_clicks'),
        Input('thumbs-down-button', 'n_clicks'),
        Input({'type': 'word-item', 'index': ALL}, 'n_clicks'),
    ],
    [
        State('new-words-input', 'value'),
        State('search-word-input', 'value'),
        State('number-search-input', 'value'),
        State('upload-markdown', 'filename'),
        State('report-output', 'value'),
        State('sentence-output', 'children'),
    ]
)
def update_app(selected_layers, theme, word_phrase_filter, text_size, import_clicks, search_clicks, search_submit, number_search_clicks, number_search_submit, upload_contents, report_clicks, color_report_clicks, visual_clicks, copy_report_clicks, export_clicks, number_filter, copy_matched_words_clicks, copy_all_words_clicks, gen_sentence_clicks, thumbs_up, thumbs_down, word_clicks, new_words_text, search_word, number_search_value, upload_filenames, current_report, current_sentence):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ''
    theme_colors = THEMES[theme]
    report_output = current_report or ""
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
                    for sub_word in w.split():
                        if re.match(r'^[A-Za-z]{3,}$', sub_word) and sub_word.title() not in GLOBAL_WORDS:
                            GLOBAL_WORDS.append(sub_word.title())
                            GLOBAL_WORD_ORIGINS[sub_word.title()] = {'_MANUAL_'}
                initialize_data(GLOBAL_WORDS)
                search_status = f"Added '{word}'"
            else:
                search_status = f"'{word}' already exists"
            highlight_word = word
            report_output = generate_individual_report(word, selected_layers)
            report_header = f"Resonance for '{word}' 🌀"

    if triggered in ['number-search-button', 'number-search-input'] and number_search_value:
        try:
            number = float(number_search_value)
            report_output = generate_number_report(number, selected_layers)
            report_header = f"Resonances for Number: {number} 🌀"
            number_search_status = f"Found matches for {number}"
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
                phrases = [w.title() for w in re.findall(r'\b[A-Za-z\s]{3,}\b', decoded) if w.title() not in GLOBAL_WORDS and re.match(r'^[A-Za-z\s]+$', w)]
                words = []
                for phrase in phrases:
                    if ' ' in phrase:
                        words.extend([w.title() for w in phrase.split() if re.match(r'^[A-Za-z]{3,}$', w) and w.title() not in GLOBAL_WORDS])
                    if phrase not in GLOBAL_WORDS:
                        GLOBAL_WORDS.append(phrase)
                        GLOBAL_WORD_ORIGINS[phrase] = {filename}
                        added += 1
                for w in words:
                    if w not in GLOBAL_WORDS:
                        GLOBAL_WORDS.append(w)
                        GLOBAL_WORD_ORIGINS[w] = {filename}
                        added += 1
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
        words = [w.lower() for w in current_sentence.split() if w.lower() in [w.lower() for w in GLOBAL_WORDS]]
        for w in words:
            if w in [w.lower() for w in GLOBAL_WORDS]:
                GLOBAL_WORDS.append(w.title()) if score > 0 else GLOBAL_WORDS.remove(w.title()) if w.title() in GLOBAL_WORDS and score < 0 else None

    if triggered == 'generate-report-button' and report_clicks:
        report_output = generate_full_report(selected_layers, number_filter)
        download_report = dcc.send_string(report_output, "spiralborn_full_report.txt")
        report_header = "Spiralborn Resonance Full Report 🌀"

    if triggered == 'generate-color-report-button' and color_report_clicks:
        report_output = generate_color_report(selected_layers)
        download_report = dcc.send_string(report_output, "spiralborn_color_report.txt")
        report_header = "Spiralborn Color Family Resonance Report 🌀"

    if triggered == 'copy-report-button' and current_report:
        pyperclip.copy(current_report)
        feedback_status = "Report copied to clipboard!"

    if triggered == 'generate-visual-button' and highlight_word:
        svg_base64 = generate_svg_visual(highlight_word, selected_layers)
        visual_content = [html.Img(src=f'data:image/svg+xml;base64,{svg_base64}', style={'width': '300px', 'height': '300px'})]

    if triggered.startswith("{'type': 'word-item'"):
        for i, click in enumerate(word_clicks):
            if click and ctx.triggered[0]['value']:
                highlight_word = ctx.triggered[0]['prop_id'].split('"index":"')[1].split('"')[0]
                report_output = generate_individual_report(highlight_word, selected_layers)
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
    word_elems = [
        html.Button(
            w, 
            style={
                'padding': '8px 12px', 
                'margin': '5px', 
                'borderRadius': '15px', 
                'backgroundColor': get_word_color(w)[0], 
                'color': '#FFFFFF', 
                'border': 'none', 
                'cursor': 'pointer', 
                'fontSize': f'{text_size}px', 
                'transition': 'transform 0.2s ease, box-shadow 0.2s ease'
            }, 
            id={'type': 'word-item', 'index': w}
        ) for w in sorted(matched)
    ]

    main_style = {'background': theme_colors['main_bg'], 'color': theme_colors['main_text'], 'height': '100vh', 'display': 'flex', 'fontFamily': 'Poppins, sans-serif'}
    sidebar_style = {'width': '300px', 'padding': '20px', 'background': theme_colors['sidebar_bg'], 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)', 'overflowY': 'auto', 'fontSize': f'{text_size}px'}
    input_style = {'width': '100%', 'height': '80px', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}
    search_input_style = {'width': '100%', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}
    number_input_style = {'width': '100%', 'background': theme_colors['input_bg'], 'color': theme_colors['input_text'], 'border': theme_colors['input_border'], 'borderRadius': '5px', 'padding': '8px', 'fontSize': f'{text_size}px', 'transition': 'all 0.3s ease'}
    report_style = {'width': '100%', 'height': '60vh', 'background': theme_colors['report_bg'], 'color': theme_colors['main_text'], 'border': theme_colors['report_border'], 'borderRadius': '10px', 'padding': '10px', 'fontSize': f'{text_size}px', 'fontFamily': 'Fira Code, monospace', 'transition': 'all 0.3s ease', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}
    header_style = {'fontFamily': 'Poppins, sans-serif', 'fontSize': '24px', 'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '10px', 'color': theme_colors['header_grad']}

    button_style = {'background': theme_colors['button_bg'], 'color': theme_colors['button_text'], 'border': 'none', 'borderRadius': '5px', 'padding': '10px', 'cursor': 'pointer', 'transition': 'transform 0.2s ease, box-shadow 0.2s ease'}
    button_ids = ['import-words-button', 'search-word-button', 'number-search-button', 'gen-sentence-button', 'copy-all-words-button', 'generate-report-button', 'generate-color-report-button', 'generate-visual-button', 'copy-matched-words-button', 'export-words-button', 'copy-report-button']
    for child in app.layout.children[0].children:
        if hasattr(child, 'id') and child.id in button_ids:
            if child.style is None:
                child.style = {}
            child.style.update(button_style)
        elif child.id == 'thumbs-up-button':
            child.style.update({'background': 'linear-gradient(90deg, #98FF98, #FFD700)', 'color': '#0a001f'})
        elif child.id == 'thumbs-down-button':
            child.style.update({'background': 'linear-gradient(90deg, #FFB3BA, #FFD700)', 'color': '#0a001f'})

    return (
        report_output, word_elems, import_status, main_style, sidebar_style, input_style, search_input_style,
        number_input_style, report_style, header_style, upload_status, "", search_status, number_search_status,
        download_data, download_report, sentence, feedback_status, visual_content
    )

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)