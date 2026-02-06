# Project Setup Guide

This guide will help you set up the development environment for BM25Comp using `uv`.

## Prerequisites

- Python 3.8 or higher
- `uv` package manager ([install instructions](https://github.com/astral-sh/uv))

## Quick Start

### 1. Create a virtual environment

```bash
uv venv
```

This creates a `.venv` directory with a fresh Python virtual environment.

### 2. Activate the virtual environment

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

**On Windows:**
```cmd
.venv\Scripts\activate
```

### 3. Install the project in development mode

```bash
uv pip install -e ".[dev]"
```

This installs:
- The `bm25comp` package in editable mode
- All development dependencies (pytest, etc.)

### 4. Verify installation

```bash
python examples/basic_usage.py
```

## Development Workflow

### Running examples

```bash
python examples/basic_usage.py
python examples/space_efficiency.py
python examples/memory_efficiency.py
```

### Running tests

```bash
pytest tests/
```

Or run specific test files:
```bash
pytest tests/test_bm25.py
pytest tests/test_incremental.py
```

### Adding new dependencies

If you need to add new packages:

```bash
# Add to runtime dependencies
uv pip install <package>

# Add to dev dependencies
uv pip install <package>
# Then manually add to pyproject.toml [project.optional-dependencies]
```

### Deactivate virtual environment

When you're done:
```bash
deactivate
```

## VS Code Integration

If you're using VS Code, it should automatically detect the `.venv` folder. You can also:

1. Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose the interpreter from `.venv`

## Troubleshooting

### `uv` not found

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or via pip:
```bash
pip install uv
```

### Permission errors on macOS

If you get permission errors, you might need to use:
```bash
uv venv --python python3
```

### Import errors

Make sure:
1. Virtual environment is activated
2. Package is installed with `uv pip install -e .`
3. You're running Python from within the venv

## Project Structure

```
bm25comp/
├── .venv/              # Virtual environment (created by uv venv)
├── src/
│   └── bm25comp/       # Main package
│       ├── __init__.py
│       ├── builder.py
│       └── reader.py
├── examples/           # Usage examples
├── tests/              # Test suite
├── pyproject.toml      # Project configuration
└── README.md           # Main documentation
```
