"""
app/tasks/embed.py
Celery tasks for background embedding.

Tasks:
  auto_embed         — triggered after each Excel upload (per seller, per date)
  nightly_embed_all  — Celery Beat scheduled task, runs daily at 2 AM IST
  embed_single_product — embeds a single product summary (used by /ai/embed/product)
"""
import asyncio
import logging
from datetime import date, timedelta

from celery import shared_task

logger = logging.getLogger(__name__)


# ── Core async embedding logic ─────────────────────────────────
async def _run_embed(seller_id: str, snap_date_str: str) -> int:
    """
    Fetch product snapshot for seller + date, batch-encode summaries,
    bulk-upsert into Supabase product_embeddings.
    Returns number of products embedded.
    """
    from sqlalchemy import text
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    from app.db.session import AsyncSessionLocal
    from app.models.models import ProductEmbedding
    from app.services.embeddings import embed_batch

    snap_date = date.fromisoformat(snap_date_str)

    async with AsyncSessionLocal() as db:
        sql = text("""
            SELECT
                p.product_id, p.sku, p.product_name, p.category,
                i.marketplace,
                i.available_stock, i.reorder_threshold,
                pr.selling_price,
                CASE WHEN pr.selling_price > 0 AND pr.cost_price IS NOT NULL 
                     THEN ((pr.selling_price - pr.cost_price - COALESCE(pr.commission_amount, 0)) / pr.selling_price) * 100 
                     ELSE NULL END AS margin_pct,
                t.impressions, t.clicks, t.orders AS ad_orders,
                CASE WHEN t.ad_spend > 0 THEN t.revenue_from_ads / t.ad_spend ELSE 0 END AS roas
            FROM products p
            LEFT JOIN inventory_snapshots i
                ON i.product_id = p.product_id AND i.seller_id = :sid
               AND i.snapshot_date = :d
            LEFT JOIN pricing_snapshots pr
                ON pr.product_id = p.product_id AND pr.seller_id = :sid
               AND pr.snapshot_date = :d
            LEFT JOIN traffic_metrics t
                ON t.product_id = p.product_id AND t.seller_id = :sid
               AND t.metric_date = :d
            WHERE p.seller_id = :sid
        """)
        result = await db.execute(sql, {"sid": seller_id, "d": snap_date})
        rows = result.mappings().all()

        if not rows:
            logger.warning("[Embed] No products for seller=%s date=%s", seller_id, snap_date)
            return 0

        # Build summary strings
        summaries = [
            (
                f"Product: {r['product_name']} (SKU: {r['sku']}, Category: {r['category']}, "
                f"Marketplace: {r['marketplace'] or 'N/A'}). "
                f"Stock: {r['available_stock'] or 'N/A'} units "
                f"(threshold: {r['reorder_threshold'] or 10}). "
                f"Price: Rs.{r['selling_price'] or 'N/A'}, "
                f"Margin: {r['margin_pct'] or 'N/A'}%. "
                f"Traffic: {r['impressions'] or 0} impressions, "
                f"{r['clicks'] or 0} clicks, {r['ad_orders'] or 0} ad orders, "
                f"ROAS: {r['roas'] or 0}."
            )
            for r in rows
        ]
        metas = [
            {
                "available_stock": r["available_stock"],
                "selling_price":   float(r["selling_price"]) if r["selling_price"] else None,
                "margin_pct":      float(r["margin_pct"]) if r["margin_pct"] else None,
                "roas":            float(r["roas"]) if r["roas"] else None,
            }
            for r in rows
        ]

        # ONE batch model call for all products
        vectors = await embed_batch(summaries)

        # Bulk upsert into Supabase pgvector
        ins = pg_insert(ProductEmbedding).values([
            {
                "seller_id":    seller_id,
                "product_id":   str(rows[i]["product_id"]),
                "embed_date":   snap_date,
                "embed_type":   "daily_snapshot",
                "summary_text": summaries[i],
                "embedding":    vectors[i],
                "meta":         metas[i],
            }
            for i in range(len(rows))
        ])
        stmt = ins.on_conflict_do_update(
            index_elements=["seller_id", "product_id", "embed_date", "embed_type"],
            set_={
                "summary_text": ins.excluded.summary_text,
                "embedding":    ins.excluded.embedding,
                "meta":         ins.excluded.meta,
            },
        )
        await db.execute(stmt)
        await db.commit()

        logger.info("[Embed] seller=%s date=%s embedded=%d", seller_id, snap_date, len(rows))
        return len(rows)


# ── Task 1: Per-upload trigger ─────────────────────────────────
@shared_task(
    name="app.services.tasks.auto_embed",
    bind=True,
    max_retries=3,
    default_retry_delay=30,   # Retry after 30s on failure
    queue="embed",
)
def auto_embed(self, seller_id: str, snap_date: str):
    """
    Triggered automatically after every Excel upload.
    Embeds all products for the given seller and date.

    Usage from FastAPI:
        from app.tasks.embed import auto_embed
        auto_embed.delay(seller_id, snap_date)
    """
    try:
        # Publish "Task Started"
        import redis
        from app.core.config import settings
        import json
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.publish(f"channel:{seller_id}", json.dumps({"event": "embedding_started", "message": f"Embedding products for {snap_date}..."}))
        
        logger.info("[Celery] auto_embed started seller=%s date=%s", seller_id, snap_date)
        count = asyncio.run(_run_embed(seller_id, snap_date))
        logger.info("[Celery] auto_embed done embedded=%d", count)
        
        # Publish "Embedding Complete"
        r.publish(f"channel:{seller_id}", json.dumps({"event": "embedding_complete", "message": f"Successfully embedded {count} products.", "count": count}))

        # Trigger AI Agent simulation automatically after embedding
        from app.services.ai_agent_client import trigger_simulation
        try:
            r.publish(f"channel:{seller_id}", json.dumps({"event": "ai_started", "message": "Triggering AI Board of Directors..."}))
            logger.info("[Celery] Triggering AI multi-agent simulation for seller=%s", seller_id)
            # Create a simple snapshot summary payload
            snapshot_data = {"event": "auto_embed_complete", "date": snap_date, "embedded_count": count}
            
            # Use a slightly older date for time_window_start as a default
            from datetime import date as _date, timedelta
            end_date = _date.fromisoformat(snap_date)
            start_date = end_date - timedelta(days=7)
            
            ai_result = asyncio.run(trigger_simulation(
                seller_id=seller_id,
                time_window_start=str(start_date),
                time_window_end=str(end_date),
                snapshot_data=snapshot_data
            ))
            if ai_result:
                logger.info("[Celery] AI Simulation triggered successfully: %s", ai_result.get("status"))
                r.publish(f"channel:{seller_id}", json.dumps({"event": "ai_complete", "message": "Executive plan ready.", "result": "success"}))
            else:
                logger.warning("[Celery] AI Simulation triggered but returned no valid result.")
                r.publish(f"channel:{seller_id}", json.dumps({"event": "ai_error", "message": "AI failed to generate plan."}))
        except Exception as ai_exc:
            logger.error("[Celery] Failed to trigger AI Simulation: %s", ai_exc)
            r.publish(f"channel:{seller_id}", json.dumps({"event": "ai_error", "message": str(ai_exc)}))

        return {"status": "ok", "embedded": count, "seller_id": seller_id, "date": snap_date}
    except Exception as exc:
        logger.error("[Celery] auto_embed error: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


# ── Task 2: Single product embed (for /ai/embed/product) ───────
@shared_task(
    name="app.services.tasks.embed_single_product",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    queue="embed",
)
def embed_single_product(self, seller_id: str, product_id: str, summary: str, embed_date: str | None = None, embed_type: str = "daily_snapshot"):
    """
    Embed a single product summary.

    Used by /ai/embed/product to offload embedding work to Celery.
    """
    try:
        from datetime import date as _date

        from app.db.session import AsyncSessionLocal
        from app.services.embeddings import embedding_service

        async def _run():
            d = _date.fromisoformat(embed_date) if embed_date else _date.today()
            async with AsyncSessionLocal() as db:
                await embedding_service.upsert_product_embedding(
                    db,
                    seller_id=seller_id,
                    product_id=product_id,
                    summary_text=summary,
                    embed_date=d,
                    embed_type=embed_type,
                )
            return {"status": "ok", "embedded": True, "product_id": product_id, "date": str(d)}

        result = asyncio.run(_run())
        logger.info("[Celery] embed_single_product seller=%s product=%s date=%s", seller_id, product_id, result["date"])
        return result
    except Exception as exc:
        logger.error("[Celery] embed_single_product error: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


# ── Task 3: Nightly batch for ALL sellers ─────────────────────
@shared_task(
    name="app.services.tasks.nightly_embed_all",
    queue="embed",
)
def nightly_embed_all():
    """
    Scheduled by Celery Beat at 2:00 AM IST daily.
    Re-embeds yesterday's snapshot for every seller in the database.
    This ensures the AI memory layer is always up-to-date.
    """
    async def _run():
        from sqlalchemy import text
        from app.db.session import AsyncSessionLocal

        yesterday = str(date.today() - timedelta(days=1))

        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT seller_id FROM sellers"))
            seller_ids = [str(row.seller_id) for row in result.fetchall()]

        logger.info("[Celery] nightly_embed_all: %d sellers for date=%s", len(seller_ids), yesterday)
        results = []
        for sid in seller_ids:
            try:
                count = await _run_embed(sid, yesterday)
                results.append({"seller_id": sid, "embedded": count})
            except Exception as e:
                logger.error("[Celery] nightly embed failed seller=%s: %s", sid, e)
                results.append({"seller_id": sid, "error": str(e)})
        return results

    return asyncio.run(_run())

# ── Task 4: Weekly AI Action Plan (Health Check) ───────────────
@shared_task(
    name="app.services.tasks.weekly_health_check",
    queue="embed",
)
def weekly_health_check():
    """
    Scheduled by Celery Beat at 8:00 AM IST every Monday.
    Scans the database for all active sellers and triggers the AI Board of Directors
    to generate an Executive Action Plan for the previous week's performance.
    """
    async def _run():
        from sqlalchemy import text
        from datetime import date as _date, timedelta
        from app.db.session import AsyncSessionLocal
        from app.services.ai_agent_client import trigger_simulation

        today = _date.today()
        start_date = today - timedelta(days=7)
        end_date = today - timedelta(days=1)
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT seller_id FROM sellers"))
            seller_ids = [str(row.seller_id) for row in result.fetchall()]

        logger.info("[Celery] weekly_health_check: Triggering AI for %d sellers", len(seller_ids))
        results = []
        for sid in seller_ids:
            try:
                # Mock a generic snapshot payload indicating this is a scheduled summary
                snapshot_data = {
                    "event": "weekly_scheduled_review", 
                    "date_range": f"{start_date} to {end_date}",
                    "context": "Automated weekly board review."
                }
                
                ai_result = await trigger_simulation(
                    seller_id=sid,
                    time_window_start=str(start_date),
                    time_window_end=str(end_date),
                    snapshot_data=snapshot_data
                )
                
                if ai_result and ai_result.get("status") == "success":
                    logger.info("[Celery] Weekly AI Plan generated successfully for seller=%s", sid)
                    results.append({"seller_id": sid, "status": "success"})
                else:
                    logger.warning("[Celery] Weekly AI Plan failed for seller=%s", sid)
                    results.append({"seller_id": sid, "status": "failed"})
            except Exception as e:
                logger.error("[Celery] weekly_health_check failed for seller=%s: %s", sid, e)
                results.append({"seller_id": sid, "error": str(e)})

        return results

    return asyncio.run(_run())

# ── Task 5: Ping (for health checks) ───────────────────────────
@shared_task(name="app.services.tasks.ping", queue="embed")
def ping():
    return "pong"

# ── Task 6: Analyze all products (batch AI analysis) ───────────
@shared_task(
    name="app.services.tasks.analyze_all_products",
    queue="embed",
)
def analyze_all_products(seller_id: str, snap_date: str):
    """
    Triggered after auto_embed.
    Analyzes each product using the AI agent, with throttling.
    """
    async def _run():
        from sqlalchemy import text
        from app.db.session import AsyncSessionLocal
        from app.services.ai_agent_client import trigger_product_analysis
        from app.models.models import AIProductAnalysis
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        import asyncio

        # Publish task start
        import redis
        from app.core.config import settings
        import json
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.publish(f"channel:{seller_id}", json.dumps({"event": "ai_product_analysis_started", "message": f"Starting per-product AI analysis for {snap_date}..."}))

        async with AsyncSessionLocal() as db:
            # 1. Fetch all unique products for the seller
            sql = text("""
                SELECT p.product_id, p.sku, p.product_name, p.category, p.marketplace
                FROM products p
                WHERE p.seller_id = :seller_id AND p.is_active = TRUE
            """)
            result = await db.execute(sql, {"seller_id": seller_id})
            products = result.mappings().all()

            logger.info("[Celery] analyze_all_products: found %d products for seller=%s", len(products), seller_id)
            
            analyzed_count = 0
            
            # 2. Iterate and analyze each product
            for prod in products:
                prod_id = str(prod["product_id"])
                product_data = dict(prod)
                product_data["product_id"] = prod_id
                
                try:
                    logger.info("[Celery] Triggering analysis for product %s (%s)", prod_id, prod["product_name"])
                    ai_result = await trigger_product_analysis(seller_id, prod_id, product_data)
                    
                    if ai_result and ai_result.get("status") == "success":
                        result_data = ai_result.get("result", {})
                        
                        # Save to database
                        stmt = pg_insert(AIProductAnalysis).values(
                            seller_id=seller_id,
                            product_id=prod_id,
                            analysis_date=date.fromisoformat(snap_date),
                            product_metrics=product_data,
                            executive_summary=result_data,
                            status="completed"
                        ).on_conflict_do_update(
                            index_elements=["seller_id", "product_id", "analysis_date"],
                            set_={
                                "executive_summary": result_data,
                                "status": "completed",
                                "product_metrics": product_data,
                                "updated_at": text("NOW()")
                            }
                        )
                        await db.execute(stmt)
                        await db.commit()
                        analyzed_count += 1
                        
                        # Emit a granular event so the frontend can update live
                        r.publish(f"channel:{seller_id}", json.dumps({
                            "event": "ai_product_analyzed",
                            "product_id": prod_id,
                            "product_name": prod["product_name"],
                            "message": f"Analyzed {prod['product_name']}"
                        }))
                    
                except Exception as e:
                    logger.error("[Celery] Failed to analyze product %s: %s", prod_id, e)
                
                # Throttle to avoid hitting Groq rate limits (500ms delay)
                await asyncio.sleep(0.5)

        r.publish(f"channel:{seller_id}", json.dumps({
            "event": "ai_product_analysis_complete", 
            "message": f"Completed product analysis for {analyzed_count}/{len(products)} products.",
            "count": analyzed_count
        }))
        
        return {"seller_id": seller_id, "analyzed_count": analyzed_count, "total_products": len(products)}

    return asyncio.run(_run())
