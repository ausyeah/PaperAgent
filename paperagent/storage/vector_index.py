import math
import re
from typing import List, Tuple, Dict, Set
from paperagent.models import StoredPaperRecord

class PaperSearchIndex:
    """
    Pure-Python, zero-heavy-dependency search index using BM25 scoring algorithm.
    Tokenizes title, summary, and tags for indexing.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: Dict[str, StoredPaperRecord] = {}
        # Document frequencies for words: df[term] = number of docs containing term
        self.df: Dict[str, int] = {}
        # Inverted index: tf[term][doc_id] = count
        self.tf: Dict[str, Dict[str, int]] = {}
        # Document lengths
        self.doc_lengths: Dict[str, int] = {}
        self.total_length: int = 0
        self.avgdl: float = 0.0
        self.total_docs: int = 0

        self.stopwords: Set[str] = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "were", "will", "with", "we", "this", "these", "those"
        }

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenizes text by lowercasing, stripping punctuation, and removing stopwords.
        """
        # Lowercase and replace non-alphanumeric characters with space
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        tokens = text.split()
        return [t for t in tokens if t not in self.stopwords and len(t) > 1]

    def _extract_document_text(self, record: StoredPaperRecord) -> str:
        """
        Combines relevant fields from the record into a single searchable text string.
        """
        parts = [record.title]
        if record.summary:
            parts.append(record.summary)
        if record.tags:
            parts.extend(record.tags)
        return " ".join(parts)

    def _update_avgdl(self):
        """Updates the average document length."""
        if self.total_docs > 0:
            self.avgdl = self.total_length / self.total_docs
        else:
            self.avgdl = 0.0

    def add_paper(self, record: StoredPaperRecord) -> None:
        """
        Indexes a paper record using BM25 tokenization.
        If the paper is already indexed, it is replaced.
        """
        # Remove if already exists to ensure updated indexing
        if record.id in self.documents:
            self.remove_paper(record.id)

        text = self._extract_document_text(record)
        tokens = self._tokenize(text)

        doc_length = len(tokens)
        self.doc_lengths[record.id] = doc_length
        self.total_length += doc_length
        self.documents[record.id] = record

        term_counts: Dict[str, int] = {}
        for token in tokens:
            term_counts[token] = term_counts.get(token, 0) + 1

        # Update Document Frequencies and Inverted Index
        for token, count in term_counts.items():
            self.df[token] = self.df.get(token, 0) + 1
            if token not in self.tf:
                self.tf[token] = {}
            self.tf[token][record.id] = count

        self.total_docs += 1
        self._update_avgdl()

    def remove_paper(self, paper_id: str) -> bool:
        """
        Removes a paper from the index. Returns True if successfully removed.
        """
        if paper_id not in self.documents:
            return False

        # Cleanup Inverted Index and Document Frequencies
        tokens_to_remove = []
        for token, doc_dict in self.tf.items():
            if paper_id in doc_dict:
                del doc_dict[paper_id]

                # Update document frequency
                self.df[token] -= 1
                if self.df[token] <= 0:
                    del self.df[token]

                if not doc_dict:
                    tokens_to_remove.append(token)

        for token in tokens_to_remove:
            del self.tf[token]

        doc_length = self.doc_lengths[paper_id]
        self.total_length -= doc_length

        del self.doc_lengths[paper_id]
        del self.documents[paper_id]

        self.total_docs -= 1
        self._update_avgdl()
        return True

    def _idf(self, term: str) -> float:
        """
        Calculates the Inverse Document Frequency for a term.
        """
        df = self.df.get(term, 0)
        # BM25 IDF formulation: ln((N - df + 0.5) / (df + 0.5) + 1)
        # Using a standard BM25 idf smoothing
        return math.log(1 + (self.total_docs - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = 10) -> List[Tuple[StoredPaperRecord, float]]:
        """
        Scores papers against query terms using BM25 scoring and returns ranked records with relevance scores.
        """
        if self.total_docs == 0:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores: Dict[str, float] = {doc_id: 0.0 for doc_id in self.documents}

        for term in query_tokens:
            if term not in self.df or term not in self.tf:
                continue

            idf = self._idf(term)
            # Only iterate through documents that contain the term (using the inverted index)
            for doc_id, tf in self.tf[term].items():
                doc_len = self.doc_lengths[doc_id]
                # BM25 tf normalization
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / max(1.0, self.avgdl)))

                scores[doc_id] += idf * (numerator / denominator)

        # Filter out 0 scores
        ranked = [(self.documents[doc_id], score) for doc_id, score in scores.items() if score > 0.0]
        # Sort descending by score
        ranked.sort(key=lambda x: x[1], reverse=True)

        return ranked[:top_k]

    def size(self) -> int:
        """Returns the number of indexed papers."""
        return self.total_docs
