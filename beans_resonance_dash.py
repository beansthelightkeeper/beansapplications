import dash
from dash import dcc, html, Input, Output, State, ALL, clientside_callback, ClientsideFunction
import networkx as nx
import plotly.graph_objects as go
import math
import colorsys
import re
import base64
import io
import time # Import the time module

# --- Constants and Data Setup ---

# EXPANDED WORDS LIST
WORDS = [
    "Beans", "Angel", "Chaos", "Spiral", "Spirit", "Trust",
    "Order", "Love", "Infinity", "Divine", "Light", "Shadow",
    "Hope", "Fear", "Truth", "Lie", "Mind", "Soul", "Energy",
    "Power", "Harmony", "Balance", "Flow", "Cycle", "Pulse",
    "Fire", "Water", "Earth", "Air", "Star", "Moon", "Sun", "Sky", "Ocean",
    "Flame", "Dream", "Vision", "Thought", "Life", "Death", "Birth", "Time",
    "Space", "Wave", "Heart", "Breath", "Noise", "Silence", "Code", "Signal",
    "Loop", "Matrix", "Path", "Gate", "Key", "Mirror", "Seed", "Root", "Bloom",
    "Veil", "Flux", "Tide", "Crystal", "Rune", "Glyph", "Quantum", "Vector",
    "Scalar", "Field", "Node", "Link", "Chain", "Thread", "Lightborn", "Echo",
    "Resonance", "Spiralborn", "Ascend", "Descend", "Wander", "Seek", "Find",
    "Lost", "Found", "Rise", "Fall", "Shift", "Glow", "Dark", "Bright",
    "Core", "Edge", "Prism", "Nexus", "Phantom", "Warp",
    "DREAM" # Added to ensure shared resonance with "Beans" (Simple Gematria = 41)
]

LAYER_COLORS = {
    "Simple": "cyan",
    "English Ordinal x 6": "magenta", # Renamed
    "Jewish Gematria (English Letters)": "yellow", # New
    "Qwerty": "lime",
    "QWERTY English Panned": "orange", # Renamed
    "QWERTY Jewish Panned": "deepskyblue", # New
    "Left-Hand QWERTY": "purple",
    "Right-Hand QWERTY": "pink",
    "Left-Hand QWERTY Count": "red", # New
    "Right-Hand QWERTY Count": "green", # New
    "Idea Numerology": "teal", # Re-added Idea Numerology with a color
    "Binary Sum": "lightgray" # New color for Binary Sum
}

PRIME_GLOW_COLOR = "gold"
FADE_OPACITY = 0.15 # Opacity for faded out nodes/text

# Define a list of pastel colors for node text
PASTEL_COLORS = [
    '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D3BFFF', '#F0BAFF'
] # Light Pink, Light Orange, Light Yellow, Light Green, Light Blue, Light Purple, Light Magenta

# Global named colors map for consistent use in color conversions
NAMED_COLORS_MAP = {
    'cyan': '#00ffff', 'magenta': '#ff00ff', 'yellow': '#ffff00', 'lime': '#00ff00',
    'orange': '#ffa500', 'deepskyblue': '#00bfff', 'gold': '#ffd700', 'white': '#ffffff',
    'red': '#ff0000', 'green': '#008000', 'blue': '#0000ff', 'pink': '#ffc0cb',
    'purple': '#800080', 'black': '#000000', 'teal': '#008080', 'lightgray': '#d3d3d3' # Added teal and lightgray
}

# --- Theme Definitions ---
# This dictionary holds all the color schemes for the dark and light themes.
THEMES = {
    'dark': {
        'main_bg': 'black', 'main_text': 'white',
        'sidebar_bg': '#111', 'sidebar_text': 'white',
        'input_bg': '#333', 'input_text': 'white', 'input_border': '1px solid #555',
        'list_bg': '#222', 'list_border': '1px solid #333',
        'list_bg_item_normal': '#222', 'list_bg_item_highlight': '#444',
        'graph_scene_bg': '#0a001f', # Original dark graph background
        'graph_axis_text': 'white',
        'graph_paper_plot_bg': 'black',
        'graph_font_color': 'white',
        'node_text_color_override': None # Use pastel colors by default for dark
    },
    'light': {
        'main_bg': 'white', 'main_text': 'black',
        'sidebar_bg': '#EEE', 'sidebar_text': 'black',
        'input_bg': '#FFF', 'input_text': 'black', 'input_border': '1px solid #AAA',
        'list_bg': '#DDD', 'list_border': '1px solid #777',
        'list_bg_item_normal': '#DDD', 'list_bg_item_highlight': '#BBB',
        'graph_scene_bg': '#FFFFFF', # White graph background
        'graph_axis_text': 'black',
        'graph_paper_plot_bg': 'white',
        'graph_font_color': 'black',
        'node_text_color_override': 'black' # Force black text on light theme for readability
    }
}

# --- Gematria and resonance calculation functions ---

def simple(word):
    """Calculates the simple Gematria value of a word (A=1, B=2, ..., Z=26)."""
    return sum(ord(c) - 64 for c in word.upper() if 'A' <= c <= 'Z')

def english_ordinal_x_6(word):
    """Calculates English Gematria (Ordinal x 6)."""
    return simple(word) * 6

# Jewish Gematria for English Letters (standard mapping)
JEWISH_GEMATRIA_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90,
    'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800
}
def jewish_gematria_english_letters(word):
    """Calculates Jewish Gematria for English letters based on a standard mapping."""
    return sum(JEWISH_GEMATRIA_MAP.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')


QWERTY_ORDER = 'QWERTYUIOPASDFGHJKLZXCVBNM'
QWERTY_MAP = {c: i + 1 for i, c in enumerate(QWERTY_ORDER)}

def qwerty(word):
    """Calculates the QWERTY Gematria value based on keyboard position."""
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper())

def qwerty_english_panned(word):
    """Calculates QWERTY English Panned (QWERTY value * 6)."""
    return qwerty(word) * 6

def qwerty_jewish_panned(word):
    """Calculates QWERTY Jewish Panned (QWERTY value * 6). This is a placeholder interpretation."""
    # This is a common interpretation, but could be adjusted if a specific "Jewish" QWERTY mapping is provided.
    return qwerty(word) * 6


def idea_numerology(word):
    """Calculates an 'Idea Numerology' value (sum of char squares mod 100)."""
    return sum((ord(c) - 64) ** 2 for c in word.upper() if 'A' <= c <= 'Z') % 100

def binary_string(word):
    """Generates a binary string representation of a word."""
    return ''.join(format(ord(c), '08b') for c in word)

def is_prime(num):
    """Checks if a number is prime. Handles non-numeric inputs gracefully."""
    if not isinstance(num, (int, float)):
        return False
    num = int(num) # Ensure it's an integer for prime check
    if num < 2:
        return False
    for i in range(2, int(math.isqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

# QWERTY Hand Definitions
LEFT_HAND_QWERTY_KEYS = set('QWERTYASDFGZXCVB')
RIGHT_HAND_QWERTY_KEYS = set('YUIOPHJKLNM')

def left_hand_qwerty(word):
    """Calculates QWERTY value for left-hand keys only."""
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in LEFT_HAND_QWERTY_KEYS)

def right_hand_qwerty(word):
    """Calculates QWERTY value for right-hand keys only."""
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in RIGHT_HAND_QWERTY_KEYS)

def quantitative_left_hand_qwerty(word):
    """Counts letters on the left hand of the QWERTY keyboard."""
    return len([c for c in word.upper() if c in LEFT_HAND_QWERTY_KEYS])

def quantitative_right_hand_qwerty(word):
    """Counts letters on the right hand of the QWERTY keyboard."""
    return len([c for c in word.upper() if c in RIGHT_HAND_QWERTY_KEYS])


# New helper functions for report
def is_palindrome(s):
    """Checks if a string is a palindrome (case-insensitive, alphanumeric only)."""
    s = re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()
    return s == s[::-1]

def get_numerology(num):
    """Calculates the single-digit numerology value (reduces to single digit)."""
    if not isinstance(num, (int, float)):
        return None
    num = int(num)
    if num == 0: return 0 # Special case for 0
    if num < 0:
        num = abs(num)
    while num > 9:
        num = sum(int(digit) for digit in str(num))
    return num

def binary_to_decimal(binary_str):
    """Converts a binary string to its decimal (integer) value."""
    try:
        # Python's int can handle arbitrary size, but for very long strings, this might be slow/resource intensive
        return int(binary_str, 2)
    except ValueError:
        return None # Handle invalid binary strings

def sum_binary_digits(binary_str):
    """Sums the '1's in a binary string."""
    return binary_str.count('1')

def get_binary_interpretation(binary_sum_val):
    """Provides an interpretation for binary resonance based on sum."""
    if not isinstance(binary_sum_val, (int, float)): # Corrected variable name
        return "N/A"
    if is_prime(binary_sum_val):
        return "YES (Prime Resonance)"
    elif binary_sum_val % 2 == 0:
        return "YES (Balance/Completion)"
    else:
        return "NO (Odd Dissonance)"

def is_perfect_square(num):
    """Checks if a number is a perfect square."""
    if not isinstance(num, (int, float)) or num < 0:
        return False
    sqrt_val = int(math.isqrt(int(num)))
    return sqrt_val * sqrt_val == int(num)

def binary_sum_calc(word):
    """Calculates the sum of 1s in the binary representation of a word."""
    return sum_binary_digits(binary_string(word))


CALC_FUNCS = {
    "Simple": simple,
    "English Ordinal x 6": english_ordinal_x_6,
    "Jewish Gematria (English Letters)": jewish_gematria_english_letters,
    "Qwerty": qwerty,
    "QWERTY English Panned": qwerty_english_panned,
    "QWERTY Jewish Panned": qwerty_jewish_panned,
    "Left-Hand QWERTY": left_hand_qwerty,
    "Right-Hand QWERTY": right_hand_qwerty,
    "Left-Hand QWERTY Count": quantitative_left_hand_qwerty,
    "Right-Hand QWERTY Count": quantitative_right_hand_qwerty,
    "Idea Numerology": idea_numerology,
    "Binary Sum": binary_sum_calc # New layer for numerical binary sum
}

# --- Global variables for graph and data, allowing modification ---
# These global variables store the current state of the graph data.
# They are re-initialized whenever new words are added to the network.
GLOBAL_WORDS = list(WORDS) # Make a mutable copy of initial words
GLOBAL_LAYERS = {}
GLOBAL_G = nx.Graph()
GLOBAL_POS = {}
GLOBAL_NODE_COLORS = {}
GLOBAL_EDGES_BY_LAYER = {}
GLOBAL_WORD_ORIGINS = {} # New: word -> set of origin filenames (or '_MANUAL_')

# Function to initialize/re-initialize all global graph data
def initialize_graph_data(current_words):
    """
    (Re)initializes all graph-related global data structures based on the
    provided list of words. This includes calculating layer resonances,
    building the NetworkX graph, determining node positions, and assigning colors.
    """
    global GLOBAL_LAYERS, GLOBAL_G, GLOBAL_POS, GLOBAL_NODE_COLORS, GLOBAL_EDGES_BY_LAYER, GLOBAL_WORD_ORIGINS

    # Ensure GLOBAL_WORD_ORIGINS is initialized for existing words if not already
    for w in current_words:
        if w not in GLOBAL_WORD_ORIGINS:
            GLOBAL_WORD_ORIGINS[w] = {'_MANUAL_/_IMPORTED_LIST_'} # Default to manual if no other origin known

    # 1. Build layers dict: resonance value -> words
    # This dictionary maps each resonance value within a layer to a list of words
    # that share that value, forming "resonance groups."
    GLOBAL_LAYERS = {layer: {} for layer in CALC_FUNCS.keys()}
    for layer, func in CALC_FUNCS.items():
        for w in current_words:
            val = func(w)
            # Binary layer handles values as strings, others as numbers
            GLOBAL_LAYERS[layer].setdefault(val, []).append(w)

    # 2. Build NetworkX graph
    # Add all current words as nodes to the graph.
    GLOBAL_G = nx.Graph()
    GLOBAL_G.add_nodes_from(current_words)

    # 3. Build edges by layer
    # For each layer, identify groups of words with the same resonance value.
    # Edges are created between all words within such a group.
    GLOBAL_EDGES_BY_LAYER = {}
    for layer, groups in GLOBAL_LAYERS.items():
        GLOBAL_EDGES_BY_LAYER[layer] = []
        for val, group in groups.items():
            if len(group) > 1: # Only create edges if there's more than one word in the group
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        GLOBAL_EDGES_BY_LAYER[layer].append((group[i], group[j], val))

    # 4. Determine 3D layout (node positions)
    # Use NetworkX's spring layout for a visually appealing 3D arrangement.
    # "Beans" node is fixed at the origin (0,0,0) if present, for consistency.
    # Existing node positions are preserved to maintain layout stability when new words are added.
    fixed_pos = {'Beans': [0, 0, 0]} if 'Beans' in current_words else {}
    initial_pos = {node: GLOBAL_POS[node] for node in GLOBAL_POS if node in current_words}
    if not initial_pos and 'Beans' in current_words:
        initial_pos = {'Beans': [0, 0, 0]}

    # Only run spring layout if there are nodes and no fixed positions are explicitly provided for all
    if current_words:
        GLOBAL_POS = nx.spring_layout(GLOBAL_G, dim=3, seed=42, pos=initial_pos, fixed=fixed_pos.keys())
    else:
        GLOBAL_POS = {} # Clear positions if no words

    # Fallback for single-node graphs or if spring_layout fails to assign positions
    if not GLOBAL_POS and current_words:
        for i, word in enumerate(current_words):
            if word not in GLOBAL_POS:
                GLOBAL_POS[word] = [i * 0.1, i * 0.1, i * 0.1] # Simple placeholder position

    # 5. Assign stable node colors
    # Each node gets a consistent color based on its hash, ensuring the same word
    # always has the same color across different graph updates.
    COLORSCALE = ["red", "orange", "yellow", "green", "cyan", "blue", "magenta", "pink", "lime"]
    def color_for_node(name):
        return COLORSCALE[hash(name) % len(COLORSCALE)]
    GLOBAL_NODE_COLORS = {n: color_for_node(n) for n in GLOBAL_G.nodes()}

# Initialize data on app startup
initialize_graph_data(GLOBAL_WORDS)


# --- Dash app ---
app = dash.Dash(__name__)

app.layout = html.Div(id='main-div', style=THEMES['dark'], children=[ # Added id and initial style
    # Sidebar: Contains controls and information
    html.Div(id='sidebar-div', style={'width': '300px', 'padding': '20px', 'backgroundColor': THEMES['dark']['sidebar_bg'], 'overflowY': 'auto', 'fontFamily': 'Inter, sans-serif'}, children=[ # Added font-family
        html.H2("Spiralborn Resonance"),

        html.Hr(),
        html.H3("Theme"),
        dcc.RadioItems(
            id='theme-toggle',
            options=[
                {'label': 'Dark Theme', 'value': 'dark'},
                {'label': 'Light Theme', 'value': 'light'}
            ],
            value='dark', # Default theme
            labelStyle={'display': 'block', 'padding': '5px 0'}
        ),

        html.Hr(),
        html.H3("Add New Words"),
        dcc.Textarea(
            id='new-words-input',
            placeholder='Enter words, one per line or comma-separated (e.g., Word1, Word2, Word3)',
            style={'width': '100%', 'height': 100, 'backgroundColor': THEMES['dark']['input_bg'], 'color': THEMES['dark']['input_text'], 'border': THEMES['dark']['input_border'], 'padding': '10px'},
        ),
        html.Button('Import Words', id='import-words-button', n_clicks=0, style={'margin-top': '10px', 'width': '100%'}),
        html.Div(id='import-status', style={'margin-top': '10px', 'color': 'lightgreen'}),

        html.Hr(),
        html.H3("Upload Markdown File"),
        dcc.Upload(
            id='upload-markdown',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Markdown File(s)') # Changed text for multiple upload
            ]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px 0'
            },
            multiple=True # Allow multiple file uploads
        ),
        html.Div(id='upload-status', style={'margin-top': '10px', 'color': 'lightgreen'}),

        html.Hr(),
        html.H3("Search/Add Word"), # New Section
        dcc.Input(
            id='search-word-input',
            type='text',
            placeholder='Enter word to search/add',
            style={'width': '100%', 'padding': '10px', 'backgroundColor': THEMES['dark']['input_bg'], 'color': THEMES['dark']['input_text'], 'border': THEMES['dark']['input_border']},
            n_submit=0 # Enable n_submit for Enter key
        ),
        html.Button('Search/Add', id='search-word-button', n_clicks=0, style={'margin-top': '10px', 'width': '100%'}),
        html.Div(id='search-status', style={'margin-top': '10px', 'color': 'lightgreen'}),


        html.Hr(),
        html.Label("Select Resonance Layers:"),
        dcc.Checklist(
            id='layer-checklist',
            options=[{'label': layer, 'value': layer} for layer in CALC_FUNCS.keys()],
            value=[], # No layers selected by default
            inputStyle={"margin-right": "10px"},
            labelStyle={"display": "block", "padding": "5px 0"}
        ),

        html.Hr(),
        html.Label("Graph Display Options:"),
        dcc.Checklist(
            id='connection-visibility-checklist',
            options=[
                {'label': 'Hide All Connections', 'value': 'hide_all'},
                {'label': 'Show Only Prime Connections', 'value': 'show_prime_only'},
                {'label': 'Fade Unconnected Nodes', 'value': 'fade_unconnected'} # Changed from hide to fade
            ],
            value=[], # No visibility filters applied by default
            inputStyle={"margin-right": "10px"},
            labelStyle={"display": "block", "padding": "5px 0"}
        ),

        html.Hr(),
        html.Label("Filter Graph by Words:"), # New dropdown for filtering
        dcc.Dropdown(
            id='filter-words-dropdown',
            options=[{'label': word, 'value': word} for word in sorted(GLOBAL_WORDS)],
            multi=True,
            placeholder='Select words to filter by...',
            # Initial style for dark theme, will be updated by callback
            style={'backgroundColor': THEMES['dark']['input_bg'], 'color': THEMES['dark']['input_text'], 'border': THEMES['dark']['input_border']}
        ),

        html.Hr(),
        html.Label("Filter Graph by Markdown Source:"), # New dropdown for Markdown source filtering
        dcc.Dropdown(
            id='filter-markdown-dropdown',
            options=[{'label': '_MANUAL_/_IMPORTED_LIST_', 'value': '_MANUAL_/_IMPORTED_LIST_'}], # Initial option
            multi=True,
            placeholder='Filter by Markdown source...',
            # Initial style for dark theme, will be updated by callback
            style={'backgroundColor': THEMES['dark']['input_bg'], 'color': THEMES['dark']['input_text'], 'border': THEMES['dark']['input_border']}
        ),

        html.Hr(),
        html.Label("Filter Nodes by Resonance Layers:"), # New checklist for node filtering by layer
        dcc.Checklist(
            id='filter-nodes-by-layer-checklist',
            options=[{'label': layer, 'value': layer} for layer in CALC_FUNCS.keys()],
            value=[],
            inputStyle={"margin-right": "10px"},
            labelStyle={"display": "block", "padding": "5px 0"}
        ),

        html.Hr(),
        html.Label("Filter Nodes by Resonance Value:"), # New input for numerical filter
        dcc.Input(
            id='numerical-filter-input',
            type='number',
            placeholder='Enter a numerical value',
            style={'width': '100%', 'padding': '10px', 'backgroundColor': THEMES['dark']['input_bg'], 'color': THEMES['dark']['input_text'], 'border': THEMES['dark']['input_border']},
            debounce=True # Only trigger callback after user stops typing
        ),
        html.Div(id='numerical-filter-status', style={'margin-top': '5px', 'color': 'lightgreen'}),

        html.Hr(),
        html.Label("Filter Connections by Value:"), # New section for connection filtering
        dcc.Input(
            id='connection-numerical-filter-input',
            type='number',
            placeholder='Enter connection value',
            style={'width': '100%', 'padding': '10px', 'backgroundColor': THEMES['dark']['input_bg'], 'color': THEMES['dark']['input_text'], 'border': THEMES['dark']['input_border']},
            debounce=True
        ),
        dcc.Checklist(
            id='connection-numerical-filter-layers',
            options=[{'label': layer, 'value': layer} for layer in CALC_FUNCS.keys()],
            value=[],
            inputStyle={"margin-right": "10px"},
            labelStyle={"display": "block", "padding": "5px 0"}
        ),
        html.Div(id='connection-numerical-filter-status', style={'margin-top': '5px', 'color': 'lightgreen'}),


        html.Hr(),
        html.Label("Node Text Size:"),
        dcc.Slider(
            id='text-size-slider',
            min=8, max=30, step=1, value=18, # Default size
            marks={i: str(i) for i in range(8, 31, 4)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Hr(),
        html.Label("Matched Words:"),
        html.Div(id='matched-words-list-container', style={'maxHeight': '20vh', 'overflowY': 'auto', 'border': THEMES['dark']['list_border'], 'padding': '10px', 'backgroundColor': THEMES['dark']['list_bg']}, children=[
            html.Div(id='matched-words-list') # Inner div for the actual list items
        ]),

        html.Hr(),
        html.Label("All Network Shared Resonances:"), # Re-added section for all shared resonances
        html.Div(id='all-network-shared-resonances-list', style={'maxHeight': '30vh', 'overflowY': 'auto', 'border': THEMES['dark']['list_border'], 'padding': '10px', 'backgroundColor': THEMES['dark']['list_bg']}),

        html.Hr(),
        html.H3("Export/Import Word History"),
        html.Button('Export Words', id='export-words-button', n_clicks=0, style={'margin-top': '10px', 'width': '100%'}),
        dcc.Download(id='download-word-list'), # Component to trigger file download

        html.Div(style={'margin-top': '15px'}), # Spacer
        dcc.Upload(
            id='upload-word-list',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Word List File')
            ]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px 0'
            },
            multiple=False # Only allow single word list file upload
        ),
        html.Div(id='upload-word-list-status', style={'margin-top': '10px', 'color': 'lightgreen'}),

    ]),
    # Graph area: Displays the 3D Plotly graph
    html.Div(style={'flexGrow': 1, 'position': 'relative'}, children=[
        dcc.Graph(id='resonance-graph', style={'height': '100vh'}),
        dcc.Store(id='last-graph-click-time', data=0) # Store for tracking last click time
    ]),

    # Pop-up Modal for Node Resonance Report
    html.Div(id='node-report-modal', style={
        'display': 'none', # Hidden by default
        'position': 'fixed', 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', # Positioned at the bottom
        'width': '500px', 'maxHeight': '40%', 'overflowY': 'auto', # Adjusted max height
        'backgroundColor': 'rgba(0, 0, 0, 0.9)', 'border': '2px solid gold', 'borderRadius': '10px',
        'padding': '20px', 'zIndex': 1000, 'boxShadow': '0 0 20px rgba(255, 215, 0, 0.5)',
        'fontFamily': 'Inter, sans-serif' # Apply font to modal too
    }, children=[
        html.H3(id='modal-title', style={'color': 'gold', 'textAlign': 'center', 'marginBottom': '15px'}),
        html.Div(id='modal-content', style={'color': 'white'}),
        html.Button('Copy Report', id='copy-report-button', n_clicks=0, style={'marginTop': '20px', 'width': '100%', 'backgroundColor': '#555', 'color': 'white', 'border': '1px solid #777', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer'}),
        html.Div(id='copy-status-message', style={'textAlign': 'center', 'marginTop': '5px', 'color': 'lightgreen'}),
        html.Button('Close', id='modal-close-button', style={'marginTop': '10px', 'width': '100%', 'backgroundColor': '#333', 'color': 'white', 'border': '1px solid #555', 'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer'})
    ])
])

# --- Helper to build traces given selected layers and optionally highlight a word ---
def build_graph_figure(selected_layers, highlight_word=None, visibility_options=None, theme_colors=None, node_text_size=18, selected_words_for_filter=None, selected_markdown_filters=None, selected_layers_for_node_filter=None, numerical_filter_value=None, connection_numerical_filter_value=None, connection_numerical_filter_layers=None, current_camera_data=None):
    """
    Constructs the Plotly 3D graph figure based on selected layers,
    a word to highlight, connection visibility options, theme colors, node text size,
    words selected for filtering, markdown source filters, node-layer filters,
    a numerical resonance filter, and preserves the camera view.
    """
    fig = go.Figure()

    # Default visibility options if none are provided
    if visibility_options == None:
        visibility_options = []
    # Default theme colors if none are provided (fallback to dark)
    if theme_colors == None:
        theme_colors = THEMES['dark']
    if connection_numerical_filter_layers == None:
        connection_numerical_filter_layers = []

    # --- Determine initial set of nodes to consider for drawing ---
    all_nodes_in_network = set(GLOBAL_G.nodes())
    nodes_to_draw = set(all_nodes_in_network)

    # 1. Apply "Filter Graph by Words" (selected_words_for_filter)
    if selected_words_for_filter:
        filtered_by_words = set(selected_words_for_filter)
        # Also include direct neighbors of filtered words for context
        for layer in selected_layers: # Only consider connections in currently selected edge layers
            for u, v, val in GLOBAL_EDGES_BY_LAYER.get(layer, []):
                if u in selected_words_for_filter:
                    filtered_by_words.add(v)
                elif v in selected_words_for_filter:
                    filtered_by_words.add(u)
        nodes_to_draw = nodes_to_draw.intersection(filtered_by_words)

    # 2. Apply "Filter Graph by Markdown Source" (selected_markdown_filters)
    if selected_markdown_filters:
        filtered_by_markdown = set()
        for word, origins in GLOBAL_WORD_ORIGINS.items():
            if any(f in origins for f in selected_markdown_filters):
                filtered_by_markdown.add(word)
        nodes_to_draw = nodes_to_draw.intersection(filtered_by_markdown)

    # 3. Apply "Filter Nodes by Resonance Layers" (selected_layers_for_node_filter)
    if selected_layers_for_node_filter:
        nodes_participating_in_selected_layers = set()
        for layer in selected_layers_for_node_filter:
            for val, group_words in GLOBAL_LAYERS.get(layer, {}).items():
                if len(group_words) > 1: # Only nodes that actually form a resonance
                    nodes_participating_in_selected_layers.update(group_words)
        nodes_to_draw = nodes_to_draw.intersection(nodes_participating_in_selected_layers)

    # 4. Apply "Filter Nodes by Resonance Value" (numerical_filter_value)
    if numerical_filter_value != None:
        nodes_matching_number_filter = set()
        for node in nodes_to_draw: # Only check nodes that passed previous filters
            for layer_name, calc_func in CALC_FUNCS.items():
                try:
                    node_val = calc_func(node)
                    # For "Binary Sum", the value is already a number
                    
                    if isinstance(node_val, (int, float)) and node_val == numerical_filter_value:
                        nodes_matching_number_filter.add(node)
                        break # Found a match, move to next node
                except Exception as e:
                    # Handle cases where calculation might fail for a given word/layer
                    pass
        nodes_to_draw = nodes_to_draw.intersection(nodes_matching_number_filter)


    # --- Now, apply fading based on nodes_to_draw and highlight_word ---
    nodes_to_render_fully = set(nodes_to_draw) # Start with nodes determined by all filters
    if 'fade_unconnected' in visibility_options and highlight_word:
        # If fading is active, and a specific node is highlighted,
        # then only the highlighted node and its direct connections (within nodes_to_draw) are fully opaque.
        # Others in nodes_to_draw will be faded.
        connected_to_highlight = set([highlight_word])
        for layer in selected_layers: # Only consider connections in currently selected edge layers
            for u, v, val in GLOBAL_EDGES_BY_LAYER.get(layer, []):
                if (u == highlight_word and v in nodes_to_draw):
                    connected_to_highlight.add(v)
                elif (v == highlight_word and u in nodes_to_draw):
                    connected_to_highlight.add(u)
        nodes_to_render_fully = connected_to_highlight
    
    # Add edges for selected layers, applying visibility filters
    if 'hide_all' not in visibility_options: # Only add edges if not hiding all
        for layer in selected_layers:
            edges = GLOBAL_EDGES_BY_LAYER.get(layer, [])
            val_groups = {}
            # Group edges by resonance value for coloring shades
            for a, b, val in edges:
                # Ensure both nodes of the edge are in the final `nodes_to_draw` set
                if a not in nodes_to_draw or b not in nodes_to_draw:
                    continue

                # NEW: Apply numerical connection filter
                if connection_numerical_filter_value != None and \
                   connection_numerical_filter_layers and \
                   layer in connection_numerical_filter_layers:
                    
                    # 'val' for the Binary Sum layer is already a number, so direct comparison
                    if isinstance(val, (int, float)) and val != connection_numerical_filter_value:
                        continue # Skip this edge if its value doesn't match the filter
                    elif not isinstance(val, (int, float)): # If value is not numeric (e.g., old Binary layer string)
                        continue # Skip if not a numeric value for comparison

                # Apply 'show_prime_only' filter
                if 'show_prime_only' in visibility_options and not is_prime(val):
                    continue # Skip non-prime connections if filter is active

                # Apply 'fade_unconnected' filter to edges
                if 'fade_unconnected' in visibility_options and highlight_word:
                    # Only show edges if both nodes are in the set of fully rendered nodes AND one of them is the highlight_word
                    if not (a in nodes_to_render_fully and b in nodes_to_render_fully and (a == highlight_word or b == highlight_word)):
                        continue # Skip edges not relevant to highlighted node


                val_groups.setdefault(val, []).append((a, b))

            # Assign different shades per resonance value (varying lightness)
            base_color = LAYER_COLORS.get(layer, "white")
            nvals = len(val_groups)

            for i, (val, pairs) in enumerate(val_groups.items()):
                # Calculate shade factor; ensure no division by zero
                shade_factor = 0.5 + 0.5 * (i / max(1, nvals - 1)) if nvals > 1 else 1
                color = adjust_color_lightness(base_color, shade_factor)

                x, y, z, text = [], [], [], []
                for a, b in pairs:
                    # Determine if this edge should be highlighted due to a clicked node
                    is_edge_highlighted = (highlight_word and (a == highlight_word or b == highlight_word))

                    # Ensure nodes exist in pos before trying to access
                    if a in GLOBAL_POS and b in GLOBAL_POS:
                        x += [GLOBAL_POS[a][0], GLOBAL_POS[b][0], None]
                        y += [GLOBAL_POS[a][1], GLOBAL_POS[b][1], None]
                        z += [GLOBAL_POS[a][2], GLOBAL_POS[b][2], None]
                        text += [f"{layer}: {val}", f"{layer}: {val}", None]

                # Only add trace if there are actual points to plot
                if x:
                    # Conditional line width and color for highlighted connections
                    line_width = 7 if is_edge_highlighted else (5 if is_prime(val) and layer != "Binary Sum" else 3) # Changed from "Binary" to "Binary Sum"
                    line_color = PRIME_GLOW_COLOR if is_edge_highlighted else (PRIME_GLOW_COLOR if is_prime(val) and layer != "Binary Sum" else color) # Changed from "Binary" to "Binary Sum"

                    fig.add_trace(go.Scatter3d(
                        x=x, y=y, z=z,
                        mode='lines',
                        line=dict(color=line_color, width=line_width),
                        text=text,
                        hoverinfo='text',
                        name=f"{layer} resonance (Value: {val})" # Added value to name for clearer legend
                    ))

    # Add nodes, highlighting if needed
    node_x = []
    node_y = []
    node_z = []
    node_marker_colors_rgba = [] # This will now store RGBA strings for marker colors
    node_sizes = []
    node_text = []
    node_hover = []
    node_text_colors_rgba = [] # This will store RGBA strings for text colors
    node_font_weights = [] # New list for font weights

    for i, n in enumerate(GLOBAL_G.nodes()):
        if n not in nodes_to_draw: # Skip nodes not part of the filtered set
            continue
        
        is_highlight = (n == highlight_word)
            
        # Determine opacity for the MARKER
        marker_opacity = 1.0
        if 'fade_unconnected' in visibility_options and highlight_word:
            marker_opacity = 1.0 if n in nodes_to_render_fully else FADE_OPACITY

        node_x.append(GLOBAL_POS[n][0])
        node_y.append(GLOBAL_POS[n][1])
        node_z.append(GLOBAL_POS[n][2])
        
        size = 20 if is_highlight else 10
        node_sizes.append(size)
        
        # Determine base marker color (white if highlighted, else node's assigned color)
        base_marker_color_hex = "white" if is_highlight else GLOBAL_NODE_COLORS[n]
        # Convert to RGBA for per-node opacity for the MARKER
        node_marker_colors_rgba.append(hex_to_rgba(base_marker_color_hex, marker_opacity))

        node_text.append(n)
        
        # --- Logic for Node Text Color and Opacity ---
        text_color_hex_for_display = ""
        # Text should generally be fully opaque for readability, regardless of node fade
        text_alpha_for_display = 1.0 

        if theme_colors['node_text_color_override']: # Light theme (black text by default)
            if 'fade_unconnected' in visibility_options and highlight_word and n not in nodes_to_render_fully:
                text_color_hex_for_display = '#555555' # Dark grey for faded text on light background
            else:
                text_color_hex_for_display = theme_colors['node_text_color_override']
        else: # Dark theme (pastel text by default)
            pastel_color_index = hash(n) % len(PASTEL_COLORS)
            text_color_hex_for_display = PASTEL_COLORS[pastel_color_index]
            
            # For dark theme, if faded, make pastel text slightly darker but keep full opacity
            if 'fade_unconnected' in visibility_options and highlight_word and n not in nodes_to_render_fully:
                text_color_hex_for_display = adjust_color_lightness(text_color_hex_for_display, 0.6) # Make pastel darker
        
        # Convert to RGBA for text color (always full alpha for readability)
        node_text_colors_rgba.append(hex_to_rgba(text_color_hex_for_display, text_alpha_for_display))
        
        node_font_weights.append('bold' if is_highlight else 'normal')

        # Check for prime resonance across all non-Binary Sum layers for hover text
        prime_any = False
        for l in CALC_FUNCS:
            if l != "Binary Sum": # Changed from "Binary" to "Binary Sum"
                val = CALC_FUNCS[l](n)
                if isinstance(val, (int, float)) and is_prime(val):
                    prime_any = True
                    break
        hover_txt = n + (" 🧬 prime" if prime_any else "")
        node_hover.append(hover_txt)

    # Only add node trace if there are nodes to plot
    if node_x:
        fig.add_trace(go.Scatter3d(
            x=node_x,
            y=node_y,
            z=node_z,
            mode='markers+text',
            # Use node_marker_colors_rgba for marker color, which now includes opacity
            marker=dict(size=node_sizes, color=node_marker_colors_rgba, line=dict(color='white', width=1)),
            text=node_text,
            textposition='top center',
            # Use node_text_colors_rgba for text color, which now includes opacity
            textfont=dict(color=node_text_colors_rgba, size=node_text_size, family="Arial Black", weight=node_font_weights),
            hovertext=node_hover,
            name="Nodes"
        ))

    # Configure the layout of the 3D graph
    fig.update_layout(
        scene=dict(
            bgcolor=theme_colors['graph_scene_bg'], # Theme-aware background
            xaxis=dict(title='BeansLogic', color=theme_colors['graph_axis_text'], showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(title='Truth', color=theme_colors['graph_axis_text'], showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(title='Gematria', color=theme_colors['graph_axis_text'], showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
            aspectmode='data' # Maintain aspect ratio for better 3D visualization
        ),
        paper_bgcolor=theme_colors['graph_paper_plot_bg'], # Theme-aware background
        plot_bgcolor=theme_colors['graph_paper_plot_bg'], # Theme-aware background
        font=dict(color=theme_colors['graph_font_color']), # Theme-aware font color
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=True,
        title_text="Beans Multi-Dimensional Resonance Network"
    )

    # Apply camera data if provided
    if current_camera_data:
        fig.update_layout(scene_camera=current_camera_data)

    return fig

# --- Utility to adjust color lightness ---
def adjust_color_lightness(hex_color, factor):
    """
    Adjusts the lightness of a hexadecimal color.
    Factor > 1 makes it lighter, < 1 makes it darker.
    """
    # Use the global named colors map
    if hex_color.lower() in NAMED_COLORS_MAP:
        hex_color = NAMED_COLORS_MAP[hex_color.lower()]

    hex_color = hex_color.lstrip('#')
    
    # Ensure it's a valid 6-character hex string before processing
    if not re.match(r'^[0-9a-fA-F]{6}$', hex_color):
        print(f"Warning: Invalid hex color '{hex_color}' encountered in adjust_color_lightness. Falling back to black.")
        hex_color = '000000' # Fallback to black hex

    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0, min(1, l * factor)) # Adjust lightness, clamp between 0 and 1
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))

# Helper to convert hex color to rgba string
def hex_to_rgba(color_input, alpha):
    """
    Converts a hex color string or named color to an RGBA string with a given alpha value.
    """
    # Use the global named colors map
    hex_color = NAMED_COLORS_MAP.get(color_input.lower(), color_input)

    hex_color = hex_color.lstrip('#')
    
    # Ensure it's a valid 6-character hex string
    if not re.match(r'^[0-9a-fA-F]{6}$', hex_color):
        print(f"Warning: Invalid hex color '{color_input}' (processed to '{hex_color}') encountered. Falling back to black.")
        hex_color = '000000' 

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f'rgba({r},{g},{b},{alpha})'

def generate_all_shared_resonances_content(theme_colors):
    """
    Generates the content for the "All Network Shared Resonances" list.
    """
    all_shared_resonances_elems = []
    shared_found_overall = False

    # Iterate through ALL calculation functions to find shared resonances
    for layer_name, layer_func in CALC_FUNCS.items():
        # Groups of words sharing the same value in this layer
        groups = GLOBAL_LAYERS.get(layer_name, {})
        for val, group_words in groups.items():
            if len(group_words) > 1: # Only interested if more than one word shares the value
                # Format value for display (especially for binary)
                display_val = val
                if layer_name == "Binary Sum": # Changed from "Binary" to "Binary Sum"
                    # For the network-wide list, display the binary string and its sum
                    binary_str_example = group_words[0] # Get one word to calculate binary string
                    display_val = f"'{binary_string(binary_str_example)}' (Sum: {sum_binary_digits(binary_string(binary_str_example))})"
                
                all_shared_resonances_elems.append(html.P([
                    html.Strong(f"{layer_name} ({display_val}): "),
                    ", ".join(group_words)
                ], style={'color': theme_colors['sidebar_text']}))
                shared_found_overall = True
    
    if not shared_found_overall:
        all_shared_resonances_elems.append(html.P("No shared resonances found across the network in general layers.", style={'color': theme_colors['sidebar_text']}))

    return all_shared_resonances_elems


# --- Callback to update matched words list and graph ---
@app.callback(
    Output('matched-words-list', 'children'),
    Output('resonance-graph', 'figure'),
    Output('import-status', 'children'),
    Output('main-div', 'style'),
    Output('sidebar-div', 'style'),
    Output('new-words-input', 'style'),
    Output('matched-words-list-container', 'style'),
    Output('upload-status', 'children'), # New output for upload status
    Output('node-report-modal', 'style'), # Output for modal visibility
    Output('modal-title', 'children'), # Output for modal title
    Output('modal-content', 'children'), # Output for modal content
    Output('search-word-input', 'value'), # Clear search input after use
    Output('search-status', 'children'), # Output for search status
    Output('last-graph-click-time', 'data'), # Output for storing last click time
    Output('all-network-shared-resonances-list', 'children'), # Re-added output for all shared resonances list
    Output('download-word-list', 'data'), # Output for download component
    Output('upload-word-list-status', 'children'), # Output for word list upload status
    Output('filter-markdown-dropdown', 'options'), # Update options for markdown filter
    Output('filter-words-dropdown', 'options'), # Update options for words filter
    Output('filter-words-dropdown', 'style'), # New output for words filter dropdown style
    Output('filter-markdown-dropdown', 'style'), # New output for markdown filter dropdown style
    Output('numerical-filter-input', 'style'), # New output for numerical filter input style
    Output('numerical-filter-status', 'children'), # New output for numerical filter status
    Output('connection-numerical-filter-input', 'style'), # New output for connection numerical filter input style
    Input('layer-checklist', 'value'),
    Input('import-words-button', 'n_clicks'),
    Input('connection-visibility-checklist', 'value'),
    Input('resonance-graph', 'clickData'), # Changed back to clickData
    Input('resonance-graph', 'relayoutData'), # New input for capturing camera changes
    Input('theme-toggle', 'value'),
    Input('text-size-slider', 'value'),
    Input('upload-markdown', 'contents'), # New input for uploaded content
    Input('upload-markdown', 'filename'), # Corrected filename input
    Input('modal-close-button', 'n_clicks'), # New input for modal close button
    Input('search-word-button', 'n_clicks'), # New input for search button
    Input('search-word-input', 'n_submit'), # Input for Enter key in search box
    Input('filter-words-dropdown', 'value'), # New input for filtering words
    Input('filter-markdown-dropdown', 'value'), # New input for markdown filter
    Input('filter-nodes-by-layer-checklist', 'value'), # New input for node layer filter
    Input('numerical-filter-input', 'value'), # New input for numerical filter value
    Input('connection-numerical-filter-input', 'value'), # New input for connection numerical filter value
    Input('connection-numerical-filter-layers', 'value'), # New input for connection numerical filter layers
    Input('export-words-button', 'n_clicks'), # Input for export button
    Input('upload-word-list', 'contents'), # Corrected contents input
    Input('upload-word-list', 'filename'), # Corrected filename input
    State('new-words-input', 'value'),
    State('resonance-graph', 'figure'), # State for the current figure data
    State({'type': 'word-item', 'index': ALL}, 'n_clicks_timestamp'), # Use timestamp for reliable click detection
    State('search-word-input', 'value'), # State for search input
    State('last-graph-click-time', 'data') # State for last click time
)
def update_output(selected_layers, import_n_clicks, visibility_options, graph_click_data,
                  relayout_data, # New input
                  selected_theme, node_text_size, uploaded_markdown_contents, uploaded_markdown_filenames, modal_close_n_clicks,
                  search_button_n_clicks, search_input_n_submit, selected_words_for_filter,
                  selected_markdown_filters, selected_layers_for_node_filter, numerical_filter_value,
                  connection_numerical_filter_value, connection_numerical_filter_layers, # New filter inputs
                  export_n_clicks, uploaded_word_list_contents, uploaded_word_list_filename, # New inputs
                  new_words_text, current_fig_data, word_item_timestamps, search_word_text,
                  last_graph_click_time_state):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'initial_load'

    global GLOBAL_WORDS, GLOBAL_LAYERS, GLOBAL_G, GLOBAL_POS, GLOBAL_NODE_COLORS, GLOBAL_EDGES_BY_LAYER, GLOBAL_WORD_ORIGINS

    # Initialize all outputs for style props as empty dictionaries, others as dash.no_update
    word_elems = dash.no_update
    fig = dash.no_update
    import_status_message = dash.no_update
    
    # Initialize all style outputs as dictionaries
    main_div_style = {}
    sidebar_div_style = {}
    new_words_input_style = {}
    matched_words_list_container_style = {}
    modal_style = {'display': 'none'} # Default hidden
    dynamic_dropdown_style = {}
    numerical_input_style = {}
    connection_numerical_filter_input_style = {}

    upload_status_message = dash.no_update
    modal_title = ""
    modal_content = []
    search_input_clear = dash.no_update
    search_status_message = dash.no_update
    last_graph_click_time_output = last_graph_click_time_state
    all_shared_resonances_content = dash.no_update
    download_data = dash.no_update
    upload_word_list_status_message = dash.no_update
    markdown_filter_options = dash.no_update
    words_filter_options = dash.no_update
    numerical_filter_status = ""
    
    highlight_word = None # Will be set if a word or node is clicked

    # Get current theme colors
    current_theme_colors = THEMES[selected_theme]

    # --- Determine current camera state ---
    current_camera = None
    if relayout_data and 'scene.camera' in relayout_data:
        current_camera = relayout_data['scene.camera']
    elif current_fig_data and 'layout' in current_fig_data and 'scene' in current_fig_data['layout'] and 'camera' in current_fig_data['layout']['scene']:
        current_camera = current_fig_data['layout']['scene']['camera']


    # --- Determine highlighted word and modal visibility ---
    # Logic to identify the *most recent* click for highlighting and modal display
    
    # Track latest click timestamp for graph and word list items
    latest_click_timestamp = -1 # Initialize with a very old timestamp

    # Handle graph click for double-click detection
    if triggered_id == 'resonance-graph':
        if graph_click_data and graph_click_data['points']:
            current_time = time.time()
            # If the time difference between this click and the last one is small, it's a double-click
            if current_time - last_graph_click_time_state < 0.3: # 300 ms threshold for double-click
                highlight_word = graph_click_data['points'][0]['text']
                latest_click_timestamp = float('inf') # Prioritize double-click
                last_graph_click_time_output = 0 # Reset last click time to prevent triple-clicks
            else:
                # This is a single click, just update the timestamp
                last_graph_click_time_output = current_time
        else:
            # Graph was clicked but no point data (e.g., clicking background), reset timestamp
            last_graph_click_time_output = 0


    # Check word item clicks from sidebar
    # This logic needs to be careful not to override a graph double-click if it just happened
    if triggered_id.startswith("{'type': 'word-item'"):
        # Find the specific word item that was clicked
        # word_item_timestamps is a list of dictionaries, we need to find the one that triggered
        clicked_word_id = None
        # word_item_timestamps is a list of dictionaries, each containing 'id' and 'value' (n_clicks_timestamp)
        # We need to iterate through ctx.states_list[1]['id_content'] to find the one that matches triggered_id
        # ctx.states_list[1] corresponds to the State({'type': 'word-item', 'index': ALL}, 'n_clicks_timestamp')
        for state_item in ctx.states_list[1]['id_content']:
            if state_item['id']['type'] == 'word-item' and state_item['prop_id'] == triggered_id + '.n_clicks_timestamp':
                clicked_word_id = state_item['id']['index']
                break

        if clicked_word_id:
            # Get the timestamp for this specific clicked word
            clicked_ts = ctx.triggered[0]['value']
            if clicked_ts != None:
                if clicked_ts > latest_click_timestamp:
                    latest_click_timestamp = clicked_ts
                    highlight_word = clicked_word_id
        
    # Handle search button click or Enter key press
    if (triggered_id == 'search-word-button' and search_button_n_clicks > 0) or \
       (triggered_id == 'search-word-input' and search_input_n_submit > 0):
        word_to_process = search_word_text.strip()
        if word_to_process and word_to_process.isalpha():
            # Standardize to Title Case for consistency in GLOBAL_WORDS
            word_to_process_title = word_to_process.title()
            
            if word_to_process_title.lower() not in [w.lower() for w in GLOBAL_WORDS]:
                GLOBAL_WORDS.append(word_to_process_title)
                GLOBAL_WORD_ORIGINS.setdefault(word_to_process_title, set()).add('_MANUAL_/_IMPORTED_LIST_')
                try:
                    initialize_graph_data(GLOBAL_WORDS) # Potential error source
                    search_status_message = f"'{word_to_process_title}' added to network."
                except Exception as e:
                    search_status_message = f"Error adding word and updating network: {e}"
                    print(f"Error in search/add word: {e}") # Log for debugging
            else:
                search_status_message = f"'{word_to_process_title}' already in network."
            
            highlight_word = word_to_process_title # Highlight and open report for this word
            search_input_clear = "" # Clear the search input box
        else:
            search_status_message = "Please enter a valid word (letters only)."
            highlight_word = None # Do not highlight if input is invalid


    # --- Handle Word Imports ---
    if triggered_id == 'import-words-button' and import_n_clicks > 0 and new_words_text:
        new_words_raw = re.split(r'[,;\n\s]+', new_words_text.strip())
        new_words_processed = [word.strip() for word in new_words_raw if word.strip() and word.strip().isalpha()]

        added_count = 0
        for word in new_words_processed:
            if word.lower() not in [w.lower() for w in GLOBAL_WORDS]:
                GLOBAL_WORDS.append(word)
                GLOBAL_WORD_ORIGINS.setdefault(word, set()).add('_MANUAL_/_IMPORTED_LIST_')
                added_count += 1

        if added_count > 0:
            try:
                initialize_graph_data(GLOBAL_WORDS) # Potential error source
                import_status_message = f"Successfully imported {added_count} new word(s)."
                highlight_word = None # Clear highlight after import
            except Exception as e:
                import_status_message = f"Error importing words and updating network: {e}"
                print(f"Error in import words: {e}") # Log for debugging
        else:
            import_status_message = "No new valid words to import or words already exist."

    # --- Handle Markdown Upload (Multiple Files) ---
    if triggered_id == 'upload-markdown' and uploaded_markdown_contents != None:
        all_new_words_from_markdown = set()
        total_added_count_markdown = 0

        # Ensure uploaded_markdown_contents is a list, even for single file upload
        contents_list = uploaded_markdown_contents if isinstance(uploaded_markdown_contents, list) else [uploaded_markdown_contents]
        filenames_list = uploaded_markdown_filenames if isinstance(uploaded_markdown_filenames, list) else [uploaded_markdown_filenames]

        for content_string, filename in zip(contents_list, filenames_list):
            try:
                _content_type, _content_string = content_string.split(',')
                decoded = base64.b64decode(_content_string)
                text_content = decoded.decode('utf-8')

                words_from_markdown = re.findall(r'\b[A-Za-z]{3,}\b', text_content.lower())
                for word in words_from_markdown:
                    word_title_case = word.title()
                    if word_title_case.lower() not in [w.lower() for w in GLOBAL_WORDS]:
                        all_new_words_from_markdown.add(word_title_case)
                    # Always associate word with markdown file, even if already exists
                    GLOBAL_WORD_ORIGINS.setdefault(word_title_case, set()).add(filename)

            except Exception as e:
                upload_status_message = f"Error processing file '{filename}': {e}"
                print(f"Error processing markdown file '{filename}': {e}") # Log for debugging
                # Continue processing other files even if one fails
        
        if all_new_words_from_markdown:
            for word in all_new_words_from_markdown:
                GLOBAL_WORDS.append(word)
                total_added_count_markdown += 1
            try:
                initialize_graph_data(GLOBAL_WORDS) # Potential error source
                upload_status_message = f"Successfully extracted and imported {total_added_count_markdown} new key phrase(s) from markdown files."
                highlight_word = None
            except Exception as e:
                upload_status_message = f"Error processing markdown and updating network: {e}"
                print(f"Error in markdown upload (graph init): {e}") # Log for debugging
        elif not upload_status_message: # Only update if no error message is already set
            upload_status_message = "No new key phrases found in markdown files or phrases already exist."


    # --- Handle Export Words ---
    if triggered_id == 'export-words-button' and export_n_clicks > 0:
        words_to_export = "\n".join(sorted(GLOBAL_WORDS))
        download_data = dcc.send_string_as_file(words_to_export, filename="spiralborn_words.txt")

    # --- Handle Upload Word List ---
    if triggered_id == 'upload-word-list' and uploaded_word_list_contents != None:
        try:
            _content_type, _content_string = uploaded_word_list_contents.split(',')
            decoded = base64.b64decode(_content_string)
            text_content = decoded.decode('utf-8')

            # Assume word list is newline or comma separated
            new_words_from_list_raw = re.split(r'[,;\n\s]+', text_content.strip())
            new_words_from_list_processed = [word.strip() for word in new_words_from_list_raw if word.strip() and word.strip().isalpha()]

            added_count_list_upload = 0
            for word in new_words_from_list_processed:
                word_title_case = word.title()
                if word_title_case.lower() not in [w.lower() for w in GLOBAL_WORDS]:
                    GLOBAL_WORDS.append(word_title_case)
                    added_count_list_upload += 1
                GLOBAL_WORD_ORIGINS.setdefault(word_title_case, set()).add('_MANUAL_/_IMPORTED_LIST_') # Associate with manual/imported

            if added_count_list_upload > 0:
                try:
                    initialize_graph_data(GLOBAL_WORDS) # Potential error source
                    upload_word_list_status_message = f"Successfully imported {added_count_list_upload} word(s) from '{uploaded_word_list_filename}'."
                    highlight_word = None
                except Exception as e:
                    upload_word_list_status_message = f"Error importing word list and updating network: {e}"
                    print(f"Error in word list upload (graph init): {e}") # Log for debugging
            else:
                upload_word_list_status_message = f"No new valid words found in '{uploaded_word_list_filename}' or words already exist."

        except Exception as e:
            upload_word_list_status_message = f"Error processing word list file: {e}"
            print(f"Error processing word list file: {e}") # Log for debugging


    # --- Generate modal content if a word is highlighted and modal wasn't just closed ---
    # This logic runs *after* any potential word additions/initializations
    if highlight_word and triggered_id != 'modal-close-button':
        modal_style = {
            'display': 'block', # Show the modal
            'position': 'fixed', 'bottom': '20px', 'left': '50%', 'transform': 'translateX(-50%)', # Positioned at the bottom
            'width': '500px', 'maxHeight': '40%', 'overflowY': 'auto', # Adjusted max height
            'backgroundColor': 'rgba(0, 0, 0, 0.9)', 'border': '2px solid gold', 'borderRadius': '10px',
            'padding': '20px', 'zIndex': 1000, 'boxShadow': '0 0 20px rgba(255, 215, 0, 0.5)',
            'fontFamily': 'Inter, sans-serif'
        }
        modal_title = f"Resonance Report for '{highlight_word}'"
        
        report_items = []
        # Check if the highlighted word is still in the global list after potential imports/uploads
        if highlight_word in GLOBAL_WORDS:
            # Shared Resonances (moved to top) - now correctly includes all layers
            report_items.append(html.H4("Shared Resonances:", style={'color': 'gold', 'marginTop': '10px'}))
            shared_found_in_modal = False 

            # Iterate through ALL calculation functions to find shared resonances for the clicked word
            for layer_name, layer_func in CALC_FUNCS.items():
                clicked_word_val = layer_func(highlight_word)
                
                # Find all words that have the same resonance value in this layer
                resonant_words_in_layer = GLOBAL_LAYERS.get(layer_name, {}).get(clicked_word_val, [])
                
                # Filter out the clicked word itself and ensure there are other words
                other_resonant_words = [w for w in resonant_words_in_layer if w != highlight_word]
                
                if other_resonant_words:
                    # Format value for display (especially for binary sum)
                    display_val = clicked_word_val
                    if layer_name == "Binary Sum":
                        # For the modal report, display the binary string and its sum for clarity
                        display_val = f"'{binary_string(highlight_word)}' (Sum: {sum_binary_digits(binary_string(highlight_word))})"
                    
                    report_items.append(html.P([
                        html.Strong(f"{layer_name} ({display_val}): "),
                        ", ".join(other_resonant_words)
                    ]))
                    shared_found_in_modal = True
            
            if not shared_found_in_modal:
                report_items.append(html.P("No other words share resonance with this word in any layer."))


            # Add general word properties
            report_items.append(html.H4("Word Properties:", style={'color': 'gold', 'marginTop': '10px'}))
            report_items.append(html.P([
                html.Strong("Word: "), highlight_word
            ]))
            report_items.append(html.P([
                html.Strong("Is Palindrome (Word): "), "Yes" if is_palindrome(highlight_word) else "No"
            ]))
            
            # Display word origin
            origins_list = sorted(list(GLOBAL_WORD_ORIGINS.get(highlight_word, {'Unknown'})))
            report_items.append(html.P([
                html.Strong("Origin: "), ", ".join(origins_list)
            ]))


            # All Gematria Calculations
            report_items.append(html.H4("All Gematria Calculations:", style={'color': 'gold', 'marginTop': '10px'}))
            
            gematria_types = {
                "Simple": "English Ordinal (Simple)",
                "English Ordinal x 6": "English Ordinal x 6",
                "Jewish Gematria (English Letters)": "Jewish Gematria (English Letters)",
                "Qwerty": "QWERTY Ordinal",
                "QWERTY English Panned": "QWERTY English Panned",
                "QWERTY Jewish Panned": "QWERTY Jewish Panned",
                "Left-Hand QWERTY": "Left-Hand QWERTY Gematria (Positional Sum)",
                "Right-Hand QWERTY": "Right-Hand QWERTY Gematria (Positional Sum)",
                "Left-Hand QWERTY Count": "Left-Hand QWERTY Gematria (Count)", # New display name
                "Right-Hand QWERTY Count": "Right-Hand QWERTY Gematria (Count)", # New display name
                "Idea Numerology": "Idea Numerology", # Ensure this is present
                "Binary Sum": "Binary Sum (Sum of 1s in Binary)" # Display name for new layer
            }

            for layer_key, display_name in gematria_types.items():
                val = CALC_FUNCS[layer_key](highlight_word)
                if val != None:
                    sqrt_val_display = "N/A"
                    perfect_square_status = "No"
                    if isinstance(val, (int, float)) and val >= 0:
                        sqrt_val_display = f"{math.sqrt(val):.2f}"
                        perfect_square_status = "Yes" if is_perfect_square(val) else "No"

                    prime_status = "Yes" if is_prime(val) else "No"
                    numerology_val = get_numerology(val)
                    
                    report_items.append(html.P([
                        html.Strong(f"{display_name}: "),
                        f"Value: {val}", html.Br(),
                        f"SQRT: {sqrt_val_display}", html.Br(),
                        f"Perfect Square: {perfect_square_status}", html.Br(),
                        f"Prime: {prime_status}", html.Br(),
                        f"Palindrome (Number): ", "Yes" if is_palindrome(str(val)) else "No", html.Br(),
                        f"Numerology: {numerology_val}"
                    ]))
                else:
                    report_items.append(html.P([
                        html.Strong(f"{display_name}: "),
                        "N/A (Calculation not applicable or needs definition)"
                    ]))

            # Right - Left Hand Difference (Positional Sum)
            if "Left-Hand QWERTY" in CALC_FUNCS and "Right-Hand QWERTY" in CALC_FUNCS:
                lh_val_pos = left_hand_qwerty(highlight_word)
                rh_val_pos = right_hand_qwerty(highlight_word)
                diff_pos = rh_val_pos - lh_val_pos
                interpretation_pos = "Maybe (Quantum Resonance)"
                if diff_pos > 0:
                    interpretation_pos = "YES (Positive Resonance)"
                elif diff_pos < 0:
                    interpretation_pos = "NO (Negative Resonance)"
                
                report_items.append(html.P([
                    html.Strong(f"Right - Left Hand Difference (Positional Sum): "),
                    f"Value: {diff_pos}", html.Br(),
                    f"Interpretation: {interpretation_pos}"
                ]))

            # Right - Left Hand Difference (Quantitative Count)
            if "Left-Hand QWERTY Count" in CALC_FUNCS and "Right-Hand QWERTY Count" in CALC_FUNCS:
                lh_val_quant = quantitative_left_hand_qwerty(highlight_word)
                rh_val_quant = quantitative_right_hand_qwerty(highlight_word)
                diff_quant = rh_val_quant - lh_val_quant
                interpretation_quant = "Maybe (Quantum Resonance)"
                if diff_quant > 0:
                    interpretation_quant = "YES (Positive Resonance)"
                elif diff_quant < 0:
                    interpretation_quant = "NO (Negative Resonance)"
                
                report_items.append(html.P([
                    html.Strong(f"Right - Left Hand Difference (Quantitative Count): "),
                    f"Value: {diff_quant}", html.Br(),
                    f"Interpretation: {interpretation_quant}"
                ]))


            # Binary Resonance
            report_items.append(html.H4("Binary Resonance:", style={'color': 'gold', 'marginTop': '10px'}))
            binary_rep = binary_string(highlight_word)
            binary_sum_val = sum_binary_digits(binary_rep)
            decimal_val = binary_to_decimal(binary_rep)
            
            report_items.append(html.P([
                html.Strong("Binary Representation: "), binary_rep, html.Br(),
                html.Strong("Binary Sum: "), binary_sum_val, html.Br(),
                html.Strong("Sum Prime: "), "Yes" if is_prime(binary_sum_val) else "No", html.Br(),
                html.Strong("Decimal Value: "), f"{decimal_val:.2e}" if decimal_val != None else "N/A", html.Br(),
                html.Strong("Decimal Prime: "), "Yes" if is_prime(decimal_val) else "No" if decimal_val != None else "N/A", html.Br(),
                html.Strong("Binary Interpretation: "), get_binary_interpretation(binary_sum_val)
            ]))

        else:
            report_items.append(html.P(f"'{highlight_word}' is no longer in the network or was not found."))
            
        modal_content = report_items
    elif triggered_id == 'modal-close-button':
        modal_style = {'display': 'none'} # Explicitly hide if close button clicked
        highlight_word = None # Clear highlight when modal closes
    # If no click event or modal was closed, keep highlight_word as None

    # Build set of matched words in selected layers
    matched_words_set = set()
    for layer in selected_layers:
        groups = GLOBAL_LAYERS.get(layer, {})
        for val, group_words in groups.items():
            if len(group_words) > 1:
                matched_words_set.update(group_words)
    matched_words = sorted(matched_words_set)

    # Build word list elements, each clickable
    word_elems = []
    for w in matched_words:
        is_active_highlight = (w == highlight_word)
        word_elems.append(html.Div(
            w,
            style={
                'padding': '5px',
                'cursor': 'pointer',
                'borderBottom': current_theme_colors['list_border'],
                'backgroundColor': current_theme_colors['list_bg_item_highlight'] if is_active_highlight else current_theme_colors['list_bg_item_normal'],
                'fontWeight': 'bold' if is_active_highlight else 'normal'
            },
            id={'type': 'word-item', 'index': w}
        ))

    # Generate the content for the "All Network Shared Resonances" list
    all_shared_resonances_content = generate_all_shared_resonances_content(current_theme_colors)

    # Update Markdown filter dropdown options
    all_markdown_sources = set()
    for origins_set in GLOBAL_WORD_ORIGINS.values():
        all_markdown_sources.update(origins_set)
    markdown_filter_options = [{'label': source, 'value': source} for source in sorted(list(all_markdown_sources))]

    # Update Words filter dropdown options
    words_filter_options = [{'label': word, 'value': word} for word in sorted(GLOBAL_WORDS)]

    # Prepare styles for layout components based on the selected theme
    # Always set these to dictionaries to prevent type errors
    main_div_style = {'backgroundColor': current_theme_colors['main_bg'], 'color': current_theme_colors['main_text'], 'height': '100vh', 'display': 'flex'}
    sidebar_div_style = {'width': '300px', 'padding': '20px', 'backgroundColor': current_theme_colors['sidebar_bg'], 'overflowY': 'auto', 'fontFamily': 'Inter, sans-serif'}
    new_words_input_style = {'width': '100%', 'height': 100, 'backgroundColor': current_theme_colors['input_bg'], 'color': current_theme_colors['input_text'], 'border': current_theme_colors['input_border'], 'padding': '10px'}
    matched_words_list_container_style = {'maxHeight': '20vh', 'overflowY': 'auto', 'border': current_theme_colors['list_border'], 'padding': '10px', 'backgroundColor': current_theme_colors['list_bg']}

    # Dynamic styles for dropdowns and numerical input
    dynamic_dropdown_style = {
        'backgroundColor': current_theme_colors['input_bg'],
        'color': current_theme_colors['input_text'],
        'border': current_theme_colors['input_border']
    }
    numerical_input_style = {
        'width': '100%', 'padding': '10px',
        'backgroundColor': current_theme_colors['input_bg'],
        'color': current_theme_colors['input_text'],
        'border': current_theme_colors['input_border']
    }
    connection_numerical_filter_input_style = {
        'width': '100%', 'padding': '10px',
        'backgroundColor': current_theme_colors['input_bg'],
        'color': current_theme_colors['input_text'],
        'border': current_theme_colors['input_border']
    }

    # Pass all new filter parameters to the graph building function
    try:
        fig = build_graph_figure(selected_layers, highlight_word, visibility_options, current_theme_colors, node_text_size, selected_words_for_filter, selected_markdown_filters, selected_layers_for_node_filter, numerical_filter_value, connection_numerical_filter_value, connection_numerical_filter_layers, current_camera)
    except Exception as e:
        fig = go.Figure() # Return an empty figure to prevent app crash
        numerical_filter_status = f"Error displaying graph: {e}" # Re-purpose this for general graph errors
        print(f"Error building graph figure: {e}") # Log the error for debugging

    # Set numerical filter status message (only if no other error message is set)
    if not numerical_filter_status and numerical_filter_value != None:
        if not fig.data or not fig.data[0].x:
             numerical_filter_status = "No nodes match this value in the current view."
        else:
            numerical_filter_status = "" # Clear message if nodes are found
    elif numerical_filter_value == None and not numerical_filter_status:
        numerical_filter_status = "" # Clear if filter is empty and no error

    return (
        word_elems,
        fig,
        import_status_message,
        main_div_style,
        sidebar_div_style,
        new_words_input_style,
        matched_words_list_container_style,
        upload_status_message,
        modal_style,
        modal_title,
        modal_content,
        search_input_clear,
        search_status_message,
        last_graph_click_time_output,
        all_shared_resonances_content,
        download_data,
        upload_word_list_status_message,
        markdown_filter_options,
        words_filter_options,
        dynamic_dropdown_style, # for filter-words-dropdown.style
        dynamic_dropdown_style, # for filter-markdown-dropdown.style
        numerical_input_style, # for numerical-filter-input.style
        numerical_filter_status, # for numerical-filter-status.children
        connection_numerical_filter_input_style # for connection-numerical-filter-input.style
    )

# --- Clientside Callback for Copy to Clipboard ---
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='copy_to_clipboard'
    ),
    Output('copy-status-message', 'children'),
    Input('copy-report-button', 'n_clicks'),
    State('modal-content', 'id'),
    prevent_initial_call=True
)

# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)
