"""
Embedding Service — sentence-transformers + pgvector
Generates 384-dim vectors and stores them in PostgreSQL via pgvector.
"""
import asyncio
from datetime import date
from typing import Optional

import numpy as np
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.models import ProductEmbedding, InsightEmbedding
from app.core.config import settings

# Lazy-loaded pipeline instance
_model = None
_lock  = asyncio.Lock()


async def _get_model():
    """Lazily load the sentence-transformers model in a thread."""
    global _model
    if _model is not None:
        return _model
    async with _lock:
        if _model is not None:
            return _model
        loop = asyncio.get_event_loop()
        _model = await loop.run_in_executor(None, _load_model)
    return _model


def _load_model():
    from sentence_transformers import SentenceTransformer
    print(f"[Embedding] Loading model '{settings.EMBEDDING_MODEL}'...")
    m = SentenceTransformer(settings.EMBEDDING_MODEL)
    print("[Embedding] Model ready ✅")
    return m


async def embed_text(text: str) -> list[float]:
    """Return a 384-dim embedding vector for a text string."""
    model = await _get_model()
    loop  = asyncio.get_event_loop()
    vec   = await loop.run_in_executor(None, lambda: model.encode(text, normalize_embeddings=True))
    return vec.tolist()


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Batch embed multiple texts for efficiency."""
    model  = await _get_model()
    loop   = asyncio.get_event_loop()
    vecs   = await loop.run_in_executor(None, lambda: model.encode(texts, normalize_embeddings=True, batch_size=32))
    return [v.tolist() for v in vecs]


# ── Singleton service ──────────────────────────────────────────
class EmbeddingService:
    async def preload(self):
        """Pre-warm the model at startup to prevent cold-start lag."""
        await _get_model()

    async def upsert_product_embedding(
        self,
        db: AsyncSession,
        seller_id: str,
        product_id: str,
        summary_text: str,
        embed_date: Optional[date] = None,
        embed_type: str = "daily_snapshot",
        metadata: Optional[dict] = None,
    ) -> ProductEmbedding:
        embed_date = embed_date or date.today()
        vector = await embed_text(summary_text)

        # Upsert (on conflict update vector + text)
        stmt = (
            pg_insert(ProductEmbedding)
            .values(
                seller_id=seller_id,
                product_id=product_id,
                embed_date=embed_date,
                embed_type=embed_type,
                summary_text=summary_text,
                embedding=vector,
                meta=metadata or {},       # ORM attr is 'meta' (column name is 'metadata')
            )
            .on_conflict_do_update(
                index_elements=["seller_id", "product_id", "embed_date", "embed_type"],
                set_={"summary_text": summary_text, "embedding": vector, "metadata": metadata or {}},
            )
        )
        await db.execute(stmt)
        await db.commit()
        return vector

    async def find_similar_products(
        self,
        db: AsyncSession,
        seller_id: str,
        query_text: str,
        limit: int = 5,
        embed_type: str = "daily_snapshot",
    ) -> list[dict]:
        """
        Find similar products using pgvector cosine similarity.
        Returns product_id, summary_text, and similarity score.
        """
        query_vector = await embed_text(query_text)
        # Use raw SQL for pgvector operator <=> (cosine distance)
        from sqlalchemy import text
        sql = text("""
            SELECT
                pe.product_id,
                pe.summary_text,
                pe.embed_date,
                pe.metadata,
                1 - (pe.embedding <=> cast(:vec AS vector)) AS similarity
            FROM product_embeddings pe
            WHERE pe.seller_id = :seller_id
              AND pe.embed_type = :embed_type
            ORDER BY pe.embedding <=> cast(:vec AS vector)
            LIMIT :limit
        """)
        result = await db.execute(sql, {
            "vec": str(query_vector),
            "seller_id": str(seller_id),
            "embed_type": embed_type,
            "limit": limit,
        })
        rows = result.fetchall()
        return [
            {
                "product_id": str(r.product_id),
                "summary_text": r.summary_text,
                "embed_date": str(r.embed_date),
                "metadata": r.metadata,
                "similarity": float(r.similarity),
            }
            for r in rows
        ]

    async def store_insight(
        self,
        db: AsyncSession,
        seller_id: str,
        insight_text: str,
        insight_type: str,
        insight_date: Optional[date] = None,
        metadata: Optional[dict] = None,
    ):
        insight_date = insight_date or date.today()
        vector = await embed_text(insight_text)
        row = InsightEmbedding(
            seller_id=seller_id,
            insight_date=insight_date,
            insight_type=insight_type,
            insight_text=insight_text,
            embedding=vector,
            meta=metadata or {},            # ORM attr is 'meta' (column name is 'metadata')
        )
        db.add(row)
        await db.commit()
        return row

    async def find_similar_insights(
        self,
        db: AsyncSession,
        seller_id: str,
        query_text: str,
        limit: int = 5,
    ) -> list[dict]:
        query_vector = await embed_text(query_text)
        from sqlalchemy import text
        sql = text("""
            SELECT
                ie.insight_type,
                ie.insight_text,
                ie.insight_date,
                ie.metadata,
                1 - (ie.embedding <=> cast(:vec AS vector)) AS similarity
            FROM insight_embeddings ie
            WHERE ie.seller_id = :seller_id
            ORDER BY ie.embedding <=> cast(:vec AS vector)
            LIMIT :limit
        """)
        result = await db.execute(sql, {
            "vec": str(query_vector),
            "seller_id": str(seller_id),
            "limit": limit,
        })
        rows = result.fetchall()
        return [
            {
                "insight_type": r.insight_type,
                "insight_text": r.insight_text,
                "insight_date": str(r.insight_date),
                "metadata": r.metadata,
                "similarity": float(r.similarity),
            }
            for r in rows
        ]


embedding_service = EmbeddingService()
