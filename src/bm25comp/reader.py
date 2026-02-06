import math
import struct
from typing import Any, Dict, List, Tuple


class BM25Reader:
    """
    Reader class for loading and querying BM25 indices saved in binary format.

    Can read indices created by BM25Builder from any language that implements
    the same binary format specification.
    """

    def __init__(self):
        """Initialize empty BM25Reader."""
        self.k1: float = 0.0
        self.b: float = 0.0
        self.avgdl: float = 0.0
        self.num_docs: int = 0
        self.num_terms: int = 0

        self.id_to_key: Dict[int, str] = {}
        self.doc_lengths: Dict[int, int] = {}
        self.postings: Dict[str, List[Tuple[int, int]]] = {}
        self.term_doc_freq: Dict[str, int] = {}

        self.loaded = False

    def load(self, filepath: str) -> None:
        """
        Load a BM25 index from a binary file.

        Args:
            filepath: Path to the BM25 index file

        Raises:
            ValueError: If file format is invalid
            FileNotFoundError: If file doesn't exist
        """
        with open(filepath, "rb") as f:
            # Read and verify header
            magic = struct.unpack("!I", f.read(4))[0]
            if magic != 0x424D3235:  # "BM25"
                raise ValueError("Invalid BM25 file format: wrong magic number")

            version = struct.unpack("!I", f.read(4))[0]
            if version != 1:
                raise ValueError(f"Unsupported BM25 file version: {version}")

            # Read BM25 parameters and statistics
            self.k1 = struct.unpack("!f", f.read(4))[0]
            self.b = struct.unpack("!f", f.read(4))[0]
            self.avgdl = struct.unpack("!f", f.read(4))[0]
            self.num_docs = struct.unpack("!I", f.read(4))[0]
            self.num_terms = struct.unpack("!I", f.read(4))[0]

            # Read key mapping section
            num_keys = struct.unpack("!I", f.read(4))[0]
            for _ in range(num_keys):
                doc_id = struct.unpack("!I", f.read(4))[0]
                key_length = struct.unpack("!I", f.read(4))[0]
                key_bytes = f.read(key_length)
                key = key_bytes.decode("utf-8")
                self.id_to_key[doc_id] = key

            # Read doc lengths section
            num_doc_lengths = struct.unpack("!I", f.read(4))[0]
            for _ in range(num_doc_lengths):
                doc_id = struct.unpack("!I", f.read(4))[0]
                length = struct.unpack("!I", f.read(4))[0]
                self.doc_lengths[doc_id] = length

            # Read postings section
            for _ in range(self.num_terms):
                term_length = struct.unpack("!I", f.read(4))[0]
                term_bytes = f.read(term_length)
                term = term_bytes.decode("utf-8")

                num_postings = struct.unpack("!I", f.read(4))[0]
                postings_list = []

                for _ in range(num_postings):
                    doc_id = struct.unpack("!I", f.read(4))[0]
                    freq = struct.unpack("!I", f.read(4))[0]
                    postings_list.append((doc_id, freq))

                self.postings[term] = postings_list
                self.term_doc_freq[term] = num_postings

        self.loaded = True

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization by splitting on whitespace and converting to lowercase.
        Must match the tokenization used in BM25Builder.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        return text.lower().split()

    def _idf(self, term: str) -> float:
        """
        Calculate IDF (Inverse Document Frequency) for a term.

        Args:
            term: The term to calculate IDF for

        Returns:
            IDF score
        """
        if term not in self.term_doc_freq:
            return 0.0

        df = self.term_doc_freq[term]
        idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1.0)
        return idf

    def score_document(self, query: str, doc_id: int) -> float:
        """
        Calculate BM25 score for a single document given a query.

        Args:
            query: Query string
            doc_id: Document ID to score

        Returns:
            BM25 score
        """
        if not self.loaded:
            raise RuntimeError("Must call load() before scoring")

        if doc_id not in self.doc_lengths:
            return 0.0

        query_terms = self._tokenize(query)
        score = 0.0
        doc_length = self.doc_lengths[doc_id]

        for term in query_terms:
            if term not in self.postings:
                continue

            idf = self._idf(term)

            # Find term frequency in this document using binary search
            # since postings are stored as (doc_id, freq) pairs
            tf = 0
            postings_list = self.postings[term]

            # Binary search for the document ID
            left, right = 0, len(postings_list) - 1
            while left <= right:
                mid = (left + right) // 2
                mid_doc_id = postings_list[mid][0]

                if mid_doc_id == doc_id:
                    tf = postings_list[mid][1]
                    break
                elif mid_doc_id < doc_id:
                    left = mid + 1
                else:
                    right = mid - 1

            if tf > 0:
                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (
                    1 - self.b + self.b * (doc_length / self.avgdl)
                )
                score += idf * (numerator / denominator)

        return score

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for documents matching a query.

        Args:
            query: Query string
            top_k: Number of top results to return

        Returns:
            List of (key, score) tuples, sorted by score descending
        """
        if not self.loaded:
            raise RuntimeError("Must call load() before searching")

        query_terms = self._tokenize(query)

        # Get candidate documents (documents containing at least one query term)
        candidate_docs = set()
        for term in query_terms:
            if term in self.postings:
                for doc_id, _ in self.postings[term]:
                    candidate_docs.add(doc_id)

        # Score all candidate documents
        scores = []
        for doc_id in candidate_docs:
            score = self.score_document(query, doc_id)
            if score > 0:
                key = self.id_to_key[doc_id]
                scores.append((key, score))

        # Sort by score descending and return top k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded index.

        Returns:
            Dictionary with index statistics
        """
        if not self.loaded:
            raise RuntimeError("Must call load() first")

        return {
            "num_documents": self.num_docs,
            "num_unique_terms": self.num_terms,
            "average_document_length": self.avgdl,
            "k1": self.k1,
            "b": self.b,
            "total_postings": sum(len(p) for p in self.postings.values()),
        }
