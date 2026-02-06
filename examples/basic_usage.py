"""
Basic usage example for BM25Comp library.

Demonstrates:
- Building a BM25 index from documents
- Saving the index to a binary file
- Loading the index
- Searching for relevant documents
"""

from bm25comp import BM25Builder, BM25Reader


def main():
    # Sample documents
    documents = {
        "doc1": "The quick brown fox jumps over the lazy dog",
        "doc2": "Never jump over the lazy dog quickly",
        "doc3": "Bright vixens jump; dozy fowl quack",
        "doc4": "The five boxing wizards jump quickly",
        "doc5": "Jackdaws love my big sphinx of quartz",
    }

    print("=" * 60)
    print("BM25Comp Example")
    print("=" * 60)

    # Step 1: Build the index
    print("\n1. Building BM25 index...")
    builder = BM25Builder(k1=1.5, b=0.75)

    for doc_id, content in documents.items():
        builder.add(doc_id, content)
        print(f"   Added: {doc_id}")

    builder.build()
    print("   Index built successfully!")

    # Step 2: Show statistics
    stats = builder.get_stats()
    print(f"\n2. Index Statistics:")
    print(f"   Documents: {stats['num_documents']}")
    print(f"   Unique terms: {stats['num_unique_terms']}")
    print(f"   Average doc length: {stats['average_document_length']:.2f}")
    print(f"   Total postings: {stats['total_postings']}")
    print(f"   k1: {stats['k1']}, b: {stats['b']}")

    # Step 3: Save to file
    index_file = "example_index.bm25"
    print(f"\n3. Saving index to '{index_file}'...")
    builder.save(index_file)
    print("   Saved successfully!")

    # Step 4: Load the index
    print(f"\n4. Loading index from '{index_file}'...")
    reader = BM25Reader()
    reader.load(index_file)
    print("   Loaded successfully!")

    # Verify loaded stats match
    loaded_stats = reader.get_stats()
    print(
        f"   Verified: {loaded_stats['num_documents']} documents, "
        f"{loaded_stats['num_unique_terms']} terms"
    )

    # Step 5: Search examples
    print("\n5. Search Examples:")
    print("-" * 60)

    queries = [
        "quick brown fox",
        "lazy dog",
        "jump quickly",
        "sphinx quartz",
    ]

    for query in queries:
        print(f"\n   Query: '{query}'")
        results = reader.search(query, top_k=3)

        if results:
            for rank, (doc_id, score) in enumerate(results, 1):
                print(f"      {rank}. {doc_id:6s} (score: {score:.4f})")
                print(f'         "{documents[doc_id]}"')
        else:
            print("      No results found")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
