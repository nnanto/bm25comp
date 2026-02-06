# BM25Comp Benchmarks

Benchmarking tools for measuring BM25Comp performance.

## Overview

This directory contains scripts for:
- **Generating** synthetic test data
- **Benchmarking** build, load, and query performance
- **Analyzing** index size and throughput

## Quick Start

### 1. Generate Sample Data

Create a test dataset:

```bash
# Small dataset (100 documents)
python benchmarks/generate_sample_data.py -o benchmarks/data/small.json -n 100

# Medium dataset (10,000 documents)
python benchmarks/generate_sample_data.py -o benchmarks/data/medium.json -n 10000

# Large dataset (100,000 documents)
python benchmarks/generate_sample_data.py -o benchmarks/data/large.json -n 100000
```

### 2. Run Benchmark

Benchmark with your data:

```bash
# Basic benchmark
python benchmarks/run_benchmark.py benchmarks/data/small.json

# With custom parameters
python benchmarks/run_benchmark.py benchmarks/data/medium.json \
  --queries 20 \
  --top-k 20 \
  --output my_index.bm25 \
  --keep-index
```

## Data Format

JSON input must be a dictionary mapping document IDs to token lists:

```json
{
  "doc1": ["token1", "token2", "token3"],
  "doc2": ["token4", "token5"],
  "doc3": ["token1", "token6", "token7"]
}
```

## Scripts

### generate_sample_data.py

Generate synthetic tokenized documents for testing.

**Usage:**
```bash
python benchmarks/generate_sample_data.py -o OUTPUT.json [OPTIONS]
```

**Options:**
- `-n, --num-docs`: Number of documents (default: 1000)
- `-v, --vocab-size`: Vocabulary size (default: 1000)
- `--min-length`: Minimum document length (default: 10)
- `--max-length`: Maximum document length (default: 100)
- `--seed`: Random seed for reproducibility
- `--pretty`: Pretty-print JSON (larger file size)

**Examples:**
```bash
# Small test dataset
python benchmarks/generate_sample_data.py -o data/test.json -n 100 -v 50

# Large dataset with long documents
python benchmarks/generate_sample_data.py -o data/big.json -n 50000 --max-length 500

# Reproducible dataset
python benchmarks/generate_sample_data.py -o data/fixed.json -n 1000 --seed 42
```

### run_benchmark.py

Benchmark BM25 build, load, and query performance.

**Usage:**
```bash
python benchmarks/run_benchmark.py JSON_FILE [OPTIONS]
```

**Options:**
- `-o, --output`: Output path for index file (default: temp file)
- `-q, --queries`: Number of sample queries (default: 10)
- `-k, --top-k`: Results per query (default: 10)
- `--keep-index`: Keep index file after benchmarking

**Examples:**
```bash
# Quick benchmark
python benchmarks/run_benchmark.py data/small.json

# Extensive benchmark with saved index
python benchmarks/run_benchmark.py data/large.json \
  --queries 50 \
  --top-k 100 \
  --output large_index.bm25 \
  --keep-index

# Benchmark your own data
python benchmarks/run_benchmark.py /path/to/your/data.json
```

## Measured Metrics

### Build Performance
- **Build time**: Time to process all documents and create postings
- **Save time**: Time to write index to disk
- **Throughput**: Documents processed per second
- **Output size**: Index file size in bytes/MB
- **Size per document**: Average bytes per document

### Load Performance
- **Load time**: Time to read index from disk
- **Throughput**: Documents loaded per second

### Query Performance
- **Average query time**: Mean time per query (milliseconds)
- **Min/Max query time**: Fastest and slowest queries
- **Throughput**: Queries per second

## Example Output

```
============================================================
BUILDING BM25 INDEX
============================================================
Documents: 10,000
Total tokens: 500,000
Average doc length: 50.00
Unique tokens: 5,000

Building index...
  Processed 2,000/10,000 documents...
  Processed 4,000/10,000 documents...
  ...

✓ Build complete!
  Build time: 2.345s
  Save time: 0.156s
  Total time: 2.501s
  Output size: 2,456,789 bytes (2.34 MB)
  Unique terms: 5,000
  Total postings: 250,000

============================================================
LOADING BM25 INDEX
============================================================
Loading index from: /tmp/tmpXXXXXX.bm25

✓ Load complete!
  Load time: 0.234s
  Documents: 10,000
  Unique terms: 5,000
  Average doc length: 50.00

============================================================
RUNNING QUERIES
============================================================

Query 1/10: 'test data'
  Time: 5.23ms
  Results: 156
  Top result: doc_00001234 (score: 8.2345)

...

✓ Queries complete!
  Total time: 0.052s
  Average time: 5.20ms per query
  Throughput: 192.31 queries/second

============================================================
BENCHMARK SUMMARY
============================================================

Dataset:
  Documents: 10,000

Build Performance:
  Time: 2.501s
  Throughput: 3,998.40 docs/second
  Output size: 2,456,789 bytes (2.34 MB)
  Size per doc: 245.68 bytes

Load Performance:
  Time: 0.234s
  Throughput: 42,735.04 docs/second

Query Performance:
  Queries run: 10
  Average time: 5.20ms
  Min time: 4.12ms
  Max time: 6.78ms
  Throughput: 192.31 queries/second
```

## Tips

### Performance Testing

1. **Warm-up runs**: Run benchmark twice, use second result
2. **Multiple trials**: Average results from multiple runs
3. **System load**: Close other applications during benchmarking
4. **Dataset size**: Test with realistic data sizes

### Data Generation

1. **Vocabulary size**: Affects unique terms and index size
2. **Document length**: Longer docs = more postings
3. **Zipfian distribution**: Simulates real word frequencies
4. **Reproducibility**: Use `--seed` for consistent results

### Custom Data

To benchmark your own data, convert it to the required JSON format:

```python
import json

# Your data
documents = {
    "id1": "your text here",
    "id2": "more text",
}

# Tokenize (use your own tokenizer)
tokenized = {
    doc_id: text.lower().split()
    for doc_id, text in documents.items()
}

# Save
with open('my_data.json', 'w') as f:
    json.dump(tokenized, f)
```

Then run the benchmark:
```bash
python benchmarks/run_benchmark.py my_data.json
```

## Interpreting Results

### Build Performance
- **< 1000 docs/sec**: Check if data is already loaded in memory
- **1000-10000 docs/sec**: Typical for average hardware
- **> 10000 docs/sec**: Excellent performance

### Query Performance
- **< 1ms**: Very fast, likely small dataset
- **1-10ms**: Good performance for medium datasets
- **> 100ms**: May need optimization or index is very large

### Index Size
- **100-500 bytes/doc**: Typical for average documents
- **< 100 bytes/doc**: Very compact (short docs or small vocab)
- **> 1000 bytes/doc**: Large documents or many unique terms

## Troubleshooting

### Out of Memory
- Reduce dataset size
- Process in batches
- Increase system RAM

### Slow Performance
- Check CPU usage
- Close background applications
- Use SSD instead of HDD
- Enable performance mode (laptops)

### Large Index Files
- Check vocabulary size
- Verify data format (shouldn't have duplicates)
- Expected for large datasets
