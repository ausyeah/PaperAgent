import pytest
from paperagent.models import ParsedPaper, PaperMetadata, PaperSection
from paperagent.parser.table_extractor import TableExtractor

@pytest.fixture
def table_extractor():
    return TableExtractor()

def test_extract_md_table_with_caption(table_extractor):
    markdown = """
    Some text here.
    
    Table 1: Important Results
    | Model | Accuracy | F1 Score |
    |---|---|---|
    | Baseline | 0.85 | 0.84 |
    | Ours | 0.95 | 0.94 |
    
    More text here.
    """
    
    paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper", authors=[], abstract="", year=2024),
        raw_markdown=markdown
    )
    
    collection = table_extractor.extract_tables(paper)
    
    assert collection.paper_title == "Test Paper"
    assert len(collection.tables) == 1
    
    table = collection.tables[0]
    assert table.caption == "Important Results"
    assert table.headers == ["Model", "Accuracy", "F1 Score"]
    assert table.rows == [
        ["Baseline", "0.85", "0.84"],
        ["Ours", "0.95", "0.94"]
    ]
    assert "Model,Accuracy,F1 Score\r\nBaseline,0.85,0.84\r\nOurs,0.95,0.94\r\n" in table.csv_data

def test_extract_md_table_no_caption(table_extractor):
    markdown = """
    | A | B |
    | :--- | ---: |
    | 1 | 2 |
    """
    paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper", authors=[], abstract="", year=2024),
        raw_markdown=markdown
    )
    collection = table_extractor.extract_tables(paper)
    
    assert len(collection.tables) == 1
    assert collection.tables[0].caption == ""
    assert collection.tables[0].headers == ["A", "B"]
    assert collection.tables[0].rows == [["1", "2"]]

def test_extract_latex_table_env(table_extractor):
    latex = r"""
    \begin{table}[ht]
    \centering
    \caption{Performance comparison on CIFAR-10}
    \begin{tabular}{c c c}
    Method & Param & Acc \\
    \hline
    A & 10M & 90\% \\
    B & 20M & 92\% \\
    \end{tabular}
    \end{table}
    """
    paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper", authors=[], abstract="", year=2024),
        raw_markdown=latex
    )
    collection = table_extractor.extract_tables(paper)
    
    assert len(collection.tables) == 1
    table = collection.tables[0]
    assert table.caption == "Performance comparison on CIFAR-10"
    assert table.headers == ["Method", "Param", "Acc"]
    assert table.rows == [
        ["A", "10M", "90\\%"],
        ["B", "20M", "92\\%"]
    ]

def test_extract_latex_tabular_env(table_extractor):
    latex = r"""
    Some inline tabular:
    \begin{tabular}{ll}
    X & Y \\
    \toprule
    1 & 2 \\
    3 & 4 \\
    \bottomrule
    \end{tabular}
    """
    paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper", authors=[], abstract="", year=2024),
        raw_markdown=latex
    )
    collection = table_extractor.extract_tables(paper)
    
    assert len(collection.tables) == 1
    table = collection.tables[0]
    assert table.caption == ""
    assert table.headers == ["X", "Y"]
    assert table.rows == [
        ["1", "2"],
        ["3", "4"]
    ]

def test_extract_empty_tables(table_extractor):
    paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper", authors=[], abstract="", year=2024),
        raw_markdown="No tables here."
    )
    collection = table_extractor.extract_tables(paper)
    assert len(collection.tables) == 0

def test_fallback_to_sections(table_extractor):
    markdown = """
    | Sec | Val |
    |---|---|
    | 1 | 10 |
    """
    paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper", authors=[], abstract="", year=2024),
        raw_markdown="",
        sections=[PaperSection(title="Results", content=markdown)]
    )
    collection = table_extractor.extract_tables(paper)
    assert len(collection.tables) == 1
    assert collection.tables[0].headers == ["Sec", "Val"]
