import json
from typing import Optional, Any, Dict, List

from paperagent.models import CitationGraph, GraphVisualizationBundle

ROLE_COLORS = {
    'foundation': '#3b82f6', # blue
    'baseline': '#f97316',   # orange
    'successor': '#22c55e',  # green
    'related': '#6b7280',    # gray
}

def export_citation_graph_html(graph: CitationGraph, output_path: Optional[str] = None) -> GraphVisualizationBundle:
    """
    Converts CitationGraph nodes and edges into an interactive HTML visualization bundle.
    """
    
    vis_nodes: List[Dict[str, Any]] = []
    
    for node in graph.nodes:
        color = ROLE_COLORS.get(node.influence_role, ROLE_COLORS['related'])
        
        vis_node = {
            "id": node.title,
            "label": node.title,
            "color": color,
            "title": f"Authors: {', '.join(node.authors) if node.authors else 'Unknown'}<br>Role: {node.influence_role}",
            "hidden": False,
            "authors": node.authors,
            "year": node.year,
            "arxiv_id": node.arxiv_id,
            "doi": node.doi,
            "citation_count": node.citation_count,
            "influence_role": node.influence_role
        }
        vis_nodes.append(vis_node)
        
    vis_edges: List[Dict[str, Any]] = []
    
    for edge in graph.edges:
        vis_edge = {
            "from": edge.get("source"),
            "to": edge.get("target"),
            "label": edge.get("relation", ""),
            "arrows": "to"
        }
        vis_edges.append(vis_edge)
        
    nodes_json = json.dumps(vis_nodes)
    edges_json = json.dumps(vis_edges)
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Citation Graph: {graph.root_paper_title}</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            height: 100vh;
            font-family: Arial, sans-serif;
        }}
        #container {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        #toolbar {{
            padding: 10px;
            background: #f3f4f6;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        #search {{
            padding: 5px;
            width: 300px;
        }}
        #network {{
            flex: 1;
        }}
        #sidebar {{
            width: 300px;
            background: #f9fafb;
            border-left: 1px solid #e5e7eb;
            padding: 20px;
            box-sizing: border-box;
            overflow-y: auto;
        }}
        h2, h3 {{
            margin-top: 0;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        .color-box {{
            width: 15px;
            height: 15px;
            margin-right: 10px;
            border-radius: 3px;
        }}
        .detail-row {{
            margin-bottom: 10px;
        }}
        .detail-label {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="toolbar">
            <label for="search">Search:</label>
            <input type="text" id="search" placeholder="Type to filter nodes...">
        </div>
        <div id="network"></div>
    </div>
    <div id="sidebar">
        <h2>Node Details</h2>
        <div id="details">
            <p>Select a node to see details.</p>
        </div>
        
        <h3 style="margin-top: 20px;">Legend</h3>
        <div class="legend-item"><div class="color-box" style="background-color: {ROLE_COLORS['foundation']}"></div>Foundation</div>
        <div class="legend-item"><div class="color-box" style="background-color: {ROLE_COLORS['baseline']}"></div>Baseline</div>
        <div class="legend-item"><div class="color-box" style="background-color: {ROLE_COLORS['successor']}"></div>Successor</div>
        <div class="legend-item"><div class="color-box" style="background-color: {ROLE_COLORS['related']}"></div>Related</div>
    </div>

    <script type="text/javascript">
        const nodesData = {nodes_json};
        const edgesData = {edges_json};
        
        const nodes = new vis.DataSet(nodesData);
        const edges = new vis.DataSet(edgesData);
        
        const container = document.getElementById('network');
        const data = {{
            nodes: nodes,
            edges: edges
        }};
        
        const options = {{
            nodes: {{
                shape: 'dot',
                size: 20,
                font: {{
                    size: 14,
                    color: '#333'
                }},
                borderWidth: 2
            }},
            edges: {{
                width: 1,
                color: '#999'
            }},
            physics: {{
                forceAtlas2Based: {{
                    gravitationalConstant: -26,
                    centralGravity: 0.005,
                    springLength: 230,
                    springConstant: 0.18
                }},
                maxVelocity: 146,
                solver: 'forceAtlas2Based',
                timestep: 0.35,
                stabilization: {{iterations: 150}}
            }}
        }};
        
        const network = new vis.Network(container, data, options);
        
        network.on('click', function(params) {{
            const detailsDiv = document.getElementById('details');
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                
                let authorsHtml = 'Unknown';
                if (node.authors && node.authors.length > 0) {{
                    authorsHtml = node.authors.join(', ');
                }}
                
                let detailsHtml = `
                    <div class="detail-row"><span class="detail-label">Title:</span> ${{node.label}}</div>
                    <div class="detail-row"><span class="detail-label">Role:</span> ${{node.influence_role || 'Unknown'}}</div>
                    <div class="detail-row"><span class="detail-label">Authors:</span> ${{authorsHtml}}</div>
                `;
                
                if (node.year) detailsHtml += `<div class="detail-row"><span class="detail-label">Year:</span> ${{node.year}}</div>`;
                if (node.arxiv_id) detailsHtml += `<div class="detail-row"><span class="detail-label">ArXiv:</span> ${{node.arxiv_id}}</div>`;
                if (node.doi) detailsHtml += `<div class="detail-row"><span class="detail-label">DOI:</span> ${{node.doi}}</div>`;
                if (node.citation_count !== null && node.citation_count !== undefined) detailsHtml += `<div class="detail-row"><span class="detail-label">Citations:</span> ${{node.citation_count}}</div>`;
                
                detailsDiv.innerHTML = detailsHtml;
            }} else {{
                detailsDiv.innerHTML = '<p>Select a node to see details.</p>';
            }}
        }});
        
        document.getElementById('search').addEventListener('input', function(e) {{
            const query = e.target.value.toLowerCase();
            const updates = [];
            nodes.forEach(function(node) {{
                const match = node.label.toLowerCase().includes(query) || 
                              (node.authors && node.authors.join(' ').toLowerCase().includes(query));
                updates.push({{id: node.id, hidden: !match}});
            }});
            nodes.update(updates);
        }});
    </script>
</body>
</html>"""
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
    return GraphVisualizationBundle(
        paper_title=graph.root_paper_title,
        nodes=vis_nodes,
        edges=vis_edges,
        standalone_html=html_template
    )