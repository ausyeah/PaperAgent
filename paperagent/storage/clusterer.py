import math
import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict

from paperagent.models import StoredPaperRecord, TopicCluster, TopicClusterCollection

class PaperLibraryClusterer:
    """
    Semantic topic clustering and taxonomy mapper for stored papers.
    Uses pure-Python TF-IDF and K-Means for zero-dependency deterministic clustering.
    """

    def __init__(self, max_iters: int = 50):
        self.max_iters = max_iters
        self.stopwords: Set[str] = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "were", "will", "with", "we", "this", "these", "those",
            "paper", "proposed", "method", "model", "approach", "results", "show",
            "can", "which", "our", "an", "based", "using", "also", "new", "two"
        }

    def _tokenize(self, text: str) -> List[str]:
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        tokens = text.split()
        return [t for t in tokens if t not in self.stopwords and len(t) > 2]

    def cluster_papers(self, papers: List[StoredPaperRecord], num_clusters: int = 3) -> TopicClusterCollection:
        if not papers:
            return TopicClusterCollection(clusters=[])

        num_clusters = min(num_clusters, len(papers))

        # 1. Compute TF for each paper
        paper_tfs: List[Dict[str, int]] = []
        df: Dict[str, int] = defaultdict(int)
        
        for p in papers:
            text = f"{p.title} {p.summary} {' '.join(p.tags)}"
            tokens = self._tokenize(text)
            tf = defaultdict(int)
            for t in tokens:
                tf[t] += 1
            paper_tfs.append(tf)
            for t in set(tokens):
                df[t] += 1

        # 2. Compute TF-IDF vectors
        N = len(papers)
        vocab = list(df.keys())
        # To avoid log(1) == 0 for words appearing in all documents and nullifying them,
        # we can use smooth IDF: log((N + 1) / (df + 1)) + 1
        idf = {t: math.log((N + 1) / (df[t] + 1)) + 1.0 for t in vocab}

        vectors: List[Dict[str, float]] = []
        for tf in paper_tfs:
            vec = {}
            norm = 0.0
            for t, count in tf.items():
                val = count * idf[t]
                vec[t] = val
                norm += val * val
            norm = math.sqrt(norm) if norm > 0 else 1.0
            vectors.append({t: v/norm for t, v in vec.items()})

        # 3. K-Means Clustering (Deterministic init)
        centers: List[Dict[str, float]] = [dict(vectors[i]) for i in range(num_clusters)]
        
        assignments: List[int] = [-1] * N

        for _ in range(self.max_iters):
            new_assignments = []
            for vec in vectors:
                best_c = 0
                best_sim = -1.0
                for c_idx, center in enumerate(centers):
                    sim = sum(vec.get(t, 0) * center.get(t, 0) for t in vec)
                    if sim > best_sim:
                        best_sim = sim
                        best_c = c_idx
                new_assignments.append(best_c)

            if new_assignments == assignments:
                break
            assignments = new_assignments

            new_centers = [{} for _ in range(num_clusters)]
            counts = [0] * num_clusters
            for i, c in enumerate(assignments):
                counts[c] += 1
                for t, v in vectors[i].items():
                    new_centers[c][t] = new_centers[c].get(t, 0) + v
            
            for c in range(num_clusters):
                if counts[c] > 0:
                    norm = 0.0
                    for t in new_centers[c]:
                        new_centers[c][t] /= counts[c]
                        norm += new_centers[c][t] ** 2
                    norm = math.sqrt(norm) if norm > 0 else 1.0
                    for t in new_centers[c]:
                        new_centers[c][t] /= norm
                else:
                    # If empty cluster, keep old center to avoid losing it, though it won't attract points next time.
                    new_centers[c] = centers[c]
            
            centers = new_centers

        # 4. Formulate Topic Clusters
        clusters_out = []
        for c in range(num_clusters):
            c_paper_ids = [papers[i].id for i, a in enumerate(assignments) if a == c]
            if not c_paper_ids:
                continue

            center_vec = centers[c]
            sorted_terms = sorted(center_vec.items(), key=lambda x: x[1], reverse=True)
            top_keywords = [t for t, v in sorted_terms[:5] if v > 0]

            if not top_keywords:
                top_keywords = ["general"]

            cluster_name = " ".join(top_keywords[:2]).title() + " Papers"
            summary = f"A collection of papers discussing {', '.join(top_keywords)}."
            
            clusters_out.append(TopicCluster(
                cluster_name=cluster_name,
                keywords=top_keywords,
                paper_ids=c_paper_ids,
                summary=summary
            ))

        return TopicClusterCollection(clusters=clusters_out)