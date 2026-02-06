"""
Example demonstrating memory efficiency through incremental processing.

This example shows how BM25Comp saves memory by processing documents
incrementally during add() instead of storing them in a list.
"""

import sys
from bm25comp import BM25Builder


def get_size_mb(obj):
    """Get approximate size of object in MB."""
    return sys.getsizeof(obj) / (1024 * 1024)


def main():
    print("=" * 70)
    print("BM25Comp Memory Efficiency Example")
    print("=" * 70)

    # Create large documents to demonstrate memory savings
    print("\n1. Creating test data...")
    num_docs = 1000
    doc_size_chars = 1000  # 1KB per document

    # Generate sample text
    sample_text = " ".join([f"word{i % 100}" for i in range(doc_size_chars // 10)])

    print(f"   Number of documents: {num_docs:,}")
    print(f"   Approximate size per document: {len(sample_text)} bytes")
    print(f"   Total raw text size: ~{(len(sample_text) * num_docs) / (1024 * 1024):.2f} MB")

    # Build index
    print("\n2. Building index incrementally...")
    builder = BM25Builder(k1=1.5, b=0.75)

    for i in range(num_docs):
        key = f"doc_{i:05d}"
        builder.add(key, sample_text)

        if (i + 1) % 250 == 0:
            print(f"   Processed {i + 1:,} documents...")

    builder.build()
    print("   Index built successfully!")

    # Calculate memory usage
    print("\n3. Memory Analysis:")

    # Estimate memory if we stored all documents
    # Each document: (key string ~10 bytes, content ~1000 bytes) = ~1010 bytes
    estimated_with_storage = (len(sample_text) + 20) * num_docs / (1024 * 1024)

    # Actual memory: postings + doc_lengths + key_mapping
    stats = builder.get_stats()

    # Rough estimates (not exact, but illustrative)
    postings_size = stats['total_postings'] * 8  # doc_id (4) + freq (4)
    doc_lengths_size = stats['num_documents'] * 8  # doc_id (4) + length (4)
    key_mapping_size = stats['num_documents'] * 20  # rough estimate for key storage

    actual_size_mb = (postings_size + doc_lengths_size + key_mapping_size) / (1024 * 1024)

    print(f"   If we stored documents: ~{estimated_with_storage:.2f} MB")
    print(f"   Actual index size: ~{actual_size_mb:.2f} MB")
    print(f"   Memory saved: ~{estimated_with_storage - actual_size_mb:.2f} MB")
    print(f"   Reduction: {((estimated_with_storage - actual_size_mb) / estimated_with_storage * 100):.1f}%")

    print(f"\n4. Index Statistics:")
    print(f"   Documents indexed: {stats['num_documents']:,}")
    print(f"   Unique terms: {stats['num_unique_terms']:,}")
    print(f"   Total postings: {stats['total_postings']:,}")
    print(f"   Average document length: {stats['average_document_length']:.2f}")

    print("\n" + "=" * 70)
    print("Key Takeaway:")
    print("  By processing documents incrementally during add() instead of")
    print("  storing them, we avoid holding all raw text in memory.")
    print("  The builder only keeps the computed postings and statistics!")
    print("=" * 70)


if __name__ == "__main__":
    main()
