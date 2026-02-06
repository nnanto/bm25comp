"""
Example demonstrating custom tokenization with add_tokenized().

Shows how to use your own tokenizer instead of the default one.
"""

import re
from bm25comp import BM25Builder, BM25Reader


def custom_tokenizer(text: str) -> list[str]:
    """
    Custom tokenizer that:
    - Preserves case
    - Removes punctuation
    - Splits on whitespace
    - Filters out very short tokens
    """
    # Remove punctuation but keep alphanumeric and spaces
    text = re.sub(r"[^\w\s]", "", text)

    # Split on whitespace
    tokens = text.split()

    # Filter out tokens shorter than 2 characters
    tokens = [t for t in tokens if len(t) >= 2]

    return tokens


def stemming_tokenizer(text: str) -> list[str]:
    """
    Simple stemming tokenizer (naive implementation for demo).
    In production, use a real stemmer like Porter or Snowball.
    """
    text = text.lower()
    tokens = text.split()

    # Very naive "stemming" - just remove common suffixes
    stemmed = []
    for token in tokens:
        # Remove 'ing', 'ed', 's'
        if token.endswith("ing"):
            token = token[:-3]
        elif token.endswith("ed"):
            token = token[:-2]
        elif token.endswith("s") and len(token) > 3:
            token = token[:-1]
        stemmed.append(token)

    return stemmed


def main():
    print("=" * 70)
    print("Custom Tokenization Example")
    print("=" * 70)

    documents = {
        "doc1": "The Quick Brown Fox jumps over the lazy dog!",
        "doc2": "Python is a programming language.",
        "doc3": "Machine Learning and AI are transforming technology.",
        "doc4": "The quick fox ran quickly through the forest.",
    }

    # Example 1: Default tokenization
    print("\n1. Default Tokenization (built-in)")
    print("-" * 70)

    builder1 = BM25Builder()
    for key, content in documents.items():
        builder1.add(key, content)
    builder1.build()

    stats1 = builder1.get_stats()
    print(f"   Unique terms: {stats1['num_unique_terms']}")
    print(f"   Sample terms: {list(builder1.postings.keys())[:10]}")

    # Example 2: Custom tokenization (case-preserving)
    print("\n2. Custom Tokenization (case-preserving, no punctuation)")
    print("-" * 70)

    builder2 = BM25Builder()
    for key, content in documents.items():
        tokens = custom_tokenizer(content)
        print(f"   {key}: {tokens[:5]}...")
        builder2.add_tokenized(key, tokens)
    builder2.build()

    stats2 = builder2.get_stats()
    print(f"   Unique terms: {stats2['num_unique_terms']}")
    print(f"   Sample terms: {list(builder2.postings.keys())[:10]}")

    # Example 3: Stemming tokenization
    print("\n3. Stemming Tokenization (naive stemming)")
    print("-" * 70)

    builder3 = BM25Builder()
    for key, content in documents.items():
        tokens = stemming_tokenizer(content)
        print(f"   {key}: {tokens[:5]}...")
        builder3.add_tokenized(key, tokens)
    builder3.build()

    stats3 = builder3.get_stats()
    print(f"   Unique terms: {stats3['num_unique_terms']}")
    print(f"   Sample terms: {list(builder3.postings.keys())[:10]}")

    # Example 4: Search comparison
    print("\n4. Search Comparison")
    print("-" * 70)

    # Save all indices
    builder1.save("index_default.bm25")
    builder2.save("index_custom.bm25")
    builder3.save("index_stemmed.bm25")

    query = "quick"
    print(f"   Query: '{query}'")

    # Search with default tokenization
    reader1 = BM25Reader()
    reader1.load("index_default.bm25")
    results1 = reader1.search(query, top_k=3)
    print(f"\n   Default tokenization results:")
    for key, score in results1:
        print(f"      {key}: {score:.4f}")

    # Search with custom tokenization
    reader2 = BM25Reader()
    reader2.load("index_custom.bm25")
    # Need to tokenize query the same way!
    query_tokens = custom_tokenizer(query)
    results2 = reader2.search(" ".join(query_tokens), top_k=3)
    print(f"\n   Custom tokenization results:")
    for key, score in results2:
        print(f"      {key}: {score:.4f}")

    # Search with stemming
    reader3 = BM25Reader()
    reader3.load("index_stemmed.bm25")
    query_tokens = stemming_tokenizer(query)
    results3 = reader3.search(" ".join(query_tokens), top_k=3)
    print(f"\n   Stemmed tokenization results:")
    for key, score in results3:
        print(f"      {key}: {score:.4f}")

    print("\n" + "=" * 70)
    print("Key Takeaways:")
    print("  • add_tokenized() lets you use any tokenizer you want")
    print("  • Remember to tokenize queries the same way as documents")
    print("  • Custom tokenization can improve search quality for your domain")
    print("  • Case-sensitive tokens create more unique terms")
    print("  • Stemming reduces unique terms and improves recall")
    print("=" * 70)

    # Cleanup
    import os

    os.remove("index_default.bm25")
    os.remove("index_custom.bm25")
    os.remove("index_stemmed.bm25")


if __name__ == "__main__":
    main()
