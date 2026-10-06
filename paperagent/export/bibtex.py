from paperagent.models import PaperMetadata

def generate_bibtex(meta: PaperMetadata) -> str:
    """Generates standard BibTeX citation entry (@article{...})."""
    # Simple ID generation
    author_id = meta.authors[0].split()[-1].lower() if meta.authors else "unknown"
    year_id = str(meta.year) if meta.year else "nd"
    citation_id = f"{author_id}{year_id}{meta.title.split()[0].lower() if meta.title else 'paper'}"

    # Remove non-alphanumeric characters for ID
    citation_id = ''.join(c for c in citation_id if c.isalnum())

    lines = [f"@article{{{citation_id},"]
    lines.append(f"  title={{{meta.title}}},")

    if meta.authors:
        authors_str = " and ".join(meta.authors)
        lines.append(f"  author={{{authors_str}}},")

    if meta.year:
        lines.append(f"  year={{{meta.year}}},")

    if meta.doi:
        lines.append(f"  doi={{{meta.doi}}},")

    if meta.arxiv_id:
        lines.append(f"  journal={{arXiv preprint arXiv:{meta.arxiv_id}}},")

    lines.append("}")

    return "\n".join(lines)
