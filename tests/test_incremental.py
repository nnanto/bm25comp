"""
Tests for incremental document processing in BM25Builder.
"""

import os
import tempfile
from bm25comp import BM25Builder, BM25Reader


def test_incremental_processing():
    """Test that documents are processed incrementally without storage."""
    builder = BM25Builder()

    # Add documents
    builder.add("doc1", "hello world")
    builder.add("doc2", "world peace")

    # Verify intermediate state (before build)
    assert builder.num_docs == 2
    assert builder.doc_lengths[0] == 2  # "hello world"
    assert builder.doc_lengths[1] == 2  # "world peace"
    assert builder.total_length == 4

    # Build
    builder.build()

    # Verify final state
    stats = builder.get_stats()
    assert stats['num_documents'] == 2
    assert stats['average_document_length'] == 2.0
    assert stats['num_unique_terms'] == 3  # hello, world, peace


def test_duplicate_keys_with_incremental():
    """Test that duplicate keys are handled correctly with incremental processing."""
    builder = BM25Builder()

    # Add documents with duplicate keys
    builder.add("doc1", "first content")
    builder.add("doc1", "second content")
    builder.add("doc2", "third content")

    # Should have 3 documents
    assert builder.num_docs == 3

    # But only 2 unique keys
    assert len(builder.key_to_id) == 2
    assert len(builder.id_to_key) == 2

    builder.build()

    stats = builder.get_stats()
    assert stats['num_documents'] == 3


def test_no_document_storage():
    """Test that documents are not stored after being processed."""
    builder = BM25Builder()

    builder.add("doc1", "some content")
    builder.add("doc2", "more content")

    # Verify that we don't have a 'documents' attribute storing raw text
    assert not hasattr(builder, 'documents')

    builder.build()

    # After build, temp_postings should be cleared
    assert len(builder.temp_postings) == 0


def test_round_trip_with_incremental():
    """Test full round-trip with incremental processing."""
    with tempfile.NamedTemporaryFile(suffix=".bm25", delete=False) as f:
        index_path = f.name

    try:
        # Build index
        builder = BM25Builder()
        builder.add("doc1", "machine learning algorithms")
        builder.add("doc2", "deep learning neural networks")
        builder.add("doc3", "machine vision systems")
        builder.build()
        builder.save(index_path)

        # Load and verify
        reader = BM25Reader()
        reader.load(index_path)

        results = reader.search("machine learning", top_k=10)
        assert len(results) > 0
        assert results[0][0] == "doc1"

    finally:
        if os.path.exists(index_path):
            os.remove(index_path)


def test_large_batch_incremental():
    """Test incremental processing with a large batch of documents."""
    builder = BM25Builder()

    num_docs = 100
    for i in range(num_docs):
        builder.add(f"doc_{i}", f"content with some words {i % 10}")

    # Verify counts before build
    assert builder.num_docs == num_docs
    assert len(builder.doc_lengths) == num_docs

    builder.build()

    # Verify after build
    stats = builder.get_stats()
    assert stats['num_documents'] == num_docs
    assert stats['num_unique_terms'] > 0
    assert len(builder.temp_postings) == 0  # Should be cleared
