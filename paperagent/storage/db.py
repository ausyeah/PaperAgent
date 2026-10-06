import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
from paperagent.models import PaperProject, StoredPaperRecord

class PaperStorage:
    def __init__(self, db_path: str = "paperagent.db"):
        self.db_path = db_path
        self._uri = db_path.startswith("file:")
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, uri=self._uri)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    arxiv_id TEXT,
                    created_at TEXT NOT NULL,
                    tags TEXT,
                    summary TEXT,
                    has_code BOOLEAN,
                    project_data TEXT NOT NULL
                )
            ''')
            conn.commit()

    def save_paper(self, project: PaperProject) -> StoredPaperRecord:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            created_at = project.created_at.isoformat()

            has_code = bool(project.synthesis and project.synthesis.target_module_code)
            summary = ""
            if project.analysis:
                summary = project.analysis.executive_summary

            tags = project.paper.metadata.categories if project.paper.metadata.categories else []

            cursor.execute('''
                INSERT OR REPLACE INTO papers
                (id, title, arxiv_id, created_at, tags, summary, has_code, project_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.id,
                project.paper.metadata.title,
                project.paper.metadata.arxiv_id,
                created_at,
                json.dumps(tags),
                summary,
                has_code,
                project.model_dump_json()
            ))
            conn.commit()

            return StoredPaperRecord(
                id=project.id,
                title=project.paper.metadata.title,
                arxiv_id=project.paper.metadata.arxiv_id,
                created_at=created_at,
                tags=tags,
                summary=summary,
                has_code=has_code
            )

    def get_paper(self, paper_id: str) -> Optional[PaperProject]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT project_data FROM papers WHERE id = ?', (paper_id,))
            row = cursor.fetchone()
            if row:
                return PaperProject.model_validate_json(row[0])
            return None

    def list_papers(self, limit: int = 50, offset: int = 0, tag: Optional[str] = None, q: Optional[str] = None) -> List[StoredPaperRecord]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT id, title, arxiv_id, created_at, tags, summary, has_code FROM papers'
            params = []

            conditions = []
            if tag:
                conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            if q:
                conditions.append("(title LIKE ? OR summary LIKE ?)")
                params.append(f'%{q}%')
                params.append(f'%{q}%')

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                StoredPaperRecord(
                    id=row[0],
                    title=row[1],
                    arxiv_id=row[2],
                    created_at=row[3],
                    tags=json.loads(row[4]),
                    summary=row[5],
                    has_code=bool(row[6])
                )
                for row in rows
            ]

    def delete_paper(self, paper_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM papers WHERE id = ?', (paper_id,))
            conn.commit()
            return cursor.rowcount > 0
