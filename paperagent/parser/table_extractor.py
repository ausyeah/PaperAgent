import re
import csv
import io
import uuid
from typing import List, Tuple

from paperagent.models import ParsedPaper, ExtractedTable, ExtractedTableCollection

class TableExtractor:
    """Extractor for markdown and LaTeX tables in paper text."""

    def __init__(self):
        # Match MD tables
        self.md_table_pattern = re.compile(
            r'(?:^[ \t]*(?:Table|Figure)\s+\d+[:\.].*?\n)*' # Optional caption above
            r'(^[ \t]*\|.*\|[ \t]*\n'          # Header
            r'^[ \t]*\|[-: |]+\|[ \t]*\n'     # Separator
            r'(?:^[ \t]*\|.*\|[ \t]*(?:\n|$))+)' # Rows
            r'(?:^[ \t]*(?:Table|Figure)\s+\d+[:\.].*?(?:\n|$))*', # Optional caption below
            re.MULTILINE
        )
        self.md_caption_pattern = re.compile(r'^(?:Table|Figure)\s+\d+[:\.](.*?)$', re.MULTILINE)

        # Match LaTeX table env
        self.latex_table_env_pattern = re.compile(
            r'\\begin\{(table\*?)\}(.*?)\\end\{\1\}',
            re.DOTALL
        )
        # Match LaTeX tabular env
        self.latex_tabular_env_pattern = re.compile(
            r'\\begin\{(tabular\*?|tabularx\*?)\}(?:\{[^}]*\})?(.*?)\\end\{\1\}',
            re.DOTALL
        )
        self.latex_caption_pattern = re.compile(r'\\caption(?:\[[^\]]*\])?\{(.*?)\}', re.DOTALL)


    def _csv_format(self, header: List[str], rows: List[List[str]]) -> str:
        if not header and not rows:
            return ""
        out = io.StringIO()
        writer = csv.writer(out)
        if header:
            writer.writerow(header)
        for row in rows:
            writer.writerow(row)
        return out.getvalue()

    def _extract_md_tables(self, text: str) -> List[ExtractedTable]:
        tables = []
        for match in self.md_table_pattern.finditer(text):
            full_match = match.group(0).strip()
            table_block = match.group(1).strip()
            
            # Extract caption
            caption = ""
            caption_match = self.md_caption_pattern.search(full_match)
            if caption_match:
                caption = caption_match.group(1).strip()
                
            lines = table_block.split('\n')
            if len(lines) < 3:
                continue
                
            headers = [col.strip() for col in lines[0].strip().strip('|').split('|')]
            rows = []
            for line in lines[2:]:
                if line.strip():
                    row = [col.strip() for col in line.strip().strip('|').split('|')]
                    rows.append(row)
                    
            tables.append(ExtractedTable(
                table_id=str(uuid.uuid4()),
                caption=caption,
                headers=headers,
                rows=rows,
                csv_data=self._csv_format(headers, rows)
            ))
            
        return tables

    def _parse_latex_tabular(self, tabular_content: str) -> Tuple[List[str], List[List[str]]]:
        lines = [line.strip() for line in tabular_content.split(r'\\')]
        
        clean_lines = []
        for line in lines:
            if not line:
                continue
            # Remove horizontal rules
            line = re.sub(r'\\(?:hline|toprule|midrule|bottomrule)', '', line).strip()
            if not line:
                continue
            row = [col.strip() for col in line.split('&')]
            clean_lines.append(row)
            
        if not clean_lines:
            return [], []
            
        headers = clean_lines[0]
        rows = clean_lines[1:] if len(clean_lines) > 1 else []
        return headers, rows

    def _extract_latex_tables(self, text: str) -> List[ExtractedTable]:
        tables = []
        
        # Process table environments
        for match in self.latex_table_env_pattern.finditer(text):
            table_content = match.group(2)
            
            caption = ""
            caption_match = self.latex_caption_pattern.search(table_content)
            if caption_match:
                caption = caption_match.group(1).replace('\n', ' ').strip()
                
            for tab_match in self.latex_tabular_env_pattern.finditer(table_content):
                tabular_content = tab_match.group(2)
                headers, rows = self._parse_latex_tabular(tabular_content)
                
                if headers:
                    tables.append(ExtractedTable(
                        table_id=str(uuid.uuid4()),
                        caption=caption,
                        headers=headers,
                        rows=rows,
                        csv_data=self._csv_format(headers, rows)
                    ))

        # Find tabular environments outside of table environments
        text_without_table_envs = self.latex_table_env_pattern.sub('', text)
        for tab_match in self.latex_tabular_env_pattern.finditer(text_without_table_envs):
            tabular_content = tab_match.group(2)
            headers, rows = self._parse_latex_tabular(tabular_content)
            
            if headers:
                tables.append(ExtractedTable(
                    table_id=str(uuid.uuid4()),
                    caption="",
                    headers=headers,
                    rows=rows,
                    csv_data=self._csv_format(headers, rows)
                ))
                
        return tables

    def extract_tables(self, paper: ParsedPaper) -> ExtractedTableCollection:
        """
        Parses paper text/markdown for markdown tables and LaTeX table/tabular blocks.
        """
        all_tables = []
        
        # Search raw markdown if available
        if paper.raw_markdown:
            all_tables.extend(self._extract_md_tables(paper.raw_markdown))
            all_tables.extend(self._extract_latex_tables(paper.raw_markdown))
            
        # Also search in individual section content
        for section in paper.sections:
            if section.content:
                # We need to make sure we don't duplicate if section content is derived from raw_markdown.
                # Since we don't have strict deduplication and usually sections are subsets,
                # let's just do a naive check if it's already extracted.
                # Actually, typically we parse the full raw text OR the sections. 
                # Let's extract from sections if raw_markdown is empty, otherwise skip to avoid dupes,
                # or just extract everything and deduplicate by content.
                pass
                
        # Deduplicate tables by csv_data
        unique_tables = []
        seen_csv = set()
        
        # We will iterate sections too to be safe, just deduplicate.
        extracted_from_sections = []
        if not paper.raw_markdown:
            for section in paper.sections:
                if section.content:
                    extracted_from_sections.extend(self._extract_md_tables(section.content))
                    extracted_from_sections.extend(self._extract_latex_tables(section.content))

        for tbl in all_tables + extracted_from_sections:
            if tbl.csv_data not in seen_csv:
                seen_csv.add(tbl.csv_data)
                unique_tables.append(tbl)
                
        return ExtractedTableCollection(
            paper_title=paper.metadata.title,
            tables=unique_tables
        )