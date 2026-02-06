import math
import struct
from collections import defaultdict
from typing import Any, Dict, List


class BM25Builder:
    """
    Builder class for BM25 algorithm that creates space-efficient,
    language-agnostic binary representations of BM25 indices.

    Keys are mapped to integers to reduce space, and all data is
    serialized in a binary format that can be read by any language.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25Builder.

        Args:
            k1: Term frequency saturation parameter (default: 1.5)
            b: Length normalization parameter (default: 0.75)
        """
        self.k1 = k1
        self.b = b

        # Key to integer mapping
        self.key_to_id: Dict[Any, int] = {}
        self.id_to_key: Dict[int, Any] = {}
        self.next_doc_id = 0

        # BM25 components (computed incrementally)
        self.temp_postings: Dict[str, Dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.doc_lengths: Dict[int, int] = {}
        self.total_length: int = 0
        self.num_docs: int = 0

        # Finalized after build()
        self.term_doc_freq: Dict[str, int] = {}  # df: document frequency per term
        self.postings: Dict[
            str, List[tuple[int, int]]
        ] = {}  # term -> [(doc_id, term_freq), ...]
        self.avgdl: float = 0.0  # average document length
        self.built = False

    def add(self, key: Any, content: str) -> None:
        """
        Add a document to the index.

        Args:
            key: Document identifier (can be any type, will be mapped to integer)
            content: Document text content
        """
        tokens = self._tokenize(content)
        self.add_tokenized(key, tokens)

    def add_tokenized(self, key: Any, tokens: List[str]) -> None:
        """
        Add a document to the index using pre-tokenized content.

        This is useful when you have your own tokenizer or want to avoid
        double-tokenization. The tokens should be in the same format as
        what _tokenize() would produce.

        Args:
            key: Document identifier (can be any type, will be mapped to integer)
            tokens: Pre-tokenized document as a list of token strings
        """
        if self.built:
            raise RuntimeError("Cannot add documents after build() has been called")

        # Map key to integer ID (reuse if key already exists)
        if key not in self.key_to_id:
            doc_id = self.next_doc_id
            self.key_to_id[key] = doc_id
            self.id_to_key[doc_id] = key
            self.next_doc_id += 1
        else:
            doc_id = self.key_to_id[key]

        # Process document immediately
        doc_length = len(tokens)

        # Store document length and update total
        self.doc_lengths[doc_id] = doc_length
        self.total_length += doc_length
        self.num_docs += 1

        # Count term frequencies in this document
        for term in tokens:
            self.temp_postings[term][doc_id] += 1

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization by splitting on whitespace and converting to lowercase.
        Override this method for custom tokenization.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        return text.lower().split()

    def build(self) -> None:
        """
        Finalize the BM25 index by computing average document length
        and converting temporary postings to final format.
        """
        if self.built:
            raise RuntimeError("build() has already been called")

        if self.num_docs == 0:
            raise ValueError("Cannot build index with no documents")

        # Compute average document length
        self.avgdl = self.total_length / self.num_docs if self.num_docs > 0 else 0.0

        # Convert temp_postings to final format and compute document frequencies
        for term, doc_freqs in self.temp_postings.items():
            self.term_doc_freq[term] = len(doc_freqs)
            # Sort postings by document ID for efficient binary search in reader
            self.postings[term] = sorted(
                [(doc_id, freq) for doc_id, freq in doc_freqs.items()]
            )

        # Clear temporary storage to free memory
        self.temp_postings.clear()

        self.built = True

    def save(self, filepath: str) -> None:
        """
        Save the BM25 index to a binary file in a language-agnostic format.

        File format:
        - Header: magic number, version, k1, b, avgdl, num_docs, num_terms
        - Key mapping section: doc_id -> key string
        - Postings section: term -> [(doc_id, term_freq), ...]
        - Doc lengths section: doc_id -> length

        Args:
            filepath: Path to save the index
        """
        if not self.built:
            raise RuntimeError("Must call build() before save()")

        with open(filepath, "wb") as f:
            # Header: magic number (4 bytes) + version (4 bytes)
            f.write(struct.pack("!I", 0x424D3235))  # "BM25" in hex
            f.write(struct.pack("!I", 1))  # version 1

            # BM25 parameters and statistics
            f.write(struct.pack("!f", self.k1))
            f.write(struct.pack("!f", self.b))
            f.write(struct.pack("!f", self.avgdl))
            f.write(struct.pack("!I", self.num_docs))
            f.write(struct.pack("!I", len(self.postings)))  # num_terms

            # Key mapping section: num_keys, then for each: doc_id, key_length, key_bytes
            f.write(struct.pack("!I", len(self.id_to_key)))
            for doc_id in sorted(self.id_to_key.keys()):
                key = str(self.id_to_key[doc_id])
                key_bytes = key.encode("utf-8")
                f.write(struct.pack("!I", doc_id))
                f.write(struct.pack("!I", len(key_bytes)))
                f.write(key_bytes)

            # Doc lengths section: for each doc_id, length
            f.write(struct.pack("!I", len(self.doc_lengths)))
            for doc_id in sorted(self.doc_lengths.keys()):
                f.write(struct.pack("!I", doc_id))
                f.write(struct.pack("!I", self.doc_lengths[doc_id]))

            # Postings section: for each term
            for term in sorted(self.postings.keys()):
                term_bytes = term.encode("utf-8")
                postings_list = self.postings[term]

                # term_length, term_bytes, num_postings, then [(doc_id, freq), ...]
                f.write(struct.pack("!I", len(term_bytes)))
                f.write(term_bytes)
                f.write(struct.pack("!I", len(postings_list)))

                for doc_id, freq in postings_list:
                    f.write(struct.pack("!I", doc_id))
                    f.write(struct.pack("!I", freq))

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the built index.

        Returns:
            Dictionary with index statistics
        """
        if not self.built:
            raise RuntimeError("Must call build() first")

        return {
            "num_documents": self.num_docs,
            "num_unique_terms": len(self.postings),
            "average_document_length": self.avgdl,
            "k1": self.k1,
            "b": self.b,
            "total_postings": sum(len(p) for p in self.postings.values()),
        }
