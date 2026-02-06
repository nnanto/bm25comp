"""
Tests for BM25Comp library.
"""

import os
import tempfile
import pytest
from bm25comp import BM25Builder, BM25Reader


class TestBM25Builder:
    """Tests for BM25Builder class."""

    def test_basic_build(self):
        """Test basic index building."""
        builder = BM25Builder()
        builder.add("doc1", "the quick brown fox")
        builder.add("doc2", "the lazy dog")
        builder.build()

        stats = builder.get_stats()
        assert stats['num_documents'] == 2
        assert stats['num_unique_terms'] > 0
        assert stats['average_document_length'] > 0

    def test_key_mapping(self):
        """Test that keys are properly mapped to integers."""
        builder = BM25Builder()
        builder.add("long_key_1", "content one")
        builder.add("long_key_2", "content two")
        builder.build()

        # Check that keys are mapped to sequential integers
        assert builder.key_to_id["long_key_1"] == 0
        assert builder.key_to_id["long_key_2"] == 1
        assert builder.id_to_key[0] == "long_key_1"
        assert builder.id_to_key[1] == "long_key_2"

    def test_duplicate_keys(self):
        """Test handling of duplicate keys."""
        builder = BM25Builder()
        builder.add("doc1", "first content")
        builder.add("doc1", "second content")
        builder.build()

        # Both documents should be indexed
        stats = builder.get_stats()
        assert stats['num_documents'] == 2

        # But the key should only be mapped once
        assert len(builder.key_to_id) == 1

    def test_empty_build_raises_error(self):
        """Test that building with no documents raises an error."""
        builder = BM25Builder()
        with pytest.raises(ValueError):
            builder.build()

    def test_add_after_build_raises_error(self):
        """Test that adding documents after build raises an error."""
        builder = BM25Builder()
        builder.add("doc1", "content")
        builder.build()

        with pytest.raises(RuntimeError):
            builder.add("doc2", "more content")

    def test_double_build_raises_error(self):
        """Test that calling build twice raises an error."""
        builder = BM25Builder()
        builder.add("doc1", "content")
        builder.build()

        with pytest.raises(RuntimeError):
            builder.build()

    def test_custom_parameters(self):
        """Test custom k1 and b parameters."""
        builder = BM25Builder(k1=2.0, b=0.5)
        builder.add("doc1", "content")
        builder.build()

        stats = builder.get_stats()
        assert stats['k1'] == 2.0
        assert stats['b'] == 0.5


class TestBM25Reader:
    """Tests for BM25Reader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "test_index.bm25")

        # Create a test index
        builder = BM25Builder(k1=1.5, b=0.75)
        builder.add("doc1", "the quick brown fox")
        builder.add("doc2", "the lazy dog")
        builder.add("doc3", "quick brown dogs")
        builder.build()
        builder.save(self.index_path)

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        os.rmdir(self.temp_dir)

    def test_load_index(self):
        """Test loading an index from file."""
        reader = BM25Reader()
        reader.load(self.index_path)

        stats = reader.get_stats()
        assert stats['num_documents'] == 3
        assert stats['num_unique_terms'] > 0

    def test_search(self):
        """Test searching for documents."""
        reader = BM25Reader()
        reader.load(self.index_path)

        results = reader.search("quick brown", top_k=10)

        # Should return results
        assert len(results) > 0

        # Results should be tuples of (key, score)
        for key, score in results:
            assert isinstance(key, str)
            assert isinstance(score, float)
            assert score > 0

    def test_search_no_results(self):
        """Test searching with no matching documents."""
        reader = BM25Reader()
        reader.load(self.index_path)

        results = reader.search("nonexistent terms xyz", top_k=10)
        assert len(results) == 0

    def test_search_top_k(self):
        """Test that top_k limits results."""
        reader = BM25Reader()
        reader.load(self.index_path)

        results = reader.search("the", top_k=2)
        assert len(results) <= 2

    def test_search_before_load_raises_error(self):
        """Test that searching before loading raises an error."""
        reader = BM25Reader()
        with pytest.raises(RuntimeError):
            reader.search("query")

    def test_score_document(self):
        """Test scoring a specific document."""
        reader = BM25Reader()
        reader.load(self.index_path)

        # Get a valid document ID
        doc_id = 0  # First document

        score = reader.score_document("quick brown", doc_id)
        assert isinstance(score, float)
        assert score >= 0

    def test_parameters_preserved(self):
        """Test that k1 and b parameters are preserved after save/load."""
        reader = BM25Reader()
        reader.load(self.index_path)

        stats = reader.get_stats()
        assert stats['k1'] == 1.5
        assert stats['b'] == 0.75


class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_round_trip(self):
        """Test building, saving, loading, and searching."""
        with tempfile.NamedTemporaryFile(suffix=".bm25", delete=False) as f:
            index_path = f.name

        try:
            # Build
            builder = BM25Builder()
            builder.add("doc1", "machine learning algorithms")
            builder.add("doc2", "deep learning neural networks")
            builder.add("doc3", "machine vision systems")
            builder.build()
            builder.save(index_path)

            # Load
            reader = BM25Reader()
            reader.load(index_path)

            # Search
            results = reader.search("machine learning", top_k=10)

            # Verify
            assert len(results) > 0
            # doc1 should score highest (has both terms)
            assert results[0][0] == "doc1"

        finally:
            if os.path.exists(index_path):
                os.remove(index_path)

    def test_large_keys(self):
        """Test with large keys (URLs, paths, etc.)."""
        with tempfile.NamedTemporaryFile(suffix=".bm25", delete=False) as f:
            index_path = f.name

        try:
            # Build with long keys
            builder = BM25Builder()
            builder.add(
                "https://example.com/articles/2024/01/15/very-long-url-path",
                "article content here"
            )
            builder.add(
                "/var/log/system/application/production/server-01/access.log",
                "log entries here"
            )
            builder.build()
            builder.save(index_path)

            # Load and search
            reader = BM25Reader()
            reader.load(index_path)
            results = reader.search("article", top_k=10)

            # Verify original keys are preserved
            assert len(results) > 0
            assert results[0][0].startswith("https://")

        finally:
            if os.path.exists(index_path):
                os.remove(index_path)
