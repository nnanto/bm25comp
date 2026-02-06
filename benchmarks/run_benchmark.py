#!/usr/bin/env python3
"""
Benchmark script for BM25Comp library.

Usage:
    python benchmarks/run_benchmark.py <json_file_path>

JSON format:
    {
        "doc1": ["token1", "token2", "token3"],
        "doc2": ["token4", "token5"],
        ...
    }
"""

import argparse
import json
import os
import sys
import time
import tempfile
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bm25comp import BM25Builder, BM25Reader


def load_json_data(file_path: str) -> Dict[str, List[str]]:
    """Load tokenized documents from JSON file."""
    print(f"Loading data from: {file_path}")
    start = time.time()

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    load_time = time.time() - start

    # Validate format
    if not isinstance(data, dict):
        raise ValueError("JSON must be a dictionary")

    for key, value in data.items():
        if not isinstance(value, list):
            raise ValueError(f"Value for key '{key}' must be a list")
        if not all(isinstance(token, str) for token in value):
            raise ValueError(f"All tokens for key '{key}' must be strings")

    print(f"✓ Loaded {len(data):,} documents in {load_time:.3f}s")
    return data


def benchmark_build(data: Dict[str, List[str]], output_path: str) -> Tuple[float, int]:
    """
    Build BM25 index and measure time and output size.

    Returns:
        (build_time, file_size)
    """
    print("\n" + "="*70)
    print("BUILDING BM25 INDEX")
    print("="*70)

    # Count statistics
    total_tokens = sum(len(tokens) for tokens in data.values())
    avg_doc_length = total_tokens / len(data) if data else 0
    unique_tokens = len(set(token for tokens in data.values() for token in tokens))

    print(f"Documents: {len(data):,}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Average doc length: {avg_doc_length:.2f}")
    print(f"Unique tokens: {unique_tokens:,}")

    # Build index
    print("\nBuilding index...")
    start = time.time()

    builder = BM25Builder(k1=1.5, b=0.75)

    # Track progress for large datasets
    progress_interval = max(1, len(data) // 10)
    for i, (key, tokens) in enumerate(data.items(), 1):
        builder.add_tokenized(key, tokens)
        if i % progress_interval == 0:
            print(f"  Processed {i:,}/{len(data):,} documents...")

    builder.build()
    build_time = time.time() - start

    # Save to file
    print("\nSaving index...")
    save_start = time.time()
    builder.save(output_path)
    save_time = time.time() - save_start

    file_size = os.path.getsize(output_path)

    # Get stats
    stats = builder.get_stats()

    print(f"\n✓ Build complete!")
    print(f"  Build time: {build_time:.3f}s")
    print(f"  Save time: {save_time:.3f}s")
    print(f"  Total time: {build_time + save_time:.3f}s")
    print(f"  Output size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print(f"  Unique terms: {stats['num_unique_terms']:,}")
    print(f"  Total postings: {stats['total_postings']:,}")

    return build_time + save_time, file_size


def benchmark_load(index_path: str) -> Tuple[float, BM25Reader]:
    """
    Load BM25 index and measure time.

    Returns:
        (load_time, reader)
    """
    print("\n" + "="*70)
    print("LOADING BM25 INDEX")
    print("="*70)

    print(f"Loading index from: {index_path}")
    start = time.time()

    reader = BM25Reader()
    reader.load(index_path)

    load_time = time.time() - start

    stats = reader.get_stats()

    print(f"\n✓ Load complete!")
    print(f"  Load time: {load_time:.3f}s")
    print(f"  Documents: {stats['num_documents']:,}")
    print(f"  Unique terms: {stats['num_unique_terms']:,}")
    print(f"  Average doc length: {stats['average_document_length']:.2f}")

    return load_time, reader


def benchmark_queries(reader: BM25Reader, queries: List[str], top_k: int = 10) -> List[Tuple[str, float, List]]:
    """
    Run queries and measure time.

    Returns:
        List of (query, query_time, results)
    """
    print("\n" + "="*70)
    print("RUNNING QUERIES")
    print("="*70)

    results = []
    total_time = 0

    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}/{len(queries)}: '{query}'")

        start = time.time()
        search_results = reader.search(query, top_k=top_k)
        query_time = time.time() - start

        total_time += query_time

        print(f"  Time: {query_time*1000:.2f}ms")
        print(f"  Results: {len(search_results)}")

        if search_results:
            print(f"  Top result: {search_results[0][0]} (score: {search_results[0][1]:.4f})")

        results.append((query, query_time, search_results))

    avg_time = total_time / len(queries) if queries else 0

    print(f"\n✓ Queries complete!")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Average time: {avg_time*1000:.2f}ms per query")
    print(f"  Throughput: {len(queries)/total_time:.2f} queries/second")

    return results


def generate_sample_queries(data: Dict[str, List[str]], num_queries: int = 10) -> List[str]:
    """Generate sample queries from the data."""
    import random

    # Get some random tokens from the data
    all_tokens = []
    for tokens in data.values():
        all_tokens.extend(tokens)

    if not all_tokens:
        return ["test query"]

    # Remove duplicates
    unique_tokens = list(set(all_tokens))

    queries = []
    for _ in range(min(num_queries, len(unique_tokens))):
        # Generate queries of varying lengths (1-3 tokens)
        query_length = random.randint(1, min(3, len(unique_tokens)))
        query_tokens = random.sample(unique_tokens, query_length)
        queries.append(" ".join(query_tokens))

    return queries


def print_summary(build_time: float, file_size: int, load_time: float,
                  query_times: List[float], num_docs: int):
    """Print final summary."""
    print("\n" + "="*70)
    print("BENCHMARK SUMMARY")
    print("="*70)

    print(f"\nDataset:")
    print(f"  Documents: {num_docs:,}")

    print(f"\nBuild Performance:")
    print(f"  Time: {build_time:.3f}s")
    print(f"  Throughput: {num_docs/build_time:.2f} docs/second")
    print(f"  Output size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print(f"  Size per doc: {file_size/num_docs:.2f} bytes")

    print(f"\nLoad Performance:")
    print(f"  Time: {load_time:.3f}s")
    print(f"  Throughput: {num_docs/load_time:.2f} docs/second")

    if query_times:
        avg_query_time = sum(query_times) / len(query_times)
        min_query_time = min(query_times)
        max_query_time = max(query_times)

        print(f"\nQuery Performance:")
        print(f"  Queries run: {len(query_times)}")
        print(f"  Average time: {avg_query_time*1000:.2f}ms")
        print(f"  Min time: {min_query_time*1000:.2f}ms")
        print(f"  Max time: {max_query_time*1000:.2f}ms")
        print(f"  Throughput: {1/avg_query_time:.2f} queries/second")

    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark BM25Comp library with tokenized JSON data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
JSON Format:
  {
    "doc1": ["token1", "token2", "token3"],
    "doc2": ["token4", "token5"],
    ...
  }

Example:
  python benchmarks/run_benchmark.py data/sample.json
  python benchmarks/run_benchmark.py data/large.json --queries 20 --top-k 20
        """
    )

    parser.add_argument('json_file', help='Path to JSON file with tokenized documents')
    parser.add_argument('--output', '-o', help='Output path for index file (default: temp file)')
    parser.add_argument('--queries', '-q', type=int, default=10,
                        help='Number of sample queries to run (default: 10)')
    parser.add_argument('--top-k', '-k', type=int, default=10,
                        help='Number of results per query (default: 10)')
    parser.add_argument('--keep-index', action='store_true',
                        help='Keep the generated index file after benchmarking')

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.json_file):
        print(f"Error: File not found: {args.json_file}")
        sys.exit(1)

    # Set output path
    if args.output:
        index_path = args.output
        cleanup = not args.keep_index
    else:
        temp_file = tempfile.NamedTemporaryFile(suffix='.bm25', delete=False)
        index_path = temp_file.name
        temp_file.close()
        cleanup = True

    try:
        # Load data
        data = load_json_data(args.json_file)

        if not data:
            print("Error: No data loaded from JSON file")
            sys.exit(1)

        # Benchmark build
        build_time, file_size = benchmark_build(data, index_path)

        # Benchmark load
        load_time, reader = benchmark_load(index_path)

        # Generate sample queries
        print("\nGenerating sample queries...")
        queries = generate_sample_queries(data, args.queries)
        print(f"Generated {len(queries)} queries")

        # Benchmark queries
        query_results = benchmark_queries(reader, queries, args.top_k)
        query_times = [qr[1] for qr in query_results]

        # Print summary
        print_summary(build_time, file_size, load_time, query_times, len(data))

        if not cleanup:
            print(f"\nIndex saved to: {index_path}")

    finally:
        # Cleanup
        if cleanup and os.path.exists(index_path):
            os.remove(index_path)
            print(f"\nCleaned up temporary index file")


if __name__ == "__main__":
    main()
