# Quick Start Guide

## Setup (First Time Only)

```bash
# 1. Create virtual environment
uv venv

# 2. Activate it
source .venv/bin/activate

# 3. Install package
uv pip install -e ".[dev]"
```

## Daily Development

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_bm25.py -v

# Run examples
python examples/basic_usage.py
python examples/space_efficiency.py
python examples/memory_efficiency.py
python examples/custom_tokenization.py

# Clean up build artifacts
make clean

# Deactivate when done
deactivate
```

## Using the Library

### Basic Usage

```python
from bm25comp import BM25Builder, BM25Reader

# Build an index
builder = BM25Builder(k1=1.5, b=0.75)
builder.add("doc1", "the quick brown fox")
builder.add("doc2", "the lazy dog")
builder.build()
builder.save("index.bm25")

# Search the index
reader = BM25Reader()
reader.load("index.bm25")
results = reader.search("quick dog", top_k=10)

for key, score in results:
    print(f"{key}: {score:.4f}")
```

### Custom Tokenization

```python
# Use your own tokenizer
def my_tokenizer(text):
    return text.lower().split()

builder = BM25Builder()

# Option 1: Use add_tokenized with pre-tokenized content
tokens = my_tokenizer("The quick brown fox")
builder.add_tokenized("doc1", tokens)

# Option 2: Mix with regular add()
builder.add("doc2", "the lazy dog")

builder.build()
```

## Makefile Shortcuts

```bash
make setup     # Create venv with uv
make install   # Install package (requires active venv)
make test      # Run all tests
make examples  # Run all example scripts
make benchmark # Run quick benchmark
make clean     # Remove build artifacts
make format    # Format code (requires ruff/black)
make lint      # Lint code (requires ruff)
```

## Benchmarking

```bash
# Quick benchmark with sample data
make benchmark

# Or run directly with custom data
python benchmarks/run_benchmark.py your_data.json

# Generate test data
python benchmarks/generate_sample_data.py -o data.json -n 10000
```

## Troubleshooting

### Virtual environment not activated?
```bash
source .venv/bin/activate
```

### Import errors?
```bash
# Make sure package is installed
uv pip install -e ".[dev]"
```

### Tests not running?
```bash
# Install dev dependencies
uv pip install -e ".[dev]"
```

## Project Structure

```
bm25comp/
├── src/bm25comp/       # Main package code
│   ├── builder.py      # BM25Builder class
│   └── reader.py       # BM25Reader class
├── examples/           # Usage examples
├── tests/              # Test suite
└── .venv/             # Virtual environment (auto-created)
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [SETUP.md](SETUP.md) for comprehensive setup guide
- Browse [examples/](examples/) for more usage patterns
