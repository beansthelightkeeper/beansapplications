import dash
from dash import dcc, html, Input, Output, State
import math
import random
import pandas as pd

# --- Aave Wordlist and Gematria Data ---
AAVE_WORDS = [
    "lit", "fam", "dope", "vibe", "chill", "slay", "bet", "fire",
    "squad", "real", "salty", "extra", "flex", "hundo", "lowkey"
]
SIMPLE_GEMATRIA = {chr(65+i): i+1 for i in range(26)}  # A=1, B=2, ..., Z=26
GOLDEN_ANGLE = 137.5  # Spiralborn resonance
SENTENCE_TEMPLATES = [
    "{word1} is {word2}, yo!",
    "Keep it {word1}, fam, that’s the {word2} vibe.",
    "Yo, {word1} and {word2} got that {word3} energy!",
    "Stay {word1}, it’s all about that {word2} life."
]
FEEDBACK_SCORES = {}  # Store sentence feedback: {sentence: score}

# --- Gematria Functions ---
def simple_gematria(word):
    return sum(SIMPLE_GEMATRIA.get(c, 0) for c in word.upper() if c.isalpha())

def reduced_gematria(word):
    val = simple_gematria(word)
    while val > 9 and val not in [11, 22]:  # Keep master numbers
        val = sum(int(d) for d in str(val))
    return val

def spiral_gematria(word):
    total = 0
    for i, c in enumerate(word.upper(), 1):
        if c.isalpha():
            val = SIMPLE_GEMATRIA.get(c, 0)
            weight = math.cos(math.radians(GOLDEN_ANGLE * i))
            total += val * weight
    return round(abs(total) * 4, 2)  # Normalize to ~[0, 100]

def grok_resonance_score(word):
    simple = simple_gematria(word)
    reduced = reduced_gematria(word)
    spiral = spiral_gematria(word)
    # Boost for Aave slang
    boost = 1.1 if word.lower() in AAVE_WORDS else 1.0
    return round((simple + reduced + spiral) / 3 * boost, 2)

def generate_sentence():
    words = random.sample(AAVE_WORDS, 3)
    template = random.choice(SENTENCE_TEMPLATES)
    if "{word3}" in template:
        sentence = template.format(word1=words[0], word2=words[1], word3=words[2])
    else:
        sentence = template.format(word1=words[0], word2=words[1])
    return sentence

# --- Dash App ---
app = dash.Dash(__name__)
app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'fontFamily': 'Arial', 'padding': '20px'}, children=[
    html.H1("Aave Gematria Spiralborn Engine 🌀", style={'color': 'gold'}),
    html.Hr(),
    html.Label("Enter Aave Word/Phrase:"),
    dcc.Input(id='word-input', type='text', value='lit', style={'width': '100%', 'backgroundColor': '#333', 'color': 'white', 'border': '1px solid gold'}),
    html.Button('Calculate Gematria', id='calc-button', n_clicks=0),
    html.Div(id='gematria-result', style={'marginTop': '20px'}),
    html.Hr(),
    html.Label("Generated Sentence:"),
    html.Div(id='sentence-output', style={'marginTop': '10px', 'fontSize': '16px'}),
    html.Button('Generate Sentence', id='gen-sentence-button', n_clicks=0),
    html.Button('👍 Thumbs Up', id='thumbs-up-button', n_clicks=0, style={'margin': '10px'}),
    html.Button('👎 Thumbs Down', id='thumbs-down-button', n_clicks=0, style={'margin': '10px'}),
    html.Div(id='feedback-status', style={'marginTop': '10px'}),
    html.Hr(),
    html.Label("Gematria Table:"),
    dcc.Graph(id='gematria-table'),
])

# --- Callbacks ---
@app.callback(
    [
        Output('gematria-result', 'children'),
        Output('gematria-table', 'figure'),
        Output('sentence-output', 'children'),
        Output('feedback-status', 'children'),
    ],
    [
        Input('calc-button', 'n_clicks'),
        Input('gen-sentence-button', 'n_clicks'),
        Input('thumbs-up-button', 'n_clicks'),
        Input('thumbs-down-button', 'n_clicks'),
    ],
    [
        State('word-input', 'value'),
        State('sentence-output', 'children'),
    ]
)
def update_app(calc_clicks, gen_clicks, thumbs_up, thumbs_down, word, current_sentence):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ''
    
    # Initialize outputs
    gematria_result = ""
    table_fig = {}
    sentence = current_sentence or generate_sentence()
    feedback_status = ""

    # Calculate Gematria
    if triggered == 'calc-button' and word:
        word = word.strip().title()
        if re.match(r'^[A-Za-z\s]+$', word):
            simple = simple_gematria(word)
            reduced = reduced_gematria(word)
            spiral = spiral_gematria(word)
            grok_score = grok_resonance_score(word)
            matches = [w for w in AAVE_WORDS if abs(grok_resonance_score(w) - grok_score) < 5 and w.lower() != word.lower()]
            gematria_result = [
                html.P(f"Word: {word}"),
                html.P(f"Simple Gematria: {simple}"),
                html.P(f"Reduced Gematria: {reduced}"),
                html.P(f"Spiral Gematria: {spiral}"),
                html.P(f"Grok Resonance Score: {grok_score}"),
                html.P(f"Matches: {', '.join(matches) if matches else 'None'}")
            ]
            # Create table
            data = {
                'Word': [word] + matches,
                'Simple': [simple_gematria(w) for w in [word] + matches],
                'Reduced': [reduced_gematria(w) for w in [word] + matches],
                'Spiral': [spiral_gematria(w) for w in [word] + matches],
                'Grok Score': [grok_resonance_score(w) for w in [word] + matches]
            }
            df = pd.DataFrame(data)
            table_fig = {
                'data': [{
                    'type': 'table',
                    'header': {'values': list(df.columns), 'fill_color': 'gold', 'font_color': 'black'},
                    'cells': {'values': [df[col] for col in df.columns], 'fill_color': 'black', 'font_color': 'white'}
                }],
                'layout': {'title': 'Gematria Resonances', 'paper_bgcolor': 'black', 'font_color': 'white'}
            }
    
    # Generate Sentence
    if triggered == 'gen-sentence-button':
        sentence = generate_sentence()
    
    # Handle Feedback
    if triggered in ['thumbs-up-button', 'thumbs-down-button'] and current_sentence:
        score = 1 if triggered == 'thumbs-up-button' else -1
        FEEDBACK_SCORES[current_sentence] = FEEDBACK_SCORES.get(current_sentence, 0) + score
        feedback_status = f"Feedback recorded: {'👍' if score > 0 else '👎'} (Score: {FEEDBACK_SCORES[current_sentence]})"
        # Adjust word weights based on feedback
        words = [w.lower() for w in current_sentence.split() if w.lower() in AAVE_WORDS]
        for w in words:
            AAVE_WORDS.append(w) if score > 0 else AAVE_WORDS.remove(w) if w in AAVE_WORDS and score < 0 else None
    
    return gematria_result, table_fig, sentence, feedback_status

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True, port=8051)