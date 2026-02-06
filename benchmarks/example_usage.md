# Benchmarking Examples

## Example 1: Quick Benchmark with Sample Data

```bash
# Using make
make benchmark

# Or directly
python benchmarks/run_benchmark.py benchmarks/data/sample.json
```

## Example 2: Generate and Benchmark Custom Dataset

```bash
# Generate 10,000 documents
python benchmarks/generate_sample_data.py \
  -o benchmarks/data/my_test.json \
  -n 10000 \
  -v 1000 \
  --seed 42

# Benchmark it
python benchmarks/run_benchmark.py benchmarks/data/my_test.json \
  --queries 50 \
  --top-k 20
```

## Example 3: Benchmark with Your Own Data

### Option A: Create JSON Directly

```python
import json

# Your documents (already tokenized)
documents = {
    "doc_001": ["natural", "language", "processing"],
    "doc_002": ["machine", "learning", "algorithms"],
    "doc_003": ["deep", "neural", "networks"],
}

# Save to JSON
with open("my_data.json", "w") as f:
    json.dump(documents, f)
```

Then run:
```bash
python benchmarks/run_benchmark.py my_data.json
```

### Option B: Convert from Text File

If you have a text file with one document per line:

```bash
# Convert to benchmark format
python benchmarks/convert_to_benchmark_format.py \
  --input documents.txt \
  --output benchmark.json \
  --format text

# Run benchmark
python benchmarks/run_benchmark.py benchmark.json
```

### Option C: Convert from CSV

If you have CSV data:

```bash
# Convert CSV to benchmark format
python benchmarks/convert_to_benchmark_format.py \
  --input data.csv \
  --output benchmark.json \
  --format csv \
  --id-column doc_id \
  --text-column content

# Run benchmark
python benchmarks/run_benchmark.py benchmark.json
```

## Example 4: Save and Reuse Index

```bash
# Benchmark and keep the index
python benchmarks/run_benchmark.py data.json \
  --output my_index.bm25 \
  --keep-index

# The index is now saved and can be used in your application
python -c "
from bm25comp import BM25Reader
reader = BM25Reader()
reader.load('my_index.bm25')
results = reader.search('query terms', top_k=10)
print(results)
"
```

## Example 5: Large Scale Benchmark

```bash
# Generate large dataset
python benchmarks/generate_sample_data.py \
  -o benchmarks/data/large.json \
  -n 100000 \
  -v 10000 \
  --max-length 200

# Benchmark with extensive queries
python benchmarks/run_benchmark.py benchmarks/data/large.json \
  --queries 100 \
  --top-k 50 \
  --output large_index.bm25 \
  --keep-index
```

## Example 6: Convert Existing BM25 Data

If you have data in another format, convert it to benchmark format:

```python
import json

# Example: Convert from your existing format
your_data = [
    {"id": "1", "title": "Doc 1", "content": "some text here"},
    {"id": "2", "title": "Doc 2", "content": "more text"},
]

# Convert to benchmark format
def tokenize(text):
    return text.lower().split()

benchmark_data = {
    item["id"]: tokenize(item["title"] + " " + item["content"])
    for item in your_data
}

# Save
with open("converted.json", "w") as f:
    json.dump(benchmark_data, f)
```

Then benchmark:
```bash
python benchmarks/run_benchmark.py converted.json
```

## Example 7: Reproducible Benchmarks

For consistent results across runs:

```bash
# Generate with seed
python benchmarks/generate_sample_data.py \
  -o benchmarks/data/reproducible.json \
  -n 5000 \
  --seed 12345

# Results will be identical on every run
python benchmarks/run_benchmark.py benchmarks/data/reproducible.json
```

## Example 8: Custom Tokenization

```python
import json
import re

# Your custom tokenizer
def custom_tokenizer(text):
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Split and lowercase
    tokens = text.lower().split()
    # Filter short tokens
    return [t for t in tokens if len(t) > 2]

# Your documents
documents = {
    "doc1": "Hello, World! How are you?",
    "doc2": "Python is great for NLP.",
}

# Tokenize
benchmark_data = {
    doc_id: custom_tokenizer(text)
    for doc_id, text in documents.items()
}

# Save
with open("custom_tokenized.json", "w") as f:
    json.dump(benchmark_data, f)
```

Benchmark:
```bash
python benchmarks/run_benchmark.py custom_tokenized.json
```

## Tips

1. **Start Small**: Test with small datasets first (100-1000 docs)
2. **Realistic Data**: Use representative vocabulary and document lengths
3. **Multiple Runs**: Average results from multiple runs for accuracy
4. **System Load**: Close other applications during benchmarking
5. **Query Types**: Test with queries similar to your use case

## Interpreting Results

**Good Performance:**
- Build: > 10,000 docs/second
- Load: > 50,000 docs/second
- Query: < 10ms per query

**Needs Investigation:**
- Build: < 1,000 docs/second
- Load: < 10,000 docs/second
- Query: > 100ms per query

**Index Size:**
- Typical: 100-500 bytes per document
- Large: > 1KB per document (many unique terms)
- Small: < 50 bytes per document (short docs or small vocab)
