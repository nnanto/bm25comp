# BM25Comp

A space-efficient BM25 (Best Matching 25) implementation with language-agnostic binary serialization.

## Features

- **Memory-efficient**: Documents are processed incrementally, no need to keep all documents in memory
- **Space-efficient**: Keys are mapped to integers to reduce storage space
- **Language-agnostic**: Binary format can be read by implementations in any language
- **Simple API**: Easy-to-use builder and reader classes
- **No external dependencies**: Uses only Python standard library

## Installation

### Using uv (recommended)

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Install package with dev dependencies
uv pip install -e ".[dev]"
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install package
pip install -e ".[dev]"
```

### Using Make (convenient shortcuts)

```bash
make setup    # Create venv
make install  # Install package (after activating venv)
make test     # Run tests
make examples # Run all examples
```

See [SETUP.md](SETUP.md) for detailed setup instructions.

## Quick Start

### Building an Index

```python
from bm25comp import BM25Builder

# Create builder with custom parameters (optional)
builder = BM25Builder(k1=1.5, b=0.75)

# Add documents
builder.add("doc1", "the quick brown fox")
builder.add("doc2", "the lazy dog")
builder.add("doc3", "quick brown dogs")

# Build the index
builder.build()

# Save to binary file
builder.save("index.bm25")

# Get statistics
stats = builder.get_stats()
print(f"Indexed {stats['num_documents']} documents")
print(f"Found {stats['num_unique_terms']} unique terms")
```

### Custom Tokenization

Use your own tokenizer by providing pre-tokenized content:

```python
from bm25comp import BM25Builder

# Custom tokenizer function
def my_tokenizer(text):
    # Your custom tokenization logic
    tokens = text.lower().split()
    return [t for t in tokens if len(t) > 2]

builder = BM25Builder()

# Tokenize content yourself and use add_tokenized()
text = "The quick brown fox"
tokens = my_tokenizer(text)
builder.add_tokenized("doc1", tokens)

builder.build()
```

This is useful for:
- Using specialized tokenizers (NLTK, spaCy, etc.)
- Preserving case sensitivity
- Applying stemming or lemmatization
- Domain-specific tokenization rules

See [examples/custom_tokenization.py](examples/custom_tokenization.py) for more examples.

### Searching

```python
from bm25comp import BM25Reader

# Load the index
reader = BM25Reader()
reader.load("index.bm25")

# Search for documents
results = reader.search("quick dog", top_k=10)

for key, score in results:
    print(f"{key}: {score:.4f}")
```

### Custom Tokenization in Search

If you used custom tokenization when building your index, you can search with pre-tokenized query terms:

```python
from bm25comp import BM25Reader

# Load the index (built with custom tokenization)
reader = BM25Reader()
reader.load("index.bm25")

# Custom tokenizer function (should match the one used during indexing)
def my_tokenizer(text):
    tokens = text.lower().split()
    return [t for t in tokens if len(t) > 2]

# Tokenize your query using the same logic
query = "quick dog"
query_terms = my_tokenizer(query)

# Search with pre-tokenized terms
results = reader.search_tokenized(query_terms, top_k=10)

for key, score in results:
    print(f"{key}: {score:.4f}")
```

This is useful when:
- You need consistent tokenization between indexing and searching
- Using specialized tokenizers (NLTK, spaCy, etc.)
- Applying stemming or lemmatization to queries
- Working with domain-specific tokenization rules

## Binary Format Specification

The binary format is designed to be language-agnostic and consists of:

### Header
- Magic number: 4 bytes (`0x424D3235` - "BM25")
- Version: 4 bytes (unsigned int)
- k1 parameter: 4 bytes (float)
- b parameter: 4 bytes (float)
- Average document length: 4 bytes (float)
- Number of documents: 4 bytes (unsigned int)
- Number of unique terms: 4 bytes (unsigned int)

### Key Mapping Section
- Number of keys: 4 bytes (unsigned int)
- For each key:
  - Document ID: 4 bytes (unsigned int)
  - Key length: 4 bytes (unsigned int)
  - Key bytes: variable length (UTF-8 encoded)

### Document Lengths Section
- Number of documents: 4 bytes (unsigned int)
- For each document:
  - Document ID: 4 bytes (unsigned int)
  - Document length: 4 bytes (unsigned int)

### Postings Section
For each term:
- Term length: 4 bytes (unsigned int)
- Term bytes: variable length (UTF-8 encoded)
- Number of postings: 4 bytes (unsigned int)
- For each posting:
  - Document ID: 4 bytes (unsigned int)
  - Term frequency: 4 bytes (unsigned int)

All multi-byte integers and floats use network byte order (big-endian).

## How It Works

### BM25 Algorithm

BM25 (Best Matching 25) is a ranking function used to estimate the relevance of documents to a search query. The score for a document D given query Q is:

```
score(D, Q) = Σ IDF(qi) · (f(qi, D) · (k1 + 1)) / (f(qi, D) + k1 · (1 - b + b · |D| / avgdl))
```

Where:
- `f(qi, D)` = frequency of term qi in document D
- `|D|` = length of document D
- `avgdl` = average document length
- `k1` = term frequency saturation parameter (typically 1.5)
- `b` = length normalization parameter (typically 0.75)
- `IDF(qi)` = inverse document frequency of term qi

### Memory Efficiency

Documents are processed incrementally during `add()` calls:

1. Each document is tokenized immediately
2. Term frequencies and postings are computed on-the-fly
3. Only the postings data is kept in memory, not the raw text
4. After `build()`, temporary data structures are cleared

This means you can index millions of documents without keeping all raw text in memory. The builder only maintains:
- Key-to-integer mappings
- Postings lists (term → document IDs and frequencies)
- Document lengths

### Space Efficiency

Keys can be any Python object (strings, integers, tuples, etc.) and may appear multiple times in postings lists. To reduce space:

1. Each unique key is mapped to a sequential integer ID
2. Postings lists store integer IDs instead of original keys
3. A separate key mapping section allows reconstruction of original keys

This is especially beneficial when:
- Keys are long strings (URLs, file paths, etc.)
- The same documents appear in many postings lists
- You have thousands or millions of documents

## Benchmarking

Measure build, load, and query performance with your data.

### Quick Start

```bash
# Generate test data
python benchmarks/generate_sample_data.py -o benchmarks/data/test.json -n 10000

# Run benchmark
python benchmarks/run_benchmark.py benchmarks/data/test.json
```

### With Your Own Data

Convert your data to JSON format (dict of key -> token list):

```python
import json

tokenized_docs = {
    "doc1": ["token1", "token2", "token3"],
    "doc2": ["token4", "token5"],
}

with open("my_data.json", "w") as f:
    json.dump(tokenized_docs, f)
```

Then benchmark:

```bash
python benchmarks/run_benchmark.py my_data.json --queries 20 --top-k 20
```

See [benchmarks/README.md](benchmarks/README.md) for detailed documentation and usage examples.

## Development

Run tests:

```bash
pytest
```

## License

MIT
