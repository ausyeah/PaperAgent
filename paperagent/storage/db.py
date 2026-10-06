import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Union
import logging

from paperagent.models import (
    PaperProject,
    ParsedPaper,
    AnalysisReport,
    SynthesisResult,
    StoredPaperRecord
)

logger = logging.getLogger(__name__)


class PaperStorage:
    """SQLite-backed persistent repository for papers, analysis reports, and code syntheses."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """
        Initialize the PaperStorage.
        If db_path is not provided, defaults to ~/.paperagent/library.db.
        Creates parent directories and schema if they do not exist.
        """
        if db_path is None:
            db_path = Path.home() / ".paperagent" / "library.db"

        str_path = str(db_path)
        if str_path == ":memory:" or str_path.startswith("file:"):
            self.db_path = str_path
            self._is_uri = str_path.startswith("file:")
            self._keepalive = self._get_connection()
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._is_uri = False
            self._keepalive = None

        self._init_db()


    def _get_connection(self):
        if self._is_uri:
            return sqlite3.connect(str(self.db_path), uri=True)
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        """Create the necessary database tables if they do not exist."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    arxiv_id TEXT,
                    created_at TEXT,
                    tags TEXT,
                    summary TEXT,
                    has_code INTEGER,
                    parsed_json TEXT,
                    analysis_json TEXT,
                    synthesis_json TEXT
                )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing database at {self.db_path}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def save_paper(self, project: PaperProject, tags: Optional[List[str]] = None) -> StoredPaperRecord:
        """
        Saves a PaperProject to the database.
        Inserts or replaces the row.
        Returns a lightweight StoredPaperRecord.
        """
        if tags is None:
            tags = []

        # Determine has_code
        has_code = bool(project.synthesis and project.synthesis.target_module_code)

        # Serialize parts of PaperProject
        parsed_json = project.paper.model_dump_json() if project.paper else None
        analysis_json = project.analysis.model_dump_json() if project.analysis else None
        synthesis_json = project.synthesis.model_dump_json() if project.synthesis else None

        # Tags formatting
        tags_str = json.dumps(tags)

        # Summary
        summary = ""
        if project.analysis and project.analysis.executive_summary:
            summary = project.analysis.executive_summary

        arxiv_id = project.paper.metadata.arxiv_id if project.paper and project.paper.metadata else None

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO papers (
                    id, title, arxiv_id, created_at, tags, summary, has_code,
                    parsed_json, analysis_json, synthesis_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.id,
                project.paper.metadata.title if project.paper and project.paper.metadata else "",
                arxiv_id,
                project.created_at.isoformat(),
                tags_str,
                summary,
                1 if has_code else 0,
                parsed_json,
                analysis_json,
                synthesis_json
            ))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving paper {project.id}: {e}")
            raise
        finally:
            if conn:
                conn.close()

        return StoredPaperRecord(
            id=project.id,
            title=project.paper.metadata.title if project.paper and project.paper.metadata else "",
            arxiv_id=arxiv_id,
            created_at=project.created_at.isoformat(),
            tags=tags,
            summary=summary,
            has_code=has_code
        )

    def get_paper(self, paper_id: str) -> Optional[PaperProject]:
        """
        Fetches a PaperProject by id. Returns None if not found.
        """
        conn = None
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, created_at, parsed_json, analysis_json, synthesis_json
                FROM papers WHERE id = ?
            ''', (paper_id,))
            row = cursor.fetchone()

            if not row:
                return None

            parsed_json = row['parsed_json']
            analysis_json = row['analysis_json']
            synthesis_json = row['synthesis_json']

            paper = ParsedPaper.model_validate_json(parsed_json) if parsed_json else None
            analysis = AnalysisReport.model_validate_json(analysis_json) if analysis_json else None
            synthesis = SynthesisResult.model_validate_json(synthesis_json) if synthesis_json else None

            # Create paper project object using validate method to parse iso format string
            # We do not override created_at directly if we pass it through init.
            # Just use validate_json or standard parsing
            project_data = {
                "id": row['id'],
                "created_at": row['created_at'],
            }
            if paper:
                project_data['paper'] = paper.model_dump()
            if analysis:
                project_data['analysis'] = analysis.model_dump()
            if synthesis:
                project_data['synthesis'] = synthesis.model_dump()

            return PaperProject(**project_data)

        except sqlite3.Error as e:
            logger.error(f"Error retrieving paper {paper_id}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def list_papers(self, limit: int = 50, offset: int = 0, tag: Optional[str] = None) -> List[StoredPaperRecord]:
        """
        Lists stored papers, ordered by created_at DESC.
        Supports pagination and basic tag filtering.
        """
        records = []
        conn = None
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = '''
                SELECT id, title, arxiv_id, created_at, tags, summary, has_code
                FROM papers
            '''
            params = []

            if tag:
                # Very basic JSON array string search since SQLite json1 might not be guaranteed
                # For a robust implementation, json_each could be used, but this works for basic json dump
                query += " WHERE tags LIKE ?"
                params.append(f'%"{tag}"%')

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            for row in rows:
                tags_list = json.loads(row['tags']) if row['tags'] else []
                records.append(StoredPaperRecord(
                    id=row['id'],
                    title=row['title'],
                    arxiv_id=row['arxiv_id'],
                    created_at=row['created_at'],
                    tags=tags_list,
                    summary=row['summary'] or "",
                    has_code=bool(row['has_code'])
                ))
        except sqlite3.Error as e:
            logger.error(f"Error listing papers: {e}")
            raise
        finally:
            if conn:
                conn.close()

        return records

    def search_papers(self, query: str, limit: int = 20) -> List[StoredPaperRecord]:
        """
        Searches papers by title, summary, or arxiv_id using case-insensitive LIKE.
        """
        records = []
        conn = None
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            search_term = f"%{query}%"

            cursor.execute('''
                SELECT id, title, arxiv_id, created_at, tags, summary, has_code
                FROM papers
                WHERE title LIKE ? OR summary LIKE ? OR arxiv_id LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (search_term, search_term, search_term, limit))
            rows = cursor.fetchall()

            for row in rows:
                tags_list = json.loads(row['tags']) if row['tags'] else []
                records.append(StoredPaperRecord(
                    id=row['id'],
                    title=row['title'],
                    arxiv_id=row['arxiv_id'],
                    created_at=row['created_at'],
                    tags=tags_list,
                    summary=row['summary'] or "",
                    has_code=bool(row['has_code'])
                ))
        except sqlite3.Error as e:
            logger.error(f"Error searching papers with query '{query}': {e}")
            raise
        finally:
            if conn:
                conn.close()

        return records

    def delete_paper(self, paper_id: str) -> bool:
        """
        Deletes a paper by id. Returns True if a record was deleted, False otherwise.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting paper {paper_id}: {e}")
            raise
        finally:
            if conn:
                conn.close()
