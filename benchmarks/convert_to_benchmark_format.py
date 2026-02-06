#!/usr/bin/env python3
"""
Helper script to convert various data formats to benchmark JSON format.

Supports:
- Plain text files (one document per line)
- CSV files with id,text columns
- JSONL files with {id: str, text: str}

Output format: {doc_id: [tokens], ...}
"""

import argparse
import csv
import json
import sys
from pathlib import Path


def simple_tokenizer(text: str) -> list[str]:
    """Simple whitespace tokenizer."""
    return text.lower().split()


def convert_text_file(input_path: str, output_path: str, tokenizer=simple_tokenizer):
    """Convert plain text file (one doc per line) to benchmark format."""
    print(f"Reading from: {input_path}")

    data = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if line:
                doc_id = f"doc_{i:08d}"
                tokens = tokenizer(line)
                data[doc_id] = tokens

                if i % 1000 == 0:
                    print(f"  Processed {i:,} lines...")

    print(f"✓ Converted {len(data):,} documents")
    return data


def convert_csv_file(input_path: str, output_path: str,
                     id_column: str = 'id', text_column: str = 'text',
                     tokenizer=simple_tokenizer):
    """Convert CSV file to benchmark format."""
    print(f"Reading from: {input_path}")

    data = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            if id_column not in row or text_column not in row:
                print(f"Warning: Row {i} missing required columns")
                continue

            doc_id = row[id_column]
            text = row[text_column]
            tokens = tokenizer(text)
            data[doc_id] = tokens

            if i % 1000 == 0:
                print(f"  Processed {i:,} rows...")

    print(f"✓ Converted {len(data):,} documents")
    return data


def convert_jsonl_file(input_path: str, output_path: str,
                       id_field: str = 'id', text_field: str = 'text',
                       tokenizer=simple_tokenizer):
    """Convert JSONL file to benchmark format."""
    print(f"Reading from: {input_path}")

    data = {}
    with open(input_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                obj = json.loads(line)
                doc_id = str(obj.get(id_field, f"doc_{i:08d}"))
                text = obj.get(text_field, "")
                tokens = tokenizer(text)
                data[doc_id] = tokens

                if i % 1000 == 0:
                    print(f"  Processed {i:,} lines...")

            except json.JSONDecodeError:
                print(f"Warning: Skipping invalid JSON on line {i}")

    print(f"✓ Converted {len(data):,} documents")
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Convert various formats to benchmark JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input Formats:
  text:  Plain text file, one document per line
  csv:   CSV file with id,text columns
  jsonl: JSONL file with {id: str, text: str} objects

Examples:
  # Convert text file
  python benchmarks/convert_to_benchmark_format.py \\
    --input docs.txt --output benchmark.json --format text

  # Convert CSV with custom columns
  python benchmarks/convert_to_benchmark_format.py \\
    --input data.csv --output benchmark.json --format csv \\
    --id-column doc_id --text-column content

  # Convert JSONL
  python benchmarks/convert_to_benchmark_format.py \\
    --input data.jsonl --output benchmark.json --format jsonl
        """
    )

    parser.add_argument('-i', '--input', required=True,
                        help='Input file path')
    parser.add_argument('-o', '--output', required=True,
                        help='Output JSON file path')
    parser.add_argument('-f', '--format', choices=['text', 'csv', 'jsonl'],
                        required=True, help='Input file format')
    parser.add_argument('--id-column', default='id',
                        help='CSV: column name for document ID (default: id)')
    parser.add_argument('--text-column', default='text',
                        help='CSV: column name for document text (default: text)')
    parser.add_argument('--id-field', default='id',
                        help='JSONL: field name for document ID (default: id)')
    parser.add_argument('--text-field', default='text',
                        help='JSONL: field name for document text (default: text)')
    parser.add_argument('--pretty', action='store_true',
                        help='Pretty-print output JSON')

    args = parser.parse_args()

    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Convert based on format
    print("="*70)
    print("CONVERTING TO BENCHMARK FORMAT")
    print("="*70)
    print()

    if args.format == 'text':
        data = convert_text_file(args.input, args.output)
    elif args.format == 'csv':
        data = convert_csv_file(args.input, args.output,
                                args.id_column, args.text_column)
    elif args.format == 'jsonl':
        data = convert_jsonl_file(args.input, args.output,
                                  args.id_field, args.text_field)
    else:
        print(f"Error: Unknown format: {args.format}")
        sys.exit(1)

    # Save output
    print(f"\nSaving to: {args.output}")
    with open(args.output, 'w', encoding='utf-8') as f:
        if args.pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)

    file_size = Path(args.output).stat().st_size
    print(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print("\n✓ Conversion complete!")
    print(f"\nRun benchmark with:")
    print(f"  python benchmarks/run_benchmark.py {args.output}")


if __name__ == "__main__":
    main()
