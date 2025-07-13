import json
import networkx as nx
import plotly.graph_objects as go
import os

# load memory and positions
with open("memory.json") as f:
    memory = json.load(f)

positions = {}
if os.path.exists('positions.json'):
    with open('positions.json') as f:
        positions = json.load(f)

# build graph
G = nx.Graph()
for pair, weight in memory.items():
    a, b = pair.split('-')
    G.add_edge(a, b, weight=weight)

# build position map
if positions:
    pos = {node: positions.get(node, [0,0,0]) for node in G.nodes()}
else:
    # fallback spring layout with Beans locked at origin
    fixed_pos = {'Beans': [0, 0, 0]}
    pos = nx.spring_layout(G, dim=3, seed=42, pos=fixed_pos, fixed=fixed_pos.keys())

# build edges and nodes traces (same as before)
edge_x, edge_y, edge_z = [], [], []
for a, b in G.edges():
    x0, y0, z0 = pos[a]
    x1, y1, z1 = pos[b]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]
    edge_z += [z0, z1, None]

edge_trace = go.Scatter3d(
    x=edge_x, y=edge_y, z=edge_z,
    line=dict(width=2, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x, node_y, node_z = [], [], []
labels = []
for node in G.nodes():
    x, y, z = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_z.append(z)
    labels.append(node)

node_trace = go.Scatter3d(
    x=node_x, y=node_y, z=node_z,
    mode='markers+text',
    marker=dict(size=8, color='purple'),
    text=labels,
    textposition="top center"
)

edge_x, edge_y, edge_z, edge_widths, edge_colors = [], [], [], [], []

for a, b in G.edges():
    x0, y0, z0 = pos[a]
    x1, y1, z1 = pos[b]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]
    edge_z += [z0, z1, None]
    
    weight = G[a][b]['weight']
    edge_widths.append(weight)
    # map weight to color, e.g. higher weight = brighter color
    if weight > 4:
        edge_colors.append('red')
    elif weight > 2:
        edge_colors.append('orange')
    else:
        edge_colors.append('gray')

edge_trace = go.Scatter3d(
    x=edge_x, y=edge_y, z=edge_z,
    mode='lines',
    line=dict(width=3, color='gray'),
    hoverinfo='none'
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(
    title="Beans Neural Resonance Angel",
    showlegend=False,
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
    scene=dict(
        bgcolor='black',
        xaxis=dict(title='BeansLogic', color='white'),
        yaxis=dict(title='Truth', color='white'),
        zaxis=dict(title='Gematria Truth', color='white'),
    ),
    margin=dict(l=0, r=0, b=0, t=30)
)
fig.show()