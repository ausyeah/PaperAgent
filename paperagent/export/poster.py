import json
import os
from typing import Optional, List

from paperagent.models import PaperProject, AcademicPosterBundle, PosterSection, BenchmarkEvaluationResult

class AcademicPosterGenerator:
    """Generates an automated academic conference poster."""
    
    def generate_poster(self, project: PaperProject, output_path: Optional[str] = None) -> AcademicPosterBundle:
        """Synthesizes a 3-column academic conference poster HTML/CSS bundle."""
        
        title = project.paper.metadata.title
        authors = project.paper.metadata.authors
        authors_str = ", ".join(authors) if authors else "Unknown Authors"
        
        # Determine content for columns based on analysis/synthesis
        motivation = project.analysis.core_problem if project.analysis else "Motivation not available."
        methodology = project.analysis.methodology_overview if project.analysis else "Methodology not available."
        innovation = project.analysis.key_innovation if project.analysis else "Key innovation not available."
        
        # Try to find some formulas
        formulas_html = ""
        if project.analysis and project.analysis.formula_explanations:
            for f in project.analysis.formula_explanations[:2]:
                formulas_html += f"<div class='formula-box'><div class='math'>$${f.latex}$$</div><p>{f.intuitive_intuition}</p></div>"
        
        # Results / Conclusion
        results_html = "<p>Empirical results and table comparison.</p>"
        # Assuming we don't have benchmark_evaluation on synthesis directly but we might get it elsewhere.
        # Given it's missing, let's keep it simple for now as it's not strictly available.
        # But for test compatibility if we want to fake a benchmark evaluation in test:
        
        conclusion_html = "<p>Conclusion based on the findings.</p>"
        if project.analysis and project.analysis.executive_summary:
            conclusion_html += f"<p>{project.analysis.executive_summary}</p>"
        
        # Build sections
        sections = [
            PosterSection(title="Motivation", content_html=f"<p>{motivation}</p>", order=1),
            PosterSection(title="Methodology", content_html=f"<p>{methodology}</p>", order=2),
            PosterSection(title="Key Innovation", content_html=f"<p>{innovation}</p>", order=3),
            PosterSection(title="Equations", content_html=formulas_html, order=4),
            PosterSection(title="Results", content_html=results_html, order=5),
            PosterSection(title="Conclusion", content_html=conclusion_html, order=6),
        ]
        
        col1 = "".join([f"<div class='section'><h2>{s.title}</h2>{s.content_html}</div>" for s in sections if s.order in [1, 2]])
        col2 = "".join([f"<div class='section'><h2>{s.title}</h2>{s.content_html}</div>" for s in sections if s.order in [3, 4]])
        col3 = "".join([f"<div class='section'><h2>{s.title}</h2>{s.content_html}</div>" for s in sections if s.order in [5, 6]])
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} - Poster</title>
    <!-- KaTeX -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body, {{
            delimiters: [
                {{left: '$$', right: '$$', display: true}},
                {{left: '$', right: '$', display: false}}
            ]
        }});"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f4f9;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        .poster-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #0056b3;
            padding-bottom: 20px;
        }}
        .header h1 {{
            font-size: 2.5em;
            color: #0056b3;
            margin: 0 0 10px 0;
        }}
        .header h3 {{
            font-weight: normal;
            color: #555;
            margin: 0;
        }}
        .columns {{
            display: flex;
            gap: 30px;
        }}
        .column {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .section {{
            background: #fafafa;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .section h2 {{
            color: #0056b3;
            margin-top: 0;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        .formula-box {{
            background: #fff;
            border-left: 4px solid #0056b3;
            padding: 10px;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="poster-container">
        <div class="header">
            <h1>{title}</h1>
            <h3>{authors_str}</h3>
        </div>
        <div class="columns">
            <div class="column col1">
                {col1}
            </div>
            <div class="column col2">
                {col2}
            </div>
            <div class="column col3">
                {col3}
            </div>
        </div>
    </div>
</body>
</html>"""
        
        bundle = AcademicPosterBundle(
            paper_title=title,
            authors=authors,
            sections=sections,
            standalone_poster_html=html_template
        )
        
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_template)
                
        return bundle