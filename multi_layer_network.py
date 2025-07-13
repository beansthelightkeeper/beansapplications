import networkx as nx
import plotly.graph_objects as go
import sys
import math

# -------------------------
# GET CONCEPTS FROM COMMAND LINE or default list
words = sys.argv[1:]
if not words:
    words = [
        "Beans", "Angel", "Chaos", "Spiral", "Spirit", "Trust",
        "Order", "Love", "Infinity", "Divine", "Light", "Shadow",
        "Hope", "Fear", "Truth", "Lie", "Mind", "Soul", "Energy",
        "Power", "Harmony", "Balance", "Flow", "Cycle", "Pulse"
    ]

print("🌱 Concepts:", words)

# -------------------------
# GEMATRIA FUNCTIONS
def simple(word):
    return sum(ord(c) - 64 for c in word.upper() if 'A' <= c <= 'Z')

def jewish(word):
    return sum((ord(c) - 64) * 6 for c in word.upper() if 'A' <= c <= 'Z')

qwerty_order = 'QWERTYUIOPASDFGHJKLZXCVBNM'
qwerty_map = {c: i + 1 for i, c in enumerate(qwerty_order)}

def qwerty(word):
    return sum(qwerty_map.get(c, 0) for c in word.upper())

def jewish_qwerty(word):
    return sum(qwerty_map.get(c, 0) * 6 for c in word.upper())

# Placeholder for your idea numerology calculation —  
# you can replace with your own logic later
def idea_numerology(word):
    # Simple example: sum of letter positions squared mod 100
    return sum((ord(c) - 64) ** 2 for c in word.upper() if 'A' <= c <= 'Z') % 100

# -------------------------
# BINARY REPRESENTATION OF WORD
def binary_string(word):
    return ''.join(format(ord(c), '08b') for c in word)

# Check if number is prime
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(math.isqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

# -------------------------
# Build resonance layers with values
layers = {
    "Simple": {},
    "Jewish": {},
    "Qwerty": {},
    "Jewish-Qwerty": {},
    "IdeaNumerology": {},
    "Binary": {}  # binary string to words mapping
}

calc_funcs = {
    "Simple": simple,
    "Jewish": jewish,
    "Qwerty": qwerty,
    "Jewish-Qwerty": jewish_qwerty,
    "IdeaNumerology": idea_numerology,
    "Binary": binary_string
}

for layer, func in calc_funcs.items():
    for w in words:
        val = func(w)
        if layer == "Binary":
            # For binary, val is string; map exact matches
            layers[layer].setdefault(val, []).append(w)
        else:
            layers[layer].setdefault(val, []).append(w)

# -------------------------
# Build graph
G = nx.Graph()
for w in words:
    G.add_node(w)

edges_by_layer = {}

# For each layer, find pairs that resonate (same value)
for layer, groups in layers.items():
    edges_by_layer[layer] = []
    for val, group in groups.items():
        if len(group) > 1:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    edges_by_layer[layer].append((group[i], group[j], val))

# -------------------------
# Assign colors per layer for edges and primes
layer_colors = {
    "Simple": "cyan",
    "Jewish": "magenta",
    "Qwerty": "yellow",
    "Jewish-Qwerty": "lime",
    "IdeaNumerology": "orange",
    "Binary": "deepskyblue"
}

prime_glow_color = "gold"

# -------------------------
# Positioning: lock Beans at center
fixed_pos = {'Beans': [0, 0, 0]}
pos = nx.spring_layout(G, dim=3, seed=42, pos=fixed_pos, fixed=fixed_pos.keys())

# -------------------------
# Helper to assign stable color per node name
colorscale = ["red", "orange", "yellow", "green", "cyan", "blue", "magenta", "pink", "lime"]
def color_for_node(name):
    return colorscale[hash(name) % len(colorscale)]

node_colors = [color_for_node(n) for n in G.nodes()]

# -------------------------
# Build plotly traces
fig = go.Figure()

# Add edges per layer with hover info & prime glow if applicable
for layer, edges in edges_by_layer.items():
    x, y, z, text, line_colors, line_widths = [], [], [], [], [], []
    for a, b, val in edges:
        x += [pos[a][0], pos[b][0], None]
        y += [pos[a][1], pos[b][1], None]
        z += [pos[a][2], pos[b][2], None]

        hover = f"{layer} resonance: {val}"

        # Glow edges if prime value and not binary layer
        prime = False
        if layer != "Binary":
            prime = is_prime(val)
        if prime:
            line_colors.append(prime_glow_color)
            line_widths.append(6)
            hover += " 🧬 prime"
        else:
            line_colors.append(layer_colors[layer])
            line_widths.append(3)

        # Because Plotly lines can't vary per segment, store info to split later (see below)
        text += [hover, hover, None]

    # Create one trace per layer (Plotly can't do per-segment color)
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        line=dict(width=3, color=layer_colors[layer]),
        name=f"{layer} connections",
        text=text,
        hoverinfo='text',
        visible=False
    ))

# Add nodes with labels, colors, and prime glow halo if prime under any layer
node_hover = []
node_marker_colors = []
node_marker_sizes = []

for n in G.nodes():
    # Check prime status for any gematria layer (excluding binary)
    prime_any = any(
        is_prime(calc_funcs[layer](n)) 
        for layer in ["Simple", "Jewish", "Qwerty", "Jewish-Qwerty", "IdeaNumerology"]
    )
    node_marker_sizes.append(14 if prime_any else 10)
    node_marker_colors.append(prime_glow_color if prime_any else color_for_node(n))
    node_hover.append(n + (" 🧬 prime" if prime_any else ""))

node_x = [pos[n][0] for n in G.nodes()]
node_y = [pos[n][1] for n in G.nodes()]
node_z = [pos[n][2] for n in G.nodes()]

fig.add_trace(go.Scatter3d(
    x=node_x, y=node_y, z=node_z,
    mode='markers+text',
    marker=dict(size=node_marker_sizes, color=node_marker_colors, line=dict(color='white', width=1)),
    text=list(G.nodes()),
    textfont=dict(color=node_marker_colors),
    textposition="top center",
    hovertext=node_hover,
    name="Nodes",
    visible=True
))

# -------------------------
# Toggle buttons for layers + combined views
layer_keys = list(edges_by_layer.keys())

# Build visibility masks for toggles (nodes always visible)
def visibility_mask(active_layers):
    mask = []
    for layer in layer_keys:
        mask.append(layer in active_layers)
    mask.append(True)  # nodes visible always
    return mask

buttons = []

# Single-layer toggles
for layer in layer_keys:
    buttons.append(dict(
        label=f"Show {layer}",
        method="update",
        args=[{"visible": visibility_mask([layer])},
              {"title": f"Nodes + {layer} resonance connections"}]
    ))

# Multi-layer toggle example — show all
buttons.append(dict(
    label="Show ALL",
    method="update",
    args=[{"visible": visibility_mask(layer_keys)},
          {"title": "Nodes + ALL resonance connections"}]
))

# Show only nodes
buttons.append(dict(
    label="Show only nodes",
    method="update",
    args=[{"visible": visibility_mask([])},
          {"title": "Nodes only (no connections)"}]
))

# -------------------------
# Add buttons to layout
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="down",
            buttons=buttons,
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.02,
            xanchor="left",
            y=0.9,
            yanchor="top",
            bgcolor='rgba(30,30,30,0.8)',
            borderwidth=1,
            bordercolor='white',
            font=dict(color='white')
        )
    ]
)

# -------------------------
# DARK COSMIC BACKGROUND & AXES
fig.update_layout(
    title="Beans Multi-Dimensional Resonance Network",
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
    scene=dict(
        bgcolor='#0a001f',
        xaxis=dict(title='BeansLogic', color='white'),
        yaxis=dict(title='Truth', color='white'),
        zaxis=dict(title='Gematria', color='white'),
    ),
    showlegend=True
)

fig.show()