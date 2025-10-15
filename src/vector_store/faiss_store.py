"""FAISS vector store for semantic search."""

import pickle
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np

from src.vector_store.embedder import Embedder
from src.vector_store.models import FAQEntry, Product


class FAISSStore:
    """FAISS vector store for semantic search."""

    def __init__(self, dimension: int = 1536, embedder: Embedder = None):
        """Initialize FAISS store.

        Args:
            dimension: Dimension of embedding vectors (1536 for OpenAI, 384 for MiniLM)
            embedder: Embedder instance for generating embeddings
        """
        self.dimension = dimension
        self.embedder = embedder
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []  # Store original documents

    def add_documents(self, documents: List[str]) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of text documents to add
        """
        if not self.embedder:
            raise ValueError("Embedder not set. Cannot add documents.")

        # Generate embeddings
        embeddings = self.embedder.embed(documents)
        embeddings_np = np.array(embeddings, dtype=np.float32)

        # Add to FAISS index
        self.index.add(embeddings_np)

        # Store original documents
        self.documents.extend(documents)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar documents.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of (document, distance) tuples
        """
        if not self.embedder:
            raise ValueError("Embedder not set. Cannot search.")

        # Generate query embedding
        query_embedding = self.embedder.embed([query])[0]
        query_embedding_np = np.array([query_embedding], dtype=np.float32)

        # Search
        distances, indices = self.index.search(query_embedding_np, top_k)

        # Return results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))

        return results

    def save(self, index_path: Path, documents_path: Path) -> None:
        """Save FAISS index and documents to disk.

        Args:
            index_path: Path to save FAISS index
            documents_path: Path to save documents pickle
        """
        # Save FAISS index
        faiss.write_index(self.index, str(index_path))

        # Save documents
        with open(documents_path, "wb") as f:
            pickle.dump(self.documents, f)

    def load(self, index_path: Path, documents_path: Path) -> None:
        """Load FAISS index and documents from disk.

        Args:
            index_path: Path to FAISS index file
            documents_path: Path to documents pickle file
        """
        # Load FAISS index
        self.index = faiss.read_index(str(index_path))

        # Load documents
        with open(documents_path, "rb") as f:
            self.documents = pickle.load(f)


class ProductVectorStore:
    """Specialized vector store for products with structured search."""

    def __init__(self, embedder: Embedder):
        """Initialize product vector store.

        Args:
            embedder: Embedder instance
        """
        self.embedder = embedder
        self.products: List[Product] = []
        self.store = FAISSStore(dimension=self._get_dimension(), embedder=embedder)

    def _get_dimension(self) -> int:
        """Get embedding dimension from embedder type."""
        # Test embedding to get dimension
        test_embed = self.embedder.embed(["test"])[0]
        return len(test_embed)

    def add_products(self, products: List[Product]) -> None:
        """Add products to vector store.

        Args:
            products: List of Product objects
        """
        self.products = products
        texts = [p.to_text() for p in products]
        self.store.add_documents(texts)

    def search(
        self, query: str, top_k: int = 5, max_price: int = None
    ) -> List[Tuple[Product, float]]:
        """Search for products.

        Args:
            query: Search query
            top_k: Number of results
            max_price: Optional maximum price filter

        Returns:
            List of (Product, score) tuples
        """
        # Search vector store (get more results for filtering)
        search_k = top_k * 3 if max_price else top_k
        results = self.store.search(query, top_k=search_k)

        # Map back to products
        product_results = []
        for doc, score in results:
            # Find matching product by text
            for product in self.products:
                if product.to_text() == doc:
                    # Apply price filter
                    if max_price is None or product.price_eur <= max_price:
                        product_results.append((product, score))
                        if len(product_results) >= top_k:
                            return product_results
                    break

        return product_results

    def save(self, base_path: Path) -> None:
        """Save product vector store.

        Args:
            base_path: Base directory path
        """
        base_path.mkdir(parents=True, exist_ok=True)
        self.store.save(
            base_path / "products.index", base_path / "products_docs.pkl"
        )

        # Save products list
        with open(base_path / "products.pkl", "wb") as f:
            pickle.dump(self.products, f)

    def load(self, base_path: Path) -> None:
        """Load product vector store.

        Args:
            base_path: Base directory path
        """
        self.store.load(
            base_path / "products.index", base_path / "products_docs.pkl"
        )

        # Load products list
        with open(base_path / "products.pkl", "rb") as f:
            self.products = pickle.load(f)


class FAQVectorStore:
    """Specialized vector store for FAQ entries."""

    def __init__(self, embedder: Embedder):
        """Initialize FAQ vector store.

        Args:
            embedder: Embedder instance
        """
        self.embedder = embedder
        self.faqs: List[FAQEntry] = []
        self.store = FAISSStore(dimension=self._get_dimension(), embedder=embedder)

    def _get_dimension(self) -> int:
        """Get embedding dimension from embedder type."""
        test_embed = self.embedder.embed(["test"])[0]
        return len(test_embed)

    def add_faqs(self, faqs: List[FAQEntry]) -> None:
        """Add FAQ entries to vector store.

        Args:
            faqs: List of FAQEntry objects
        """
        self.faqs = faqs
        texts = [faq.to_text() for faq in faqs]
        self.store.add_documents(texts)

    def search(self, query: str, top_k: int = 2) -> List[Tuple[FAQEntry, float]]:
        """Search for FAQ entries.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of (FAQEntry, score) tuples
        """
        results = self.store.search(query, top_k=top_k)

        # Map back to FAQs
        faq_results = []
        for doc, score in results:
            for faq in self.faqs:
                if faq.to_text() == doc:
                    faq_results.append((faq, score))
                    break

        return faq_results

    def save(self, base_path: Path) -> None:
        """Save FAQ vector store.

        Args:
            base_path: Base directory path
        """
        base_path.mkdir(parents=True, exist_ok=True)
        self.store.save(base_path / "faq.index", base_path / "faq_docs.pkl")

        # Save FAQs list
        with open(base_path / "faqs.pkl", "wb") as f:
            pickle.dump(self.faqs, f)

    def load(self, base_path: Path) -> None:
        """Load FAQ vector store.

        Args:
            base_path: Base directory path
        """
        self.store.load(base_path / "faq.index", base_path / "faq_docs.pkl")

        # Load FAQs list
        with open(base_path / "faqs.pkl", "rb") as f:
            self.faqs = pickle.load(f)
