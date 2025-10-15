"""Setup script to build FAISS vector stores."""

import logging
from pathlib import Path

from src.config import settings
from src.data.loader import load_faq, load_products
from src.vector_store.embedder import get_embedder
from src.vector_store.faiss_store import FAQVectorStore, ProductVectorStore

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_vector_stores():
    """Build and save FAISS vector stores for products and FAQs."""
    logger.info("Starting vector store setup...")

    # Get embedder
    embedder = get_embedder()
    logger.info(f"Using embedder: {embedder.__class__.__name__}")

    # Load data
    logger.info("Loading product catalog...")
    products = load_products(settings.product_catalog_path)
    logger.info(f"Loaded {len(products)} products")

    logger.info("Loading FAQ...")
    faqs = load_faq(settings.faq_path)
    logger.info(f"Loaded {len(faqs)} FAQ entries")

    # Create product vector store
    logger.info("Building product vector store...")
    product_store = ProductVectorStore(embedder)
    product_store.add_products(products)
    product_store.save(settings.faiss_index_path)
    logger.info(f"Product vector store saved to {settings.faiss_index_path}")

    # Create FAQ vector store
    logger.info("Building FAQ vector store...")
    faq_store = FAQVectorStore(embedder)
    faq_store.add_faqs(faqs)
    faq_store.save(settings.faiss_index_path)
    logger.info(f"FAQ vector store saved to {settings.faiss_index_path}")

    logger.info("Vector store setup complete!")

    # Test search
    logger.info("\n--- Testing Product Search ---")
    test_query = "mountain bike for trail riding"
    logger.info(f"Query: {test_query}")
    results = product_store.search(test_query, top_k=3)
    for product, score in results:
        logger.info(f"  - {product.name} ({product.type}, €{product.price_eur}) - Score: {score:.2f}")

    logger.info("\n--- Testing FAQ Search ---")
    test_query = "warranty for electric bikes"
    logger.info(f"Query: {test_query}")
    results = faq_store.search(test_query, top_k=2)
    for faq, score in results:
        logger.info(f"  - Q: {faq.question[:50]}... - Score: {score:.2f}")


if __name__ == "__main__":
    setup_vector_stores()
