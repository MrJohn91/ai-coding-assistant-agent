"""Unit tests for vector store."""

import pytest
from unittest.mock import Mock

from src.vector_store.faiss_store import ProductVectorStore, FAQVectorStore
from src.vector_store.models import Product, FAQEntry


@pytest.fixture
def mock_embedder():
    """Create mock embedder."""
    embedder = Mock()
    embedder.embed.return_value = [[0.1] * 1536]  # Mock embedding
    return embedder


@pytest.fixture
def sample_products():
    """Create sample products."""
    return [
        Product(
            id=1,
            name="Mountain Bike Pro",
            type="Mountain Bike",
            brand="TestBrand",
            price_eur=1500,
            frame_material="Aluminum",
            suspension="Full Suspension",
            wheel_size=29,
            gears=12,
            brakes="Hydraulic Disc",
            weight_kg=13.5,
            intended_use=["Trail", "Off-road"],
            color="Red",
        ),
        Product(
            id=2,
            name="City Cruiser",
            type="City Bike",
            brand="TestBrand",
            price_eur=800,
            frame_material="Steel",
            suspension="Rigid",
            wheel_size=28,
            gears=7,
            brakes="V-Brake",
            weight_kg=15.0,
            intended_use=["Urban", "Commuting"],
            color="Black",
        ),
    ]


@pytest.fixture
def sample_faqs():
    """Create sample FAQs."""
    return [
        FAQEntry(
            question="What is the warranty?",
            answer="All bikes come with 2-year warranty.",
        ),
        FAQEntry(
            question="Do you offer delivery?",
            answer="Yes, we deliver within EU in 5-7 days.",
        ),
    ]


class TestProductVectorStore:
    """Test product vector store."""

    def test_add_products(self, mock_embedder, sample_products):
        """Test adding products to store."""
        store = ProductVectorStore(mock_embedder)
        store.add_products(sample_products)

        assert len(store.products) == 2
        assert store.index is not None
        assert mock_embedder.embed.called

    def test_search_products(self, mock_embedder, sample_products):
        """Test searching products."""
        store = ProductVectorStore(mock_embedder)
        store.add_products(sample_products)

        results = store.search("mountain bike", top_k=1)

        assert len(results) == 1
        product, score = results[0]
        assert isinstance(product, Product)
        assert isinstance(score, float)


class TestFAQVectorStore:
    """Test FAQ vector store."""

    def test_add_faqs(self, mock_embedder, sample_faqs):
        """Test adding FAQs to store."""
        store = FAQVectorStore(mock_embedder)
        store.add_faqs(sample_faqs)

        assert len(store.faqs) == 2
        assert store.index is not None
        assert mock_embedder.embed.called

    def test_search_faqs(self, mock_embedder, sample_faqs):
        """Test searching FAQs."""
        store = FAQVectorStore(mock_embedder)
        store.add_faqs(sample_faqs)

        results = store.search("warranty information", top_k=1)

        assert len(results) == 1
        faq, score = results[0]
        assert isinstance(faq, FAQEntry)
        assert isinstance(score, float)
