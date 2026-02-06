#!/usr/bin/env python3
"""
Generate sample JSON data for benchmarking.

Creates synthetic tokenized documents in the format:
{
    "doc_id": ["token1", "token2", ...],
    ...
}
"""

import argparse
import json
import random
import sys


def generate_vocabulary(size: int) -> list[str]:
    """Generate a vocabulary of random words."""
    # Common word patterns for more realistic data
    prefixes = ['pre', 'post', 'anti', 'pro', 'sub', 'super', 'trans', 'inter']
    roots = ['test', 'data', 'info', 'code', 'file', 'word', 'text', 'doc',
             'system', 'process', 'service', 'model', 'user', 'event']
    suffixes = ['ing', 'ed', 's', 'er', 'tion', 'ment', 'ness', 'ly', 'ize']

    vocab = set()

    # Generate words
    while len(vocab) < size:
        # Simple words
        if random.random() < 0.3:
            word = random.choice(roots)
        # Words with prefixes
        elif random.random() < 0.5:
            word = random.choice(prefixes) + random.choice(roots)
        # Words with suffixes
        elif random.random() < 0.7:
            word = random.choice(roots) + random.choice(suffixes)
        # Complex words
        else:
            word = random.choice(prefixes) + random.choice(roots) + random.choice(suffixes)

        vocab.add(word)

    return list(vocab)


def generate_document(vocab: list[str], min_length: int, max_length: int) -> list[str]:
    """Generate a single document with random tokens from vocabulary."""
    length = random.randint(min_length, max_length)

    # Use Zipfian distribution for more realistic word frequencies
    # More frequent words appear more often
    doc = []
    for _ in range(length):
        # Zipfian-like selection: earlier words in vocab are more likely
        idx = int(random.paretovariate(1.5) - 1)
        if idx < len(vocab):
            doc.append(vocab[idx])
        else:
            doc.append(random.choice(vocab))

    return doc


def generate_dataset(num_docs: int, vocab_size: int,
                     min_doc_length: int, max_doc_length: int) -> dict[str, list[str]]:
    """Generate a complete dataset."""
    print(f"Generating vocabulary of {vocab_size:,} words...")
    vocab = generate_vocabulary(vocab_size)

    print(f"Generating {num_docs:,} documents...")
    dataset = {}

    progress_interval = max(1, num_docs // 20)
    for i in range(num_docs):
        doc_id = f"doc_{i:08d}"
        dataset[doc_id] = generate_document(vocab, min_doc_length, max_doc_length)

        if (i + 1) % progress_interval == 0:
            print(f"  Generated {i + 1:,}/{num_docs:,} documents...")

    return dataset


def print_dataset_stats(dataset: dict[str, list[str]]):
    """Print statistics about the generated dataset."""
    num_docs = len(dataset)
    all_tokens = [token for doc in dataset.values() for token in doc]
    total_tokens = len(all_tokens)
    unique_tokens = len(set(all_tokens))
    avg_doc_length = total_tokens / num_docs if num_docs > 0 else 0

    doc_lengths = [len(doc) for doc in dataset.values()]
    min_length = min(doc_lengths) if doc_lengths else 0
    max_length = max(doc_lengths) if doc_lengths else 0

    print("\nDataset Statistics:")
    print(f"  Documents: {num_docs:,}")
    print(f"  Total tokens: {total_tokens:,}")
    print(f"  Unique tokens: {unique_tokens:,}")
    print(f"  Average doc length: {avg_doc_length:.2f}")
    print(f"  Min doc length: {min_length}")
    print(f"  Max doc length: {max_length}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate sample tokenized JSON data for BM25 benchmarking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Small dataset (good for quick tests)
  python benchmarks/generate_sample_data.py -o data/small.json -n 100

  # Medium dataset
  python benchmarks/generate_sample_data.py -o data/medium.json -n 10000

  # Large dataset
  python benchmarks/generate_sample_data.py -o data/large.json -n 100000 -v 10000
        """
    )

    parser.add_argument('-o', '--output', required=True,
                        help='Output JSON file path')
    parser.add_argument('-n', '--num-docs', type=int, default=1000,
                        help='Number of documents to generate (default: 1000)')
    parser.add_argument('-v', '--vocab-size', type=int, default=1000,
                        help='Vocabulary size (default: 1000)')
    parser.add_argument('--min-length', type=int, default=10,
                        help='Minimum document length in tokens (default: 10)')
    parser.add_argument('--max-length', type=int, default=100,
                        help='Maximum document length in tokens (default: 100)')
    parser.add_argument('--seed', type=int,
                        help='Random seed for reproducibility')
    parser.add_argument('--pretty', action='store_true',
                        help='Pretty-print JSON output (larger file size)')

    args = parser.parse_args()

    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")

    # Validate arguments
    if args.num_docs <= 0:
        print("Error: Number of documents must be positive")
        sys.exit(1)

    if args.vocab_size <= 0:
        print("Error: Vocabulary size must be positive")
        sys.exit(1)

    if args.min_length <= 0 or args.max_length <= 0:
        print("Error: Document lengths must be positive")
        sys.exit(1)

    if args.min_length > args.max_length:
        print("Error: Minimum length cannot be greater than maximum length")
        sys.exit(1)

    # Generate dataset
    print("="*70)
    print("GENERATING SAMPLE DATA")
    print("="*70)
    print()

    dataset = generate_dataset(
        args.num_docs,
        args.vocab_size,
        args.min_length,
        args.max_length
    )

    # Print statistics
    print_dataset_stats(dataset)

    # Save to file
    print(f"\nSaving to: {args.output}")
    with open(args.output, 'w', encoding='utf-8') as f:
        if args.pretty:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        else:
            json.dump(dataset, f, ensure_ascii=False)

    file_size = len(json.dumps(dataset))
    print(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
