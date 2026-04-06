"""Seed an in-memory Qdrant collection with 10 hardcoded AI/ML FAQs.

This module is imported by `server.py` at startup. It exposes
`get_seeded_client()` which returns a ready-to-query QdrantClient and
the name of the collection that was created.
"""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "ai_ml_faq"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

FAQ_ENTRIES: list[dict] = [
    {
        "question": "What is machine learning?",
        "answer": (
            "Machine learning is a branch of AI where models learn patterns "
            "from data instead of being explicitly programmed with rules."
        ),
    },
    {
        "question": "What is the difference between supervised and unsupervised learning?",
        "answer": (
            "Supervised learning uses labeled examples to learn a mapping "
            "from input to output, while unsupervised learning finds "
            "structure in unlabeled data, e.g. via clustering."
        ),
    },
    {
        "question": "What is a neural network?",
        "answer": (
            "A neural network is a stack of layers of simple units (neurons) "
            "connected by weighted edges; training adjusts those weights via "
            "gradient descent so the network approximates a target function."
        ),
    },
    {
        "question": "What is a transformer model?",
        "answer": (
            "A transformer is a neural architecture built around self-attention "
            "that processes sequences in parallel, and is the foundation of "
            "modern LLMs such as GPT, Claude, and Llama."
        ),
    },
    {
        "question": "What is RAG (retrieval augmented generation)?",
        "answer": (
            "RAG is a technique where an LLM is given documents retrieved "
            "from an external knowledge base at query time so it can answer "
            "with grounded, up-to-date information instead of relying only "
            "on its training data."
        ),
    },
    {
        "question": "What is a vector database?",
        "answer": (
            "A vector database stores high-dimensional embeddings and supports "
            "fast approximate nearest-neighbor search, which lets you find "
            "semantically similar text, images, or audio."
        ),
    },
    {
        "question": "What are embeddings?",
        "answer": (
            "Embeddings are dense numeric vectors that represent the meaning "
            "of a piece of content; semantically similar items end up close "
            "together in the embedding space."
        ),
    },
    {
        "question": "What is fine-tuning?",
        "answer": (
            "Fine-tuning is the process of continuing to train a pretrained "
            "model on a smaller, task-specific dataset so it adapts its "
            "behavior or style to a particular domain."
        ),
    },
    {
        "question": "What is overfitting?",
        "answer": (
            "Overfitting happens when a model memorizes its training data "
            "and fails to generalize to new examples; it's typically "
            "addressed with more data, regularization, or early stopping."
        ),
    },
    {
        "question": "What is the Model Context Protocol (MCP)?",
        "answer": (
            "MCP is an open protocol that lets LLM applications connect to "
            "external tools, data sources, and prompts in a standardized "
            "way, similar to how USB standardizes hardware connections."
        ),
    },
]


_embedder: SentenceTransformer | None = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL_NAME)
    return _embedder


def embed(text: str) -> list[float]:
    """Embed a single string with the shared sentence-transformer model."""
    return _get_embedder().encode(text).tolist()


def get_seeded_client() -> tuple[QdrantClient, str]:
    """Build an in-memory Qdrant client and load it with the FAQ entries."""
    embedder = _get_embedder()
    dim = embedder.get_sentence_embedding_dimension()

    client = QdrantClient(":memory:")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    points: list[PointStruct] = []
    for idx, entry in enumerate(FAQ_ENTRIES):
        text = f"{entry['question']} {entry['answer']}"
        points.append(
            PointStruct(
                id=idx,
                vector=embedder.encode(text).tolist(),
                payload=entry,
            )
        )
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return client, COLLECTION_NAME
