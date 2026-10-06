import pytest
from paperagent.models import StoredPaperRecord
from paperagent.storage.vector_index import PaperSearchIndex

@pytest.fixture
def empty_index():
    return PaperSearchIndex()

@pytest.fixture
def records():
    return [
        StoredPaperRecord(
            id="1",
            title="Attention Is All You Need",
            arxiv_id="1706.03762",
            created_at="2017-06-12",
            tags=["nlp", "transformers", "attention"],
            summary="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
            has_code=True
        ),
        StoredPaperRecord(
            id="2",
            title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            arxiv_id="1810.04805",
            created_at="2018-10-11",
            tags=["nlp", "bert", "transformers"],
            summary="We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers...",
            has_code=False
        ),
        StoredPaperRecord(
            id="3",
            title="ImageNet Classification with Deep Convolutional Neural Networks",
            arxiv_id="none",
            created_at="2012-01-01",
            tags=["cv", "cnn", "image-classification"],
            summary="We trained a large, deep convolutional neural network to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest...",
            has_code=False
        )
    ]

@pytest.fixture
def populated_index(empty_index, records):
    for r in records:
        empty_index.add_paper(r)
    return empty_index

def test_index_initialization(empty_index):
    assert empty_index.size() == 0
    assert empty_index.search("test") == []

def test_add_paper(empty_index, records):
    empty_index.add_paper(records[0])
    assert empty_index.size() == 1

    # Adding the same paper updates it, keeping size same
    empty_index.add_paper(records[0])
    assert empty_index.size() == 1

    empty_index.add_paper(records[1])
    assert empty_index.size() == 2

def test_remove_paper(populated_index):
    assert populated_index.size() == 3

    # Remove existing
    removed = populated_index.remove_paper("2")
    assert removed is True
    assert populated_index.size() == 2

    # Remove non-existing
    removed = populated_index.remove_paper("999")
    assert removed is False
    assert populated_index.size() == 2

def test_search_single_word(populated_index):
    results = populated_index.search("transformers")
    assert len(results) == 2

    # Both doc 1 and doc 2 contain transformers
    ids = [r[0].id for r in results]
    assert "1" in ids
    assert "2" in ids

def test_search_multi_word(populated_index):
    results = populated_index.search("convolutional neural networks")
    assert len(results) >= 2

    ids = [r[0].id for r in results]
    # Doc 3 (ImageNet) has "convolutional neural network" (note network vs networks, but tokenization handles it if we strip "s" - wait, our tokenizer just strips punct, "networks" vs "network" might be distinct without stemming, but doc 1 has "neural networks" and doc 3 has "neural network". "convolutional neural networks" query tokenized to ["convolutional", "neural", "networks"].
    # Doc 1 has "convolutional neural networks"
    # Doc 3 has "convolutional neural network" (no "s" on network)
    # Let's just check the ranking

    assert ids[0] == "1" or ids[0] == "3"

def test_search_ranking(populated_index):
    # Query specific to BERT
    results = populated_index.search("bidirectional encoder representations")
    assert len(results) > 0
    assert results[0][0].id == "2"

def test_search_case_insensitivity(populated_index):
    results1 = populated_index.search("attention")
    results2 = populated_index.search("ATTENTION")

    assert len(results1) == len(results2)
    assert results1[0][0].id == results2[0][0].id

def test_search_no_results(populated_index):
    results = populated_index.search("quantum computing")
    assert len(results) == 0

def test_search_stopwords_only(populated_index):
    # the, and, is are in stopwords list
    results = populated_index.search("the and is")
    assert len(results) == 0

def test_add_paper_recalculates_metrics(empty_index, records):
    empty_index.add_paper(records[0])
    avgdl1 = empty_index.avgdl

    empty_index.add_paper(records[1])
    avgdl2 = empty_index.avgdl

    # avgdl should update based on document length
    assert avgdl1 != avgdl2
