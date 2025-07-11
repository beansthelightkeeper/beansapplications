import dash
from dash import dcc, html, Input, Output, State, ALL
import networkx as nx
import plotly.graph_objects as go
import math
import numpy as np
import re
import base64
import io
import pyperclip
import colorsys

# --- Constants and Data ---
WORDS = [
    "Beans", "Dream", "Spiral", "Love", "Heart", "Soul", "Trust", "Hope",
    "Spirit", "Light", "Truth", "Energy", "Infinity", "Divine", "Spiralborn",
    "Children of the Beans"
]
LAYER_COLORS = {
    "Simple": "cyan", "Jewish Gematria": "yellow", "Qwerty": "lime",
    "Left-Hand Qwerty": "purple", "Right-Hand Qwerty": "pink",
    "Binary Sum": "lightgray", "Love Resonance": "red",
    "Frequent Letters": "orange", "Leet Code": "magenta", "Simple Forms": "teal",
    "Prime Gematria": "gold"
}
NAMED_COLORS_MAP = {
    'red': '#FF0000', 'orange': '#FFA500', 'yellow': '#FFFF00', 'green': '#008000',
    'cyan': '#00FFFF', 'blue': '#0000FF', 'magenta': '#FF00FF', 'lime': '#00FF00',
    'pink': '#FFC0CB', 'purple': '#800080', 'lightgray': '#D3D3D3', 'white': '#FFFFFF',
    'gold': '#FFD700', 'black': '#000000', 'teal': '#008080'
}
THEMES = {
    'dark': {'main_bg': 'black', 'main_text': 'white', 'sidebar_bg': '#111',
             'input_bg': '#333', 'input_text': 'white', 'input_border': '1px solid #555',
             'graph_bg': '#0a001f', 'text_color': None},
    'light': {'main_bg': 'white', 'main_text': 'black', 'sidebar_bg': '#eee',
              'input_bg': '#fff', 'input_text': 'black', 'input_border': '1px solid #aaa',
              'graph_bg': '#fff', 'text_color': 'black'}
}
GOLDEN_ANGLE = 137.5  # Spiralborn love pattern
PASTEL_COLORS = ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF']
PRIME_GLOW = "gold"
FADE_OPACITY = 0.15

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

LEFT_HAND_KEYS = set('QWERTYASDFGZXCVB')
RIGHT_HAND_KEYS = set('YUIOPHJKLNM')
def left_hand_qwerty(word):
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in LEFT_HAND_KEYS)

def right_hand_qwerty(word):
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
    for i in range(2, int(math.isqrt(int(num))) + 1):
        if num % i == 0:
            return False
    return True

def prime_gematria(word):
    val = simple(word)
    return val if is_prime(val) else 0

def ambidextrous_balance(word):
    return -left_hand_qwerty(word) + right_hand_qwerty(word)

def is_golden_resonance(val):
    return isinstance(val, (int, float)) and (abs(val - 137) <= 5 or abs(val - 137.5) <= 5)

CALC_FUNCS = {
    "Simple": simple, "Jewish Gematria": jewish_gematria, "Qwerty": qwerty,
    "Left-Hand Qwerty": left_hand_qwerty, "Right-Hand Qwerty": right_hand_qwerty,
    "Binary Sum": binary_sum, "Love Resonance": love_resonance,
    "Frequent Letters": frequent_letters, "Leet Code": leet_code,
    "Simple Forms": simple_forms, "Prime Gematria": prime_gematria
}

# --- Color Detection for Words ---
def get_word_color(word):
    # Compute color based on shared resonances
    resonance_sum = 0
    resonance_count = 0
    for layer, val, group in GLOBAL_SHARED_RESONANCES:
        if layer in ['Love Resonance', 'Prime Gematria']:
            continue
        if word in group:
            resonance_sum += val
            resonance_count += 1
    # Use average resonance value to determine hue, fixed saturation/lightness for vibrancy
    avg_resonance = resonance_sum / max(resonance_count, 1)
    hue = (avg_resonance % 360) / 360.0  # Map to [0, 1] for HSL
    rgb = colorsys.hls_to_rgb(hue, 0.5, 0.7)  # Saturation=0.5, Lightness=0.7
    r, g, b = [int(x * 255) for x in rgb]
    return f'#{r:02x}{g:02x}{b:02x}'

# --- Global Data ---
GLOBAL_WORDS = list(WORDS)
GLOBAL_LAYERS = {}
GLOBAL_G = nx.Graph()
GLOBAL_POS = {}
GLOBAL_NODE_COLORS = {}
GLOBAL_EDGES_BY_LAYER = {}
GLOBAL_WORD_ORIGINS = {w: {'_MANUAL_'} for w in GLOBAL_WORDS}
GLOBAL_SHARED_RESONANCES = []

def initialize_graph_data(current_words, layout='spiral'):
    global GLOBAL_WORDS, GLOBAL_LAYERS, GLOBAL_G, GLOBAL_POS, GLOBAL_NODE_COLORS, GLOBAL_EDGES_BY_LAYER, GLOBAL_WORD_ORIGINS, GLOBAL_SHARED_RESONANCES
    GLOBAL_WORDS = list(set(w.title() for w in current_words if re.match(r'^[A-Za-z\s]+$', w)))
    for w in GLOBAL_WORDS:
        GLOBAL_WORD_ORIGINS.setdefault(w, {'_MANUAL_'})

    # Build resonance layers
    GLOBAL_LAYERS = {layer: {} for layer in CALC_FUNCS}
    for layer, func in CALC_FUNCS.items():
        for w in GLOBAL_WORDS:
            val = func(w)
            GLOBAL_LAYERS[layer].setdefault(val, []).append(w)

    # Build graph and shared resonances
    GLOBAL_G = nx.Graph()
    GLOBAL_G.add_nodes_from(GLOBAL_WORDS)
    GLOBAL_EDGES_BY_LAYER = {}
    GLOBAL_SHARED_RESONANCES = []
    for layer, groups in GLOBAL_LAYERS.items():
        GLOBAL_EDGES_BY_LAYER[layer] = []
        for val, group in groups.items():
            if len(group) > 1:
                GLOBAL_SHARED_RESONANCES.append((layer, val, group))
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        GLOBAL_EDGES_BY_LAYER[layer].append((group[i], group[j], val))

    # Layouts: Spiral, Circular, Sphere, Hexagonal Prism, Pyramid
    GLOBAL_POS = {}
    n_nodes = len(GLOBAL_G.nodes())
    if layout == 'spiral':
        if 'Beans' in GLOBAL_WORDS:
            GLOBAL_POS['Beans'] = [0, 0, 0]
        theta, radius, z = 0, 1, 0
        for node in [n for n in GLOBAL_G.nodes() if n != 'Beans']:
            theta_rad = np.radians(theta)
            GLOBAL_POS[node] = [radius * np.cos(theta_rad), radius * np.sin(theta_rad), z]
            theta += GOLDEN_ANGLE
            radius += 0.5 * (1 + np.log1p(len(GLOBAL_POS)))
            z += 0.1
    elif layout == 'circular':
        radius = 10
        for i, node in enumerate(GLOBAL_G.nodes()):
            theta = 2 * np.pi * i / n_nodes
            GLOBAL_POS[node] = [radius * np.cos(theta), radius * np.sin(theta), 0]
    elif layout == 'sphere':
        radius = 10
        for i, node in enumerate(GLOBAL_G.nodes()):
            phi = np.arccos(1 - 2 * (i + 0.5) / n_nodes)
            theta = np.pi * (1 + 5**0.5) * i
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            GLOBAL_POS[node] = [x, y, z]
    elif layout == 'hexagonal_prism':
        radius = 10
        height = 10
        for i, node in enumerate(GLOBAL_G.nodes()):
            layer = i % 2
            angle = 2 * np.pi * (i // 2) / (n_nodes // 2 + 1)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = layer * height
            GLOBAL_POS[node] = [x, y, z]
    elif layout == 'pyramid':
        base_size = 10
        height = 10
        for i, node in enumerate(GLOBAL_G.nodes()):
            if i == 0:
                GLOBAL_POS[node] = [0, 0, height]  # Apex
            else:
                angle = 2 * np.pi * (i - 1) / (n_nodes - 1)
                x = base_size * np.cos(angle)
                y = base_size * np.sin(angle)
                z = 0
                GLOBAL_POS[node] = [x, y, z]

    # Assign node colors based on resonances
    GLOBAL_NODE_COLORS = {n: get_word_color(n) for n in GLOBAL_G.nodes()}

initialize_graph_data(GLOBAL_WORDS)

# --- Generate Individual Report ---
def generate_individual_report(word, report_layers):
    report = [f"Resonance for '{word}'"]
    report.append(f"Origin: {', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))}")
    report.append(f"Golden Resonance (~137.5): {'Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No'}")
    report.append("Resonances:")
    shared_found = False
    for layer in report_layers:
        resonant_words = GLOBAL_LAYERS.get(layer, {}).get(CALC_FUNCS[layer](word), [])
        other_words = [w for w in resonant_words if w != word]
        if other_words:
            report.append(f"  {layer}: {', '.join(other_words)}")
            shared_found = True
    if not shared_found:
        report.append("  No shared resonances")
    report.append("Calculations:")
    for layer in report_layers:
        val = CALC_FUNCS[layer](word)
        report.append(f"  {layer}: {val}{' 🌀' if is_golden_resonance(val) else ''}")
    report.append("Ambidextrous Balance:")
    report.append(f"  Left-Hand Qwerty: {-left_hand_qwerty(word)}")
    report.append(f"  Right-Hand Qwerty: {right_hand_qwerty(word)}")
    report.append(f"  Balance: {ambidextrous_balance(word)}")
    report.append("Shared Resonances Across Layers:")
    for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers and word in r[2]], key=lambda x: (x[0], x[1])):
        report.append(f"  {layer}: {val}: {', '.join(group)}")
    return "\n".join(report)

# --- Generate Full Report ---
def generate_full_report(report_layers, number_filter=None):
    report = ["Spiralborn Resonance Full Report"]
    words_to_report = sorted(GLOBAL_WORDS)
    if number_filter is not None:
        words_to_report = [w for w in words_to_report if any(CALC_FUNCS[l](w) == number_filter for l in report_layers)]

    for word in words_to_report:
        report.append(f"\nWord/Phrase: {word}")
        report.append(f"Origin: {', '.join(GLOBAL_WORD_ORIGINS.get(word, {'Unknown'}))}")
        report.append(f"Color: {get_word_color(word)}")
        report.append(f"Golden Resonance (~137.5): {'Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](word)) for l in report_layers) else 'No'}")
        report.append("Resonances:")
        shared_found = False
        for layer in report_layers:
            resonant_words = GLOBAL_LAYERS.get(layer, {}).get(CALC_FUNCS[layer](word), [])
            other_words = [w for w in resonant_words if w != word]
            if other_words:
                report.append(f"  {layer}: {', '.join(other_words)}")
                shared_found = True
        if not shared_found:
            report.append("  No shared resonances")
        report.append("Calculations:")
        for layer in report_layers:
            val = CALC_FUNCS[layer](word)
            report.append(f"  {layer}: {val}{' 🌀' if is_golden_resonance(val) else ''}")
        report.append("Ambidextrous Balance:")
        report.append(f"  Left-Hand Qwerty: {-left_hand_qwerty(word)}")
        report.append(f"  Right-Hand Qwerty: {right_hand_qwerty(word)}")
        report.append(f"  Balance: {ambidextrous_balance(word)}")
        report.append("Shared Resonances Across Layers:")
        for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layers], key=lambda x: (x[0], x[1])):
            if word in group:
                report.append(f"  {layer}: {val}: {', '.join(group)}")
    return "\n".join(report)

# --- Dash App ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.layout = html.Div(id='main-div', style={'display': 'flex', 'height': '100vh'}, children=[
    # Sidebar
    html.Div(id='sidebar-div', style={'width': '300px', 'padding': '20px', 'backgroundColor': THEMES['dark']['sidebar_bg'], 'overflowY': 'auto'}, children=[
        html.H2("Spiralborn Resonance 🌀"),
        html.Hr(),
        dcc.RadioItems(id='theme-toggle', options=[
            {'label': 'Dark', 'value': 'dark'}, {'label': 'Light', 'value': 'light'}
        ], value='dark', labelStyle={'display': 'block'}),
        html.Hr(),
        dcc.RadioItems(id='layout-toggle', options=[
            {'label': 'Spiral', 'value': 'spiral'}, {'label': 'Circular', 'value': 'circular'},
            {'label': 'Sphere', 'value': 'sphere'}, {'label': 'Hexagonal Prism', 'value': 'hexagonal_prism'},
            {'label': 'Pyramid', 'value': 'pyramid'}
        ], value='spiral', labelStyle={'display': 'block'}),
        html.Hr(),
        dcc.RadioItems(id='word-phrase-toggle', options=[
            {'label': 'Words', 'value': 'words'}, {'label': 'Phrases', 'value': 'phrases'},
            {'label': 'All', 'value': 'all'}
        ], value='all', labelStyle={'display': 'block'}),
        html.Hr(),
        html.Label("Text Size:"),
        dcc.Slider(id='text-size-slider', min=8, max=16, step=1, value=10, marks={8: '8px', 12: '12px', 16: '16px'}),
        html.Hr(),
        html.Label("Add Words/Phrases:"),
        dcc.Textarea(id='new-words-input', placeholder='Enter words/phrases (e.g., Word1, Children of the Beans)', style={'width': '100%', 'height': '80px'}),
        html.Button('Import', id='import-words-button', n_clicks=0),
        html.Div(id='import-status'),
        html.Hr(),
        html.Label("Upload Markdown:"),
        dcc.Upload(id='upload-markdown', children=html.A('Select Markdown File'), style={'border': '1px dashed', 'textAlign': 'center', 'padding': '10px'}, multiple=True),
        html.Div(id='upload-status'),
        html.Hr(),
        html.Label("Search/Add Word/Phrase:"),
        dcc.Input(id='search-word-input', type='text', placeholder='Search or add word/phrase', style={'width': '100%'}),
        html.Button('Search/Add', id='search-word-button', n_clicks=0),
        html.Div(id='search-status'),
        html.Hr(),
        html.Label("Resonance Layers:"),
        dcc.Checklist(id='layer-checklist', options=[{'label': k, 'value': k} for k in CALC_FUNCS], value=['Simple'], labelStyle={'display': 'block'}),
        html.Hr(),
        html.Label("Report Layers:"),
        dcc.Checklist(id='report-layer-filter', options=[{'label': k, 'value': k} for k in CALC_FUNCS if k not in ['Love Resonance', 'Prime Gematria']], value=[k for k in CALC_FUNCS if k not in ['Love Resonance', 'Prime Gematria']], labelStyle={'display': 'block'}),
        html.Hr(),
        html.Label("Filter by Source:"),
        dcc.Dropdown(id='source-filter', options=[{'label': '_MANUAL_', 'value': '_MANUAL_'}], multi=True, placeholder='Select sources...'),
        html.Hr(),
        html.Label("Filter by Number:"),
        dcc.Input(id='number-filter', type='number', placeholder='Enter gematria value', style={'width': '100%'}),
        html.Hr(),
        html.Label("Filter by Primes:"),
        dcc.Checklist(id='prime-filter', options=[{'label': 'Prime Values Only', 'value': 'prime'}], value=[]),
        html.Hr(),
        html.Label("Shared Resonances:"),
        html.Div(id='shared-resonances-list', style={'maxHeight': '15vh', 'overflowY': 'auto'}),
        html.Hr(),
        html.Label("Matched Words/Phrases:"),
        html.Div(id='matched-words-list', style={'maxHeight': '15vh', 'overflowY': 'auto'}),
        html.Hr(),
        html.Label("Reports:"),
        html.Button('Generate Report', id='generate-report-button', n_clicks=0),
        dcc.Download(id='download-report'),
        html.Hr(),
        html.Label("Export Words:"),
        html.Button('Export', id='export-words-button', n_clicks=0),
        dcc.Download(id='download-word-list'),
    ]),
    # Graph and Modals
    html.Div(id='graph-container', style={'flexGrow': 1}, children=[
        dcc.Graph(id='resonance-graph', style={'height': '100vh'}),
        html.Div(id='node-report-modal', style={'display': 'none', 'position': 'fixed', 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 'width': '400px', 'maxHeight': '40vh', 'overflowY': 'auto', 'backgroundColor': 'rgba(0,0,0,0.9)', 'border': '2px solid gold', 'padding': '20px'}, children=[
            html.Button('✕', id='modal-x-button', style={'position': 'absolute', 'top': '5px', 'right': '5px', 'background': 'none', 'border': 'none', 'color': 'gold', 'fontSize': '16px'}),
            html.Button('Copy Report', id='copy-report-button', style={'position': 'absolute', 'top': '5px', 'left': '5px', 'background': 'none', 'border': '1px solid gold', 'color': 'gold'}),
            html.H3(id='modal-title', style={'color': 'gold', 'marginTop': '30px'}),
            html.Div(id='modal-content', style={'color': 'white'}),
            html.Button('Close', id='modal-close-button', style={'marginTop': '10px'})
        ]),
        html.Div(id='full-report-modal', style={'display': 'none', 'position': 'fixed', 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 'width': '600px', 'maxHeight': '60vh', 'overflowY': 'auto', 'backgroundColor': 'rgba(0,0,0,0.9)', 'border': '2px solid gold', 'padding': '20px'}, children=[
            html.Button('✕', id='full-report-x-button', style={'position': 'absolute', 'top': '5px', 'right': '5px', 'background': 'none', 'border': 'none', 'color': 'gold', 'fontSize': '16px'}),
            html.Button('Copy Report', id='full-report-copy-button', style={'position': 'absolute', 'top': '5px', 'left': '5px', 'background': 'none', 'border': '1px solid gold', 'color': 'gold'}),
            html.H3("Full Resonance Report", style={'color': 'gold', 'marginTop': '30px'}),
            html.Div(id='full-report-content', style={'color': 'white'}),
            html.Button('Close', id='full-report-close-button', style={'marginTop': '10px'})
        ])
    ])
])

# --- Build Graph Figure ---
def build_graph_figure(selected_layers, highlight_word=None, theme='dark', source_filter=None, number_filter=None, prime_filter=False, resonance_filter=None, word_phrase_filter='all', text_size=10):
    fig = go.Figure()
    theme_colors = THEMES[theme]
    nodes_to_draw = set(GLOBAL_G.nodes())

    # Apply word/phrase filter
    if word_phrase_filter == 'words':
        nodes_to_draw = {n for n in nodes_to_draw if ' ' not in n}
    elif word_phrase_filter == 'phrases':
        nodes_to_draw = {n for n in nodes_to_draw if ' ' in n}

    # Apply other filters
    if source_filter:
        nodes_to_draw = nodes_to_draw.intersection(
            {w for w, origins in GLOBAL_WORD_ORIGINS.items() if any(s in origins for s in source_filter)}
        )
    if number_filter is not None:
        nodes_to_draw = nodes_to_draw.intersection(
            {w for w in GLOBAL_WORDS if any(CALC_FUNCS[l](w) == number_filter for l in CALC_FUNCS if l not in ['Love Resonance', 'Prime Gematria'])}
        )
    if prime_filter:
        nodes_to_draw = nodes_to_draw.intersection(
            {w for w in GLOBAL_WORDS if any(is_prime(CALC_FUNCS[l](w)) for l in CALC_FUNCS if l not in ['Love Resonance', 'Prime Gematria'])}
        )
    if resonance_filter:
        layer, val = resonance_filter
        nodes_to_draw = nodes_to_draw.intersection(
            set(GLOBAL_LAYERS.get(layer, {}).get(val, []))
        )

    nodes_to_render_fully = nodes_to_draw if not highlight_word else {highlight_word}.union(
        {v for layer in selected_layers for u, v, _ in GLOBAL_EDGES_BY_LAYER.get(layer, []) if u == highlight_word}
    )

    # Edges
    for layer in selected_layers:
        for u, v, val in GLOBAL_EDGES_BY_LAYER.get(layer, []):
            if u not in nodes_to_draw or v not in nodes_to_draw:
                continue
            if highlight_word and not (u == highlight_word or v == highlight_word):
                continue
            color = NAMED_COLORS_MAP.get(PRIME_GLOW if is_prime(val) and layer != "Binary Sum" else LAYER_COLORS[layer], '#FFFFFF')
            width = 7 if highlight_word and (u == highlight_word or v == highlight_word) else 3
            fig.add_trace(go.Scatter3d(
                x=[GLOBAL_POS[u][0], GLOBAL_POS[v][0], None],
                y=[GLOBAL_POS[u][1], GLOBAL_POS[v][1], None],
                z=[GLOBAL_POS[u][2], GLOBAL_POS[v][2], None],
                mode='lines', line=dict(color=color, width=width),
                hoverinfo='text', text=[f"{layer}: {val}", f"{layer}: {val}", None],
                name=f"{layer} ({val})"
            ))

    # Nodes
    x, y, z, colors, sizes, texts, text_colors = [], [], [], [], [], [], []
    for n in nodes_to_draw:
        is_highlight = n == highlight_word
        opacity = 1.0 if n in nodes_to_render_fully else FADE_OPACITY
        hex_color = GLOBAL_NODE_COLORS[n]
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        x.append(GLOBAL_POS[n][0])
        y.append(GLOBAL_POS[n][1])
        z.append(GLOBAL_POS[n][2])
        colors.append(f'rgba({r},{g},{b},{opacity})')
        sizes.append(20 if is_highlight else 10)
        texts.append(n)
        text_colors.append(PASTEL_COLORS[hash(n) % len(PASTEL_COLORS)] if theme == 'dark' else 'black')

    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z, mode='markers+text', marker=dict(size=sizes, color=colors, line=dict(color='white', width=1)),
        text=texts, textposition='top center', textfont=dict(color=text_colors, size=text_size), hovertext=texts, name="Nodes"
    ))

    fig.update_layout(
        scene=dict(bgcolor=theme_colors['graph_bg'], xaxis=dict(showbackground=False, showticklabels=False),
                   yaxis=dict(showbackground=False, showticklabels=False), zaxis=dict(showbackground=False, showticklabels=False)),
        paper_bgcolor=theme_colors['main_bg'], showlegend=True, title="Children of the Beans Spiral 🌀"
    )
    return fig

# --- Main Callback ---
@app.callback(
    [
        Output('matched-words-list', 'children'),
        Output('resonance-graph', 'figure'),
        Output('import-status', 'children'),
        Output('main-div', 'style'),
        Output('sidebar-div', 'style'),
        Output('new-words-input', 'style'),
        Output('search-word-input', 'style'),
        Output('upload-status', 'children'),
        Output('node-report-modal', 'style'),
        Output('modal-title', 'children'),
        Output('modal-content', 'style'),
        Output('modal-content', 'children'),
        Output('search-word-input', 'value'),
        Output('search-status', 'children'),
        Output('download-word-list', 'data'),
        Output('source-filter', 'options'),
        Output('shared-resonances-list', 'children'),
        Output('download-report', 'data'),
        Output('full-report-modal', 'style'),
        Output('full-report-content', 'style'),
        Output('full-report-content', 'children'),
    ],
    [
        Input('layer-checklist', 'value'),
        Input('theme-toggle', 'value'),
        Input('layout-toggle', 'value'),
        Input('word-phrase-toggle', 'value'),
        Input('text-size-slider', 'value'),
        Input('import-words-button', 'n_clicks'),
        Input('search-word-button', 'n_clicks'),
        Input('search-word-input', 'n_submit'),
        Input('upload-markdown', 'contents'),
        Input('resonance-graph', 'clickData'),
        Input('modal-close-button', 'n_clicks'),
        Input('modal-x-button', 'n_clicks'),
        Input('copy-report-button', 'n_clicks'),
        Input('export-words-button', 'n_clicks'),
        Input('source-filter', 'value'),
        Input('number-filter', 'value'),
        Input('prime-filter', 'value'),
        Input('report-layer-filter', 'value'),
        Input({'type': 'word-item', 'index': ALL}, 'n_clicks'),
        Input({'type': 'resonance-item', 'index': ALL}, 'n_clicks'),
        Input('generate-report-button', 'n_clicks'),
        Input('full-report-close-button', 'n_clicks'),
        Input('full-report-x-button', 'n_clicks'),
        Input('full-report-copy-button', 'n_clicks'),
    ],
    [
        State('new-words-input', 'value'),
        State('search-word-input', 'value'),
        State('upload-markdown', 'filename'),
        State('modal-content', 'children'),
        State('full-report-content', 'children'),
    ]
)
def update_app(selected_layers, theme, layout, word_phrase_filter, text_size, import_clicks, search_clicks, search_submit, upload_contents, click_data, close_clicks, x_clicks, copy_clicks, export_clicks, source_filter, number_filter, prime_filter, report_layer_filter, word_clicks, resonance_clicks, report_clicks, full_close_clicks, full_x_clicks, full_copy_clicks, new_words_text, search_word, upload_filenames, modal_content, full_report_content):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ''
    theme_colors = THEMES[theme]
    highlight_word = None
    import_status = ""
    upload_status = ""
    search_status = ""
    modal_style = {'display': 'none'}
    modal_title = ""
    modal_content = []
    modal_content_style = {'color': 'white', 'fontSize': f'{text_size + 2}px'}
    download_data = None
    download_report = None
    full_report_style = {'display': 'none'}
    full_report_content = []
    full_report_content_style = {'color': 'white', 'fontSize': f'{text_size + 2}px'}

    # Handle layout change
    if triggered == 'layout-toggle':
        initialize_graph_data(GLOBAL_WORDS, layout)

    # Handle search/add
    if triggered in ['search-word-button', 'search-word-input'] and search_word:
        word = search_word.strip().title()
        if re.match(r'^[A-Za-z\s]+$', word) and word not in GLOBAL_WORDS:
            GLOBAL_WORDS.append(word)
            GLOBAL_WORD_ORIGINS[word] = {'_MANUAL_'}
            # Add individual words from phrases
            if ' ' in word:
                for sub_word in word.split():
                    if re.match(r'^[A-Za-z]{3,}$', sub_word) and sub_word.title() not in GLOBAL_WORDS:
                        GLOBAL_WORDS.append(sub_word.title())
                        GLOBAL_WORD_ORIGINS[sub_word.title()] = {'_MANUAL_'}
            initialize_graph_data(GLOBAL_WORDS, layout)
            search_status = f"Added '{word}'"
            highlight_word = word
        elif word in GLOBAL_WORDS:
            search_status = f"'{word}' already exists"
            highlight_word = word
        else:
            search_status = "Invalid word/phrase"

    # Handle word/phrase import
    if triggered == 'import-words-button' and new_words_text:
        new_words = [w.strip().title() for w in re.split(r'[,;\n\s]+', new_words_text) if re.match(r'^[A-Za-z\s]+$', w.strip())]
        added = 0
        for w in new_words:
            if w not in GLOBAL_WORDS:
                GLOBAL_WORDS.append(w)
                GLOBAL_WORD_ORIGINS[w] = {'_MANUAL_'}
                # Add individual words from phrases
                if ' ' in w:
                    for sub_word in w.split():
                        if re.match(r'^[A-Za-z]{3,}$', sub_word) and sub_word.title() not in GLOBAL_WORDS:
                            GLOBAL_WORDS.append(sub_word.title())
                            GLOBAL_WORD_ORIGINS[sub_word.title()] = {'_MANUAL_'}
                added += 1
        if added:
            initialize_graph_data(GLOBAL_WORDS, layout)
            import_status = f"Added {added} item(s)"

    # Handle markdown upload
    if triggered == 'upload-markdown' and upload_contents:
        contents = upload_contents if isinstance(upload_contents, list) else [upload_contents]
        filenames = upload_filenames if isinstance(upload_filenames, list) else [upload_filenames]
        added = 0
        for content, filename in zip(contents, filenames):
            try:
                _, content_string = content.split(',')
                decoded = base64.b64decode(content_string).decode('utf-8')
                # Extract phrases and words
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
                initialize_graph_data(GLOBAL_WORDS, layout)
                upload_status = f"Added {added} item(s) from {filename}"
            except Exception as e:
                upload_status = f"Error processing {filename}: {e}"

    # Handle export
    if triggered == 'export-words-button' and export_clicks:
        download_data = dcc.send_string("\n".join(sorted(GLOBAL_WORDS)), "spiralborn_words.txt")

    # Handle graph click
    if triggered == 'resonance-graph' and click_data:
        highlight_word = click_data['points'][0]['text']

    # Handle word click
    if triggered.startswith("{'type': 'word-item'"):
        for i, click in enumerate(word_clicks):
            if click and ctx.triggered[0]['value']:
                highlight_word = ctx.triggered[0]['prop_id'].split('"index":"')[1].split('"')[0]

    # Handle resonance click
    if triggered.startswith("{'type': 'resonance-item'"):
        for i, click in enumerate(resonance_clicks):
            if click and ctx.triggered[0]['value']:
                layer_val = ctx.triggered[0]['prop_id'].split('"index":"')[1].split('"')[0]
                layer, val = layer_val.split(':')
                val = int(val) if val.isdigit() else float(val)
                resonance_filter = (layer, val)
    else:
        resonance_filter = None

    # Handle individual report copy
    if triggered == 'copy-report-button' and highlight_word:
        report_text = generate_individual_report(highlight_word, report_layer_filter)
        pyperclip.copy(report_text)
        modal_content.append(html.P("Report copied to clipboard!", style={'color': 'gold', 'fontSize': f'{text_size + 2}px'}))

    # Handle full report generation
    if triggered == 'generate-report-button' and report_clicks:
        report_text = generate_full_report(report_layer_filter, number_filter)
        download_report = dcc.send_string(report_text, "spiralborn_full_report.txt")
        full_report_style = {'display': 'block', 'position': 'fixed', 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 'width': '600px', 'maxHeight': '60vh', 'overflowY': 'auto', 'backgroundColor': 'rgba(0,0,0,0.9)', 'border': '2px solid gold', 'padding': '20px'}
        full_report_content = [html.P(line, style={'fontSize': f'{text_size + 2}px'}) for line in report_text.split('\n')]

    # Handle full report copy
    if triggered == 'full-report-copy-button':
        report_text = generate_full_report(report_layer_filter, number_filter)
        pyperclip.copy(report_text)
        full_report_content.append(html.P("Full report copied to clipboard!", style={'color': 'gold', 'fontSize': f'{text_size + 2}px'}))

    # Handle full report close
    if triggered in ['full-report-close-button', 'full-report-x-button']:
        full_report_style = {'display': 'none'}

    # Modal content for individual word/phrase
    if highlight_word and triggered not in ['modal-close-button', 'modal-x-button']:
        modal_style = {'display': 'block', 'position': 'fixed', 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', 'width': '400px', 'maxHeight': '40vh', 'overflowY': 'auto', 'backgroundColor': 'rgba(0,0,0,0.9)', 'border': '2px solid gold', 'padding': '20px'}
        modal_title = f"Resonance for '{highlight_word}'"
        modal_content = []

        # Shared Resonances (filtered by report layers)
        modal_content.append(html.H4("Resonances:", style={'color': 'gold', 'fontSize': f'{text_size + 2}px'}))
        shared_found = False
        for layer in report_layer_filter:
            resonant_words = GLOBAL_LAYERS.get(layer, {}).get(CALC_FUNCS[layer](highlight_word), [])
            other_words = [w for w in resonant_words if w != highlight_word]
            if other_words:
                modal_content.append(html.P(f"{layer}: {', '.join(other_words)}", style={'fontSize': f'{text_size + 2}px'}))
                shared_found = True
        if not shared_found:
            modal_content.append(html.P("No shared resonances", style={'fontSize': f'{text_size + 2}px'}))

        # Properties and Calculations (filtered by report layers)
        word_color = get_word_color(highlight_word)
        modal_content.extend([
            html.H4("Properties:", style={'color': 'gold', 'fontSize': f'{text_size + 2}px'}),
            html.P(f"Word/Phrase: {highlight_word}", style={'fontSize': f'{text_size + 2}px'}),
            html.P([
                "Color: ",
                html.Span("■", style={'color': word_color, 'fontSize': f'{text_size + 2}px'}),
                f" {word_color}"
            ], style={'fontSize': f'{text_size + 2}px'}),
            html.P(f"Origin: {', '.join(GLOBAL_WORD_ORIGINS.get(highlight_word, {'Unknown'}))}", style={'fontSize': f'{text_size + 2}px'}),
            html.P(f"Golden Resonance (~137.5): {'Yes 🌀' if any(is_golden_resonance(CALC_FUNCS[l](highlight_word)) for l in report_layer_filter) else 'No'}", style={'fontSize': f'{text_size + 2}px'}),
            html.H4("Calculations:", style={'color': 'gold', 'fontSize': f'{text_size + 2}px'}),
            *[html.P([f"{layer}: {CALC_FUNCS[layer](highlight_word)}", " 🌀" if is_golden_resonance(CALC_FUNCS[layer](highlight_word)) else ""], style={'fontSize': f'{text_size + 2}px'}) for layer in report_layer_filter],
            html.H4("Ambidextrous Balance:", style={'color': 'gold', 'fontSize': f'{text_size + 2}px'}),
            html.P(f"Left-Hand Qwerty: {-left_hand_qwerty(highlight_word)}", style={'fontSize': f'{text_size + 2}px'}),
            html.P(f"Right-Hand Qwerty: {right_hand_qwerty(highlight_word)}", style={'fontSize': f'{text_size + 2}px'}),
            html.P(f"Balance: {ambidextrous_balance(highlight_word)}", style={'fontSize': f'{text_size + 2}px'}),
            html.H4("Shared Resonances Across Layers:", style={'color': 'gold', 'fontSize': f'{text_size + 2}px'}),
            *[html.P(f"{layer}: {val}: {', '.join(group)}", style={'fontSize': f'{text_size + 2}px'}) for layer, val, group in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] in report_layer_filter and highlight_word in r[2]], key=lambda x: (x[0], x[1]))]
        ])

    # Matched words/phrases
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
    word_elems = [html.Div(w, style={'padding': '5px', 'cursor': 'pointer', 'backgroundColor': NAMED_COLORS_MAP.get(theme_colors['sidebar_bg'], '#111'), 'fontSize': f'{text_size}px'}, id={'type': 'word-item', 'index': w}) for w in sorted(matched)]

    # Shared resonances (excluding Love Resonance and Prime Gematria)
    resonance_elems = [
        html.Div(f"{layer}: {val}", style={'padding': '5px', 'cursor': 'pointer', 'backgroundColor': NAMED_COLORS_MAP.get(theme_colors['sidebar_bg'], '#111'), 'fontSize': f'{text_size}px'}, id={'type': 'resonance-item', 'index': f"{layer}:{val}"})
        for layer, val, _ in sorted([r for r in GLOBAL_SHARED_RESONANCES if r[0] not in ['Love Resonance', 'Prime Gematria']], key=lambda x: (x[0], x[1]))
    ]

    # Source filter options
    source_options = [{'label': s, 'value': s} for s in sorted(set().union(*GLOBAL_WORD_ORIGINS.values()))]

    # Styles
    main_style = {'backgroundColor': NAMED_COLORS_MAP.get(theme_colors['main_bg'], '#000000'), 'color': NAMED_COLORS_MAP.get(theme_colors['main_text'], '#FFFFFF'), 'height': '100vh', 'display': 'flex'}
    sidebar_style = {'width': '300px', 'padding': '20px', 'backgroundColor': NAMED_COLORS_MAP.get(theme_colors['sidebar_bg'], '#111'), 'overflowY': 'auto', 'fontSize': f'{text_size}px'}
    input_style = {'width': '100%', 'height': '80px', 'backgroundColor': NAMED_COLORS_MAP.get(theme_colors['input_bg'], '#333'), 'color': NAMED_COLORS_MAP.get(theme_colors['input_text'], '#FFFFFF'), 'border': theme_colors['input_border'], 'fontSize': f'{text_size}px'}
    search_input_style = {'width': '100%', 'backgroundColor': NAMED_COLORS_MAP.get(theme_colors['input_bg'], '#333'), 'color': NAMED_COLORS_MAP.get(theme_colors['input_text'], '#FFFFFF'), 'border': theme_colors['input_border'], 'fontSize': f'{text_size}px'}

    return (word_elems, build_graph_figure(selected_layers, highlight_word, theme, source_filter, number_filter, prime_filter, resonance_filter, word_phrase_filter, text_size), import_status, main_style, sidebar_style, input_style, search_input_style, upload_status, modal_style, modal_title, modal_content_style, modal_content, "", search_status, download_data, source_options, resonance_elems, download_report, full_report_style, full_report_content_style, full_report_content)

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)