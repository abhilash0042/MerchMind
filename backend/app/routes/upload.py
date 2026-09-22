import io
import logging
from datetime import date
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import rate_limiter, enforce_seller_scope
from app.services import ingestion

router = APIRouter(
    dependencies=[Depends(rate_limiter(max_requests=60, window_seconds=60))],
)
logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/octet-stream",
    "text/csv"
}

def _validate_excel(file: UploadFile):
    if file.content_type not in ALLOWED_CONTENT_TYPES and not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx, .xls, and .csv files are accepted.")


async def _trigger_embed(seller_id: str, snap_date: date):
    """
    Fire-and-forget: enqueue the Celery embedding task.
    If Redis/Celery is down, fall back to a local asyncio background task.
    """
    import asyncio
    from app.services.tasks import auto_embed, _run_embed
    
    try:
        # 1. Try Celery (distributed)
        auto_embed.delay(seller_id, str(snap_date))
        logger.info("[Upload] Enqueued Celery auto_embed for %s", seller_id)
    except Exception as e:
        # 2. Fallback to local background task (asyncio)
        logger.warning("[Upload] Redis/Celery unavailable, using local task fallback: %s", e)
        # We wrap the async logic in a background task so we don't block the response
        asyncio.create_task(_run_embed(seller_id, str(snap_date)))
        logger.info("[Upload] Started local background _run_embed for %s", seller_id)


def _parse_file_to_df(file: UploadFile, content: bytes) -> pd.DataFrame:
    import io
    import pandas as pd
    if file.filename.endswith(".csv") or file.content_type == "text/csv":
        return pd.read_csv(io.BytesIO(content))
    return pd.read_excel(io.BytesIO(content), engine="openpyxl")

# ── Orders ─────────────────────────────────────────────────────
@router.post("/orders", summary="Upload Orders Excel sheet")
async def upload_orders(
    seller_id:     str           = Form(..., description="Seller UUID"),
    snapshot_date: Optional[str] = Form(None, description="Snapshot date YYYY-MM-DD (default: today)"),
    file:          UploadFile    = File(...),
    db:            AsyncSession  = Depends(get_db),
    _scope:        str           = Depends(enforce_seller_scope),
):
    _validate_excel(file)
    snap_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()
    content = await file.read()
    df = _parse_file_to_df(file, content)
    result  = await ingestion.ingest_orders(db, df, seller_id, snap_date)
    await _trigger_embed(seller_id, snap_date)   # ← async background embedding
    return {"status": "ok", **result, "snapshot_date": str(snap_date), "embedding": "queued"}


# ── Inventory ──────────────────────────────────────────────────
@router.post("/inventory", summary="Upload Inventory Excel sheet")
async def upload_inventory(
    seller_id:     str           = Form(...),
    snapshot_date: Optional[str] = Form(None),
    file:          UploadFile    = File(...),
    db:            AsyncSession  = Depends(get_db),
    _scope:        str           = Depends(enforce_seller_scope),
):
    _validate_excel(file)
    snap_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()
    content = await file.read()
    df = _parse_file_to_df(file, content)
    result  = await ingestion.ingest_inventory(db, df, seller_id, snap_date)
    await _trigger_embed(seller_id, snap_date)   # ← async background embedding
    return {"status": "ok", **result, "snapshot_date": str(snap_date), "embedding": "queued"}


# ── Pricing ────────────────────────────────────────────────────
@router.post("/pricing", summary="Upload Pricing Excel sheet")
async def upload_pricing(
    seller_id:     str           = Form(...),
    snapshot_date: Optional[str] = Form(None),
    file:          UploadFile    = File(...),
    db:            AsyncSession  = Depends(get_db),
    _scope:        str           = Depends(enforce_seller_scope),
):
    _validate_excel(file)
    snap_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()
    content = await file.read()
    df = _parse_file_to_df(file, content)
    result  = await ingestion.ingest_pricing(db, df, seller_id, snap_date)
    await _trigger_embed(seller_id, snap_date)   # ← async background embedding
    return {"status": "ok", **result, "snapshot_date": str(snap_date), "embedding": "queued"}


# ── Traffic & Ads ──────────────────────────────────────────────
@router.post("/traffic", summary="Upload Traffic & Ads Excel sheet")
async def upload_traffic(
    seller_id:     str           = Form(...),
    snapshot_date: Optional[str] = Form(None),
    file:          UploadFile    = File(...),
    db:            AsyncSession  = Depends(get_db),
    _scope:        str           = Depends(enforce_seller_scope),
):
    _validate_excel(file)
    snap_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()
    content = await file.read()
    df = _parse_file_to_df(file, content)
    result  = await ingestion.ingest_traffic(db, df, seller_id, snap_date)
    await _trigger_embed(seller_id, snap_date)   # ← async background embedding
    return {"status": "ok", **result, "snapshot_date": str(snap_date), "embedding": "queued"}


# ── Logistics ──────────────────────────────────────────────────
@router.post("/logistics", summary="Upload Logistics Excel sheet")
async def upload_logistics(
    seller_id:     str           = Form(...),
    snapshot_date: Optional[str] = Form(None),
    file:          UploadFile    = File(...),
    db:            AsyncSession  = Depends(get_db),
    _scope:        str           = Depends(enforce_seller_scope),
):
    _validate_excel(file)
    snap_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()
    content = await file.read()
    df = _parse_file_to_df(file, content)
    result  = await ingestion.ingest_logistics(db, df, seller_id, snap_date)
    await _trigger_embed(seller_id, snap_date)   # ← async background embedding
    return {"status": "ok", **result, "snapshot_date": str(snap_date), "embedding": "queued"}


# ── Full multi-sheet upload ────────────────────────────────────
@router.post("/full", summary="Upload a single Excel file with multiple sheets (one per domain)")
async def upload_full(
    seller_id:     str           = Form(...),
    snapshot_date: Optional[str] = Form(None),
    file:          UploadFile    = File(...),
    db:            AsyncSession  = Depends(get_db),
    _scope:        str           = Depends(enforce_seller_scope),
):
    """
    Expects an Excel workbook with up to 5 sheets named:
    Orders, Inventory, Pricing, Traffic, Logistics (case-insensitive).
    Embedding is triggered once after all sheets are processed.
    """
    import io
    import pandas as pd

    _validate_excel(file)
    snap_date = date.fromisoformat(snapshot_date) if snapshot_date else date.today()
    content = await file.read()

    results = {}
    DOMAIN_MAP = {
        "orders":    ingestion.ingest_orders,
        "inventory": ingestion.ingest_inventory,
        "pricing":   ingestion.ingest_pricing,
        "traffic":   ingestion.ingest_traffic,
        "logistics": ingestion.ingest_logistics,
    }
    CASH_ALIASES = {
        "settlements": ("settlements", "settlement", "razorpay", "stl"),
        "bank": ("bank", "bank statement", "bank_credits"),
    }

    try:
        # If it's a CSV, it's just a single sheet.
        if file.filename.endswith(".csv") or file.content_type == "text/csv":
            try:
                df = pd.read_csv(io.BytesIO(content))
                
                # Infer domain
                cols = set(str(c).strip().lower() for c in df.columns)
                inferred = "orders"
                if "available stock" in cols or "available_stock" in cols or "stock" in cols:
                    inferred = "inventory"
                elif "cost price" in cols or "cost_price" in cols or "mrp" in cols:
                    inferred = "pricing"
                elif "impressions" in cols or "page views" in cols or "ad spend" in cols:
                    inferred = "traffic"
                elif "tracking id" in cols or "courier" in cols or "rto" in cols:
                    inferred = "logistics"
                    
                results[inferred] = await DOMAIN_MAP[inferred](db, df, seller_id, snap_date)
                
            except Exception as e:
                logger.error("[Upload] CSV processing failed: %s", e, exc_info=True)
                raise HTTPException(400, f"Failed to read CSV: {e}")
                
        else:
            # Excel file processing (offload to thread pool to avoid blocking event loop)
            from fastapi.concurrency import run_in_threadpool
            
            def _parse_excel_sync(bytes_content):
                return pd.ExcelFile(io.BytesIO(bytes_content), engine="openpyxl")
            
            xl = await run_in_threadpool(_parse_excel_sync, content)
            sheet_names_lower = {s.strip().lower(): s for s in xl.sheet_names}
            found_any = False
            
            for domain, fn in DOMAIN_MAP.items():
                if domain in sheet_names_lower:
                    found_any = True
                    # Parsing sheets can also be slow, offload it
                    sheet_df = await run_in_threadpool(xl.parse, sheet_names_lower[domain])
                    results[domain] = await fn(db, sheet_df, seller_id, snap_date)

            if not found_any and len(xl.sheet_names) == 1:
                # Bug 7 Fix: was synchronous — offload to thread pool to avoid blocking event loop
                sheet_df = await run_in_threadpool(xl.parse, xl.sheet_names[0])
                cols = set(str(c).strip().lower() for c in sheet_df.columns)
                
                inferred = "orders"
                if "available stock" in cols or "available_stock" in cols or "stock" in cols:
                    inferred = "inventory"
                elif "cost price" in cols or "cost_price" in cols or "mrp" in cols:
                    inferred = "pricing"
                elif "impressions" in cols or "page views" in cols or "ad spend" in cols:
                    inferred = "traffic"
                elif "tracking id" in cols or "courier" in cols or "rto" in cols:
                    inferred = "logistics"
                    
                    results[inferred] = await DOMAIN_MAP[inferred](db, sheet_df, seller_id, snap_date)

            from app.services.payments import ingest as payment_ingest
            cash_found = False
            for cash_key, aliases in CASH_ALIASES.items():
                for alias in aliases:
                    if alias in sheet_names_lower:
                        cash_found = True
                        sheet_df = await run_in_threadpool(xl.parse, sheet_names_lower[alias])
                        if cash_key == "settlements":
                            results["settlements"] = await payment_ingest.ingest_settlements(db, sheet_df, seller_id)
                        else:
                            results["bank"] = await payment_ingest.ingest_bank(db, sheet_df, seller_id)
                        break
            if cash_found:
                found_any = True

        if not results:
            raise HTTPException(400, "No recognizable sheets found. Expected: Orders, Inventory, Pricing, Traffic, Logistics, Settlements, Bank")

        if "orders" in results and "settlements" not in results:
            try:
                from app.services.payments.seed import seed_cash_from_orders
                results["payments_seed"] = await seed_cash_from_orders(db, seller_id)
            except Exception as seed_err:
                logger.warning("[Upload] Auto cash seed skipped: %s", seed_err)

        # Trigger one embed job for all domains processed
        logger.info("[Upload] Finished multi-sheet processing, triggering embedding.")
        await _trigger_embed(seller_id, snap_date)

        return {"status": "ok", "results": results, "snapshot_date": str(snap_date), "embedding": "queued"}
    except Exception as e:
        logger.error("[Upload] Full upload failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
