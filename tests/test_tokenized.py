"""
Tests for add_tokenized method in BM25Builder.
"""

import os
import tempfile
from bm25comp import BM25Builder, BM25Reader


def test_add_tokenized_basic():
    """Test basic usage of add_tokenized."""
    builder = BM25Builder()

    # Add using pre-tokenized content
    builder.add_tokenized("doc1", ["hello", "world"])
    builder.add_tokenized("doc2", ["world", "peace"])

    builder.build()

    stats = builder.get_stats()
    assert stats["num_documents"] == 2
    assert stats["num_unique_terms"] == 3  # hello, world, peace


def test_add_tokenized_vs_add():
    """Test that add_tokenized produces same results as add."""
    # Build index using add()
    builder1 = BM25Builder()
    builder1.add("doc1", "hello world")
    builder1.add("doc2", "world peace")
    builder1.build()

    # Build index using add_tokenized()
    builder2 = BM25Builder()
    builder2.add_tokenized("doc1", ["hello", "world"])
    builder2.add_tokenized("doc2", ["world", "peace"])
    builder2.build()

    # Both should have same statistics
    stats1 = builder1.get_stats()
    stats2 = builder2.get_stats()

    assert stats1["num_documents"] == stats2["num_documents"]
    assert stats1["num_unique_terms"] == stats2["num_unique_terms"]
    assert stats1["average_document_length"] == stats2["average_document_length"]


def test_add_tokenized_custom_tokenization():
    """Test using add_tokenized with custom tokenization."""
    builder = BM25Builder()

    # Custom tokenization (e.g., preserving case, splitting on punctuation)
    text = "Hello, World! How are you?"
    custom_tokens = ["Hello", "World", "How", "are", "you"]

    builder.add_tokenized("doc1", custom_tokens)
    builder.build()

    stats = builder.get_stats()
    assert stats["num_documents"] == 1
    assert stats["average_document_length"] == 5


def test_add_tokenized_empty_list():
    """Test add_tokenized with empty token list."""
    builder = BM25Builder()

    builder.add_tokenized("doc1", [])
    builder.add_tokenized("doc2", ["hello"])

    builder.build()

    stats = builder.get_stats()
    assert stats["num_documents"] == 2
    assert stats["average_document_length"] == 0.5  # (0 + 1) / 2


def test_add_tokenized_mixed_with_add():
    """Test mixing add() and add_tokenized() calls."""
    builder = BM25Builder()

    # Mix regular add and add_tokenized
    builder.add("doc1", "hello world")
    builder.add_tokenized("doc2", ["world", "peace"])
    builder.add("doc3", "hello peace")

    builder.build()

    stats = builder.get_stats()
    assert stats["num_documents"] == 3
    assert stats["num_unique_terms"] == 3  # hello, world, peace


def test_add_tokenized_round_trip():
    """Test full round-trip with add_tokenized."""
    with tempfile.NamedTemporaryFile(suffix=".bm25", delete=False) as f:
        index_path = f.name

    try:
        # Build index using add_tokenized
        builder = BM25Builder()
        builder.add_tokenized("doc1", ["machine", "learning"])
        builder.add_tokenized("doc2", ["deep", "learning"])
        builder.add_tokenized("doc3", ["machine", "vision"])
        builder.build()
        builder.save(index_path)

        # Load and search
        reader = BM25Reader()
        reader.load(index_path)

        results = reader.search("machine learning", top_k=10)
        assert len(results) > 0
        assert results[0][0] == "doc1"

    finally:
        if os.path.exists(index_path):
            os.remove(index_path)


def test_add_tokenized_duplicate_terms():
    """Test add_tokenized with duplicate terms in token list."""
    builder = BM25Builder()

    # Token list with duplicates
    builder.add_tokenized("doc1", ["hello", "hello", "world"])
    builder.build()

    # Check term frequency is counted correctly
    assert "hello" in builder.postings
    assert builder.postings["hello"][0] == (0, 2)  # doc_id=0, freq=2


def test_add_tokenized_after_build_raises_error():
    """Test that add_tokenized after build raises an error."""
    builder = BM25Builder()
    builder.add_tokenized("doc1", ["hello"])
    builder.build()

    try:
        builder.add_tokenized("doc2", ["world"])
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "after build()" in str(e)


def test_add_tokenized_preserves_case_sensitivity():
    """Test that add_tokenized respects the tokens as-is."""
    builder = BM25Builder()

    # Add tokens with different cases
    builder.add_tokenized("doc1", ["Hello", "World"])
    builder.add_tokenized("doc2", ["hello", "world"])

    builder.build()

    # Should have 4 unique terms (case-sensitive)
    stats = builder.get_stats()
    assert stats["num_unique_terms"] == 4  # Hello, World, hello, world
