import datetime
from typing import List, Dict, Any, Optional

from paperagent.models import DailyDigestReport, StoredPaperRecord
from paperagent.storage.vector_index import PaperSearchIndex


class ArxivRadar:
    """
    ArXiv Daily Radar and Watchlist Semantic Monitor.
    Ranks incoming ArXiv feed candidate papers based on keyword relevance or BM25 vector index score.
    """

    def __init__(self, vector_index: Optional[Any] = None):
        """
        Initialize the radar.

        Args:
            vector_index: Optional existing PaperSearchIndex acting as a semantic watchlist.
        """
        self.vector_index = vector_index

    def generate_daily_digest(self, category_or_query: str, candidate_papers: List[Dict[str, Any]], top_k: int = 5) -> DailyDigestReport:
        """
        Ranks incoming ArXiv feed candidate papers based on keyword relevance or BM25 vector index score.
        Produces structured matched_papers with relevance scores and TLDRs, and an executive briefing.

        Args:
            category_or_query: The target topic, category, or search query.
            candidate_papers: List of dictionaries representing candidate papers.
                              Expected keys: 'id', 'title', 'summary' or 'abstract'.
            top_k: Number of top relevant papers to return.

        Returns:
            DailyDigestReport containing matched papers and an executive briefing.
        """
        if not candidate_papers:
            return DailyDigestReport(
                category_or_query=category_or_query,
                date=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
                matched_papers=[],
                executive_briefing=f"No new papers found for '{category_or_query}' today."
            )

        # Build a temporary index of the candidate papers for scoring
        temp_index = PaperSearchIndex()
        records_map = {}
        
        for i, paper in enumerate(candidate_papers):
            paper_id = paper.get("id", str(i))
            title = paper.get("title", "")
            summary = paper.get("summary", paper.get("abstract", ""))
            tags = paper.get("tags", paper.get("categories", []))
            
            # Format StoredPaperRecord for indexing
            record = StoredPaperRecord(
                id=paper_id,
                title=title,
                summary=summary,
                tags=tags,
                created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
            )
            temp_index.add_paper(record)
            records_map[paper_id] = paper

        # Rank based on the target category/query
        ranked_results = temp_index.search(category_or_query, top_k=len(candidate_papers))
        
        # We also want to consider the semantic watchlist if provided
        watchlist_scores = {}
        if self.vector_index is not None and getattr(self.vector_index, "total_docs", 0) > 0:
            for paper_id, record in temp_index.documents.items():
                # We query the global watchlist vector_index using the candidate's text
                query_text = f"{record.title} {record.summary}"
                # Search watchlist, get top match score
                watchlist_matches = self.vector_index.search(query_text, top_k=1)
                if watchlist_matches:
                    _, highest_score = watchlist_matches[0]
                    watchlist_scores[paper_id] = highest_score

        # Combine scores and rank
        final_ranking = []
        # If no query match from BM25, give it a 0 score
        query_scores = {record.id: score for record, score in ranked_results}
        
        for paper_id, record in temp_index.documents.items():
            q_score = query_scores.get(paper_id, 0.0)
            w_score = watchlist_scores.get(paper_id, 0.0)
            
            # Weighted combine or max. Let's use max for simplicity
            final_score = max(q_score, w_score)
            if final_score > 0.0:
                final_ranking.append((paper_id, final_score))
                
        # Sort by final score descending
        final_ranking.sort(key=lambda x: x[1], reverse=True)
        top_matches = final_ranking[:top_k]

        matched_papers = []
        for paper_id, score in top_matches:
            paper_data = records_map[paper_id]
            matched_papers.append({
                "id": paper_id,
                "title": paper_data.get("title", ""),
                "summary": paper_data.get("summary", paper_data.get("abstract", "")),
                "relevance_score": score
            })
            
        if matched_papers:
            # Deterministic executive briefing based on top hits
            titles = [f"'{p['title']}'" for p in matched_papers]
            titles_str = ", ".join(titles)
            briefing = f"Today's radar for '{category_or_query}' identified {len(matched_papers)} highly relevant breakthroughs, led by {titles_str}."
        else:
            briefing = f"No highly relevant papers matched '{category_or_query}' or watchlist today."

        return DailyDigestReport(
            category_or_query=category_or_query,
            date=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
            matched_papers=matched_papers,
            executive_briefing=briefing
        )