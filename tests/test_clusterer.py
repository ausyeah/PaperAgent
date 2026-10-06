import pytest
from datetime import datetime
from paperagent.models import StoredPaperRecord
from paperagent.storage.clusterer import PaperLibraryClusterer

def test_paper_library_clusterer():
    papers = [
        StoredPaperRecord(
            id="p1",
            title="Deep Learning for Computer Vision",
            created_at=datetime.now().isoformat(),
            summary="A deep learning approach to image classification and computer vision using CNNs.",
            tags=["vision", "deep learning"]
        ),
        StoredPaperRecord(
            id="p2",
            title="Transformers in Natural Language Processing",
            created_at=datetime.now().isoformat(),
            summary="Using transformer architectures for NLP tasks like translation and text generation.",
            tags=["nlp", "transformers"]
        ),
        StoredPaperRecord(
            id="p3",
            title="Image Segmentation with Convolutional Networks",
            created_at=datetime.now().isoformat(),
            summary="Convolutional neural networks for semantic image segmentation.",
            tags=["vision", "cnn"]
        ),
        StoredPaperRecord(
            id="p4",
            title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            created_at=datetime.now().isoformat(),
            summary="A new language representation model called BERT, designed to pre-train deep bidirectional representations from unlabeled text.",
            tags=["nlp", "bert"]
        ),
    ]

    clusterer = PaperLibraryClusterer()
    result = clusterer.cluster_papers(papers, num_clusters=2)

    assert result is not None
    assert len(result.clusters) == 2
    
    # Check that vision papers are grouped and NLP papers are grouped
    cluster_pids = [set(c.paper_ids) for c in result.clusters]
    
    vision_group = {"p1", "p3"}
    nlp_group = {"p2", "p4"}
    
    # One cluster should contain vision papers, another NLP papers
    matched_vision = False
    matched_nlp = False
    for pids in cluster_pids:
        if vision_group.issubset(pids):
            matched_vision = True
        if nlp_group.issubset(pids):
            matched_nlp = True
            
    assert matched_vision, "Vision papers were not grouped together."
    assert matched_nlp, "NLP papers were not grouped together."

    # Check keywords
    for c in result.clusters:
        assert len(c.keywords) > 0
        assert c.cluster_name != ""
        assert c.summary != ""

def test_empty_papers():
    clusterer = PaperLibraryClusterer()
    result = clusterer.cluster_papers([], num_clusters=2)
    assert len(result.clusters) == 0

def test_single_paper():
    papers = [
        StoredPaperRecord(
            id="p1",
            title="Deep Learning for Computer Vision",
            created_at=datetime.now().isoformat(),
            summary="A deep learning approach to image classification and computer vision using CNNs.",
            tags=["vision", "deep learning"]
        )
    ]
    clusterer = PaperLibraryClusterer()
    result = clusterer.cluster_papers(papers, num_clusters=3)
    assert len(result.clusters) == 1
    assert result.clusters[0].paper_ids == ["p1"]
    assert "vision" in result.clusters[0].keywords or "learning" in result.clusters[0].keywords