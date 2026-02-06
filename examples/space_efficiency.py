"""
Example demonstrating space efficiency through integer key mapping.

This example shows how BM25Comp saves space by mapping long keys
(like URLs or file paths) to compact integer IDs.
"""

import os
from bm25comp import BM25Builder


def main():
    print("=" * 70)
    print("BM25Comp Space Efficiency Example")
    print("=" * 70)

    # Simulate documents with long keys (e.g., URLs or file paths)
    documents = {
        "https://example.com/articles/2024/01/15/introduction-to-machine-learning":
            "machine learning introduction tutorial basics",

        "https://example.com/articles/2024/01/16/deep-learning-fundamentals":
            "deep learning neural networks fundamentals",

        "https://example.com/articles/2024/01/17/natural-language-processing-guide":
            "natural language processing nlp guide tutorial",

        "https://example.com/articles/2024/01/18/computer-vision-basics":
            "computer vision image processing basics",

        "https://example.com/articles/2024/01/19/reinforcement-learning-intro":
            "reinforcement learning agents rewards intro",

        "/var/log/system/application/production/server-01/access-2024-01-15.log":
            "server access log entries production system",

        "/var/log/system/application/production/server-01/error-2024-01-15.log":
            "error log entries production server system",

        "/var/log/system/application/staging/server-02/access-2024-01-15.log":
            "staging server access log system entries",
    }

    print(f"\n1. Document Keys Analysis:")
    print(f"   Number of documents: {len(documents)}")

    total_key_length = sum(len(key) for key in documents.keys())
    avg_key_length = total_key_length / len(documents)

    print(f"   Total key characters: {total_key_length}")
    print(f"   Average key length: {avg_key_length:.1f} characters")
    print(f"   Longest key: {max(len(k) for k in documents.keys())} characters")
    print(f"   Shortest key: {min(len(k) for k in documents.keys())} characters")

    # Build index
    print(f"\n2. Building index...")
    builder = BM25Builder(k1=1.5, b=0.75)

    for key, content in documents.items():
        builder.add(key, content)

    builder.build()
    print("   Index built successfully!")

    # Save to file
    index_file = "space_efficiency_index.bm25"
    builder.save(index_file)

    file_size = os.path.getsize(index_file)
    print(f"\n3. Storage Analysis:")
    print(f"   Index file: {index_file}")
    print(f"   File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")

    # Calculate savings
    stats = builder.get_stats()

    # Estimate space if we stored full keys in postings
    # Each posting would need: key_bytes + 4 bytes (term_freq)
    estimated_uncompressed = 0
    for term, postings_list in builder.postings.items():
        for doc_id, freq in postings_list:
            original_key = builder.id_to_key[doc_id]
            # UTF-8 encoding + term freq as 4 bytes
            estimated_uncompressed += len(original_key.encode('utf-8')) + 4

    # Actual space used in postings: doc_id (4 bytes) + freq (4 bytes)
    actual_postings_space = stats['total_postings'] * 8

    # Add the key mapping overhead (stored once)
    key_mapping_overhead = sum(
        4 +  # doc_id
        4 +  # key_length
        len(str(key).encode('utf-8'))  # key_bytes
        for key in documents.keys()
    )

    actual_with_mapping = actual_postings_space + key_mapping_overhead
    space_saved = estimated_uncompressed - actual_with_mapping
    savings_pct = (space_saved / estimated_uncompressed) * 100 if estimated_uncompressed > 0 else 0

    print(f"\n4. Space Savings (Postings Data Only):")
    print(f"   Without integer mapping: ~{estimated_uncompressed:,} bytes")
    print(f"   With integer mapping: ~{actual_with_mapping:,} bytes")
    print(f"   Space saved: ~{space_saved:,} bytes ({savings_pct:.1f}%)")
    print(f"   Key mapping overhead: {key_mapping_overhead:,} bytes")

    print(f"\n5. Efficiency Gains:")
    print(f"   Average key length: {avg_key_length:.1f} characters")
    print(f"   Integer ID size: 4 bytes")
    print(f"   Compression ratio: {avg_key_length / 4:.2f}x per posting")
    print(f"   Total postings: {stats['total_postings']}")

    print("\n" + "=" * 70)
    print("Key Takeaway:")
    print(f"  By mapping keys to integers, we save ~{savings_pct:.1f}% of space")
    print(f"  in postings data, with only a small one-time key mapping overhead.")
    print("=" * 70)


if __name__ == "__main__":
    main()
