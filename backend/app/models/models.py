"""SQLAlchemy ORM models for all CommercePulse tables."""
import uuid
from datetime import date, datetime
from typing import Optional

try:
    from pgvector.sqlalchemy import Vector as _Vector
    _VECTOR_AVAILABLE = True
except ImportError:
    _VECTOR_AVAILABLE = False

from sqlalchemy import ARRAY, Float

def Vector(dims: int):
    """Returns pgvector Vector type if available, else ARRAY(Float) fallback."""
    if _VECTOR_AVAILABLE:
        return _Vector(dims)
    return ARRAY(Float)
from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, BigInteger, JSON,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


# ── helpers ────────────────────────────────────────────────────
def now():
    return datetime.utcnow()

def new_uuid():
    return str(uuid.uuid4())


# ── Seller ─────────────────────────────────────────────────────
class Seller(Base):
    __tablename__ = "sellers"

    seller_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_name = Column(Text, nullable=False, index=True)
    marketplace = Column(Text, nullable=False, default="multi")
    region      = Column(Text, nullable=False, default="IN")
    email       = Column(Text, unique=True, index=True)
    is_active   = Column(Boolean, nullable=False, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    products   = relationship("Product", back_populates="seller", lazy="selectin")


# ── Product ────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("seller_id", "sku", "marketplace"),)

    product_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id    = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    sku          = Column(Text, nullable=False, index=True)
    product_name = Column(Text, nullable=False, index=True)
    category     = Column(Text, index=True)
    sub_category = Column(Text)
    brand        = Column(Text)
    marketplace  = Column(Text)
    is_active    = Column(Boolean, nullable=False, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    seller     = relationship("Seller", back_populates="products")


# ── Order ──────────────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    order_id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_order_id   = Column(Text, unique=True, index=True)  # must be unique for ON CONFLICT upsert
    seller_id           = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id          = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="SET NULL"), index=True)
    marketplace         = Column(Text, nullable=False, index=True)
    order_status        = Column(Text, nullable=False, index=True)
    quantity            = Column(Integer, nullable=False, default=1)
    selling_price       = Column(Numeric(12, 2), nullable=False)
    discount            = Column(Numeric(12, 2), default=0)
    tax                 = Column(Numeric(12, 2), default=0)
    shipping_fee        = Column(Numeric(12, 2), nullable=True, default=0)
    order_date          = Column(Date, nullable=False, index=True)
    delivery_date       = Column(Date)
    return_flag         = Column(Boolean, default=False, index=True)
    cancellation_reason = Column(Text)
    customer_name       = Column(Text)    # may be NULL if dataset lacks this column
    customer_email      = Column(Text)
    payment_mode        = Column(Text)
    snapshot_date       = Column(Date, nullable=False, default=date.today, index=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())


# ── InventorySnapshot ──────────────────────────────────────────
class InventorySnapshot(Base):
    __tablename__  = "inventory_snapshots"
    __table_args__ = (UniqueConstraint("seller_id", "product_id", "marketplace", "snapshot_date"),)

    id                = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id         = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id        = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, index=True)
    marketplace       = Column(Text, nullable=False, index=True)
    available_stock   = Column(Integer, nullable=False, default=0)
    reserved_stock    = Column(Integer, nullable=False, default=0)
    reorder_threshold = Column(Integer, default=10)
    days_of_stock     = Column(Numeric(6, 1))
    warehouse_location= Column(Text)
    snapshot_date     = Column(Date, nullable=False, default=date.today, index=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())


# ── PricingSnapshot ────────────────────────────────────────────
class PricingSnapshot(Base):
    __tablename__  = "pricing_snapshots"
    __table_args__ = (UniqueConstraint("seller_id", "product_id", "marketplace", "snapshot_date"),)

    id                  = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id           = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id          = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, index=True)
    marketplace         = Column(Text, nullable=False, index=True)
    selling_price       = Column(Numeric(12, 2), nullable=False)
    cost_price          = Column(Numeric(12, 2))
    mrp                 = Column(Numeric(12, 2))
    commission_pct      = Column(Numeric(5, 2), default=0)
    commission_amount   = Column(Numeric(12, 2), default=0)
    discount_percentage = Column(Numeric(5, 2), default=0)
    snapshot_date       = Column(Date, nullable=False, default=date.today, index=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())


# ── TrafficMetric ──────────────────────────────────────────────
class TrafficMetric(Base):
    __tablename__  = "traffic_metrics"
    __table_args__ = (UniqueConstraint("seller_id", "product_id", "marketplace", "metric_date"),)

    id               = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id        = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id       = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, index=True)
    marketplace      = Column(Text, nullable=False, index=True)
    metric_date      = Column(Date, nullable=False, default=date.today, index=True)
    impressions      = Column(Integer, default=0)
    clicks           = Column(Integer, default=0)
    sessions         = Column(Integer, default=0)
    page_views       = Column(Integer, default=0)
    orders           = Column(Integer, default=0)
    ad_spend         = Column(Numeric(12, 2), default=0)
    revenue_from_ads = Column(Numeric(12, 2), default=0)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())


# ── LogisticsMetric ────────────────────────────────────────────
class LogisticsMetric(Base):
    __tablename__ = "logistics_metrics"
    __table_args__ = (UniqueConstraint("seller_id", "tracking_id", "marketplace", "snapshot_date"),)

    id                 = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id           = Column(UUID(as_uuid=True), ForeignKey("orders.order_id", ondelete="SET NULL"))
    seller_id          = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False)
    marketplace        = Column(Text, nullable=False)
    courier_name       = Column(Text)
    tracking_id        = Column(Text)
    fulfillment_type   = Column(Text, default="seller")
    warehouse_id       = Column(Text)
    dispatch_date      = Column(Date)
    expected_delivery  = Column(Date)
    actual_delivery    = Column(Date)
    delivery_status    = Column(Text, nullable=False)
    rto_flag           = Column(Boolean, default=False)
    rto_reason         = Column(Text)
    snapshot_date      = Column(Date, nullable=False, default=date.today)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())


# ── ProductEmbedding ──────────────────────────────────────────
class ProductEmbedding(Base):
    __tablename__  = "product_embeddings"
    __table_args__ = (UniqueConstraint("seller_id", "product_id", "embed_date", "embed_type"),)

    id           = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id    = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False)
    product_id   = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    embed_date   = Column(Date, nullable=False, default=date.today)
    embed_type   = Column(Text, nullable=False, default="daily_snapshot")
    summary_text = Column(Text, nullable=False)
    embedding    = Column(Vector(384), nullable=True)
    meta         = Column("metadata", JSON, default=dict)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())


# ── InsightEmbedding ──────────────────────────────────────────
class InsightEmbedding(Base):
    __tablename__ = "insight_embeddings"

    id           = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id    = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False)
    insight_date = Column(Date, nullable=False, default=date.today)
    insight_type = Column(Text, nullable=False)
    insight_text = Column(Text, nullable=False)
    embedding    = Column(Vector(384), nullable=True)
    meta         = Column("metadata", JSON, default=dict)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())


# ── AIProductAnalysis ──────────────────────────────────────────
class AIProductAnalysis(Base):
    __tablename__  = "ai_product_analyses"
    __table_args__ = (UniqueConstraint("seller_id", "product_id", "analysis_date"),)

    id                 = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id          = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False)
    product_id         = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    analysis_date      = Column(Date, nullable=False, default=date.today)
    
    product_metrics    = Column(JSON, nullable=False, default=dict)
    revenue_insights   = Column(JSON)
    ops_insights       = Column(JSON)
    marketing_insights = Column(JSON)
    market_insights    = Column(JSON)
    executive_summary  = Column(JSON)
    
    status             = Column(Text, nullable=False, default="pending")
    error_message      = Column(Text)
    
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    updated_at         = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ── Payments / reconciliation (reconnAIssance engine, Brew Boulevard cash) ─
class PaymentLedgerRow(Base):
    __tablename__ = "payment_ledger_row"

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id       = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    order_id        = Column(Text, nullable=False, index=True)
    product_id      = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="SET NULL"), index=True)
    sku             = Column(Text, index=True)
    marketplace     = Column(Text)
    order_date      = Column(Date, nullable=False, index=True)
    amount_paise    = Column(Integer, nullable=False)
    payment_method  = Column(Text)
    status          = Column(Text)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())


class PaymentSettlementRow(Base):
    __tablename__ = "payment_settlement_row"

    id                    = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id             = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    settlement_batch_id   = Column(Text, nullable=False, index=True)
    utr                   = Column(Text, index=True)
    order_ref             = Column(Text, nullable=False, index=True)
    sku                   = Column(Text, index=True)
    product_id            = Column(UUID(as_uuid=True), index=True)
    gross_amount_paise    = Column(Integer, nullable=False)
    fee_amount_paise      = Column(Integer, nullable=False)
    gst_on_fee_paise      = Column(Integer, nullable=False)
    net_amount_paise      = Column(Integer, nullable=False)
    settlement_date       = Column(Date, nullable=False, index=True)
    created_at            = Column(DateTime(timezone=True), server_default=func.now())


class PaymentBankRow(Base):
    __tablename__ = "payment_bank_row"

    id                   = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id            = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    bank_txn_id          = Column(Text, nullable=False, index=True)
    value_date           = Column(Date, nullable=False, index=True)
    credit_amount_paise  = Column(Integer, nullable=False)
    narration            = Column(Text, nullable=False)
    created_at           = Column(DateTime(timezone=True), server_default=func.now())


class PaymentReconRun(Base):
    __tablename__ = "payment_recon_run"

    id               = Column(Text, primary_key=True)
    seller_id        = Column(UUID(as_uuid=True), ForeignKey("sellers.seller_id", ondelete="CASCADE"), nullable=False, index=True)
    status           = Column(Text, nullable=False, default="running", index=True)
    started_at       = Column(DateTime(timezone=True), server_default=func.now())
    completed_at     = Column(DateTime(timezone=True))
    record_count     = Column(Integer, default=0)
    match_rate       = Column(Numeric(8, 4), default=0)
    exact_matches    = Column(Integer, default=0)
    fuzzy_matches    = Column(Integer, default=0)
    ai_matches       = Column(Integer, default=0)
    exception_count  = Column(Integer, default=0)
    error_message    = Column(Text)


class PaymentCanonical(Base):
    __tablename__ = "payment_canonical"

    id              = Column(Text, primary_key=True)
    run_id          = Column(Text, ForeignKey("payment_recon_run.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id       = Column(UUID(as_uuid=True), nullable=False, index=True)
    source          = Column(Text, nullable=False, index=True)
    source_row_id   = Column(BigInteger, nullable=False)
    normalized_ref  = Column(Text, nullable=False, index=True)
    amount_paise    = Column(Integer, nullable=False)
    event_date      = Column(Date, nullable=False)
    batch_id        = Column(Text, index=True)
    sku             = Column(Text, index=True)
    product_id      = Column(UUID(as_uuid=True), index=True)
    raw_payload     = Column(JSON, default=dict)


class PaymentMatchGroup(Base):
    __tablename__ = "payment_match_group"

    id          = Column(Text, primary_key=True)
    run_id      = Column(Text, ForeignKey("payment_recon_run.id", ondelete="CASCADE"), nullable=False, index=True)
    tier        = Column(Text, nullable=False, index=True)
    confidence  = Column(Numeric(6, 4), nullable=False)
    reason      = Column(Text, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class PaymentMatchMember(Base):
    __tablename__ = "payment_match_member"

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id        = Column(Text, ForeignKey("payment_match_group.id", ondelete="CASCADE"), nullable=False, index=True)
    canonical_id    = Column(Text, ForeignKey("payment_canonical.id", ondelete="CASCADE"), nullable=False, index=True)
    role            = Column(Text, nullable=False)


class PaymentException(Base):
    __tablename__ = "payment_exception"

    id              = Column(Text, primary_key=True)
    run_id          = Column(Text, ForeignKey("payment_recon_run.id", ondelete="CASCADE"), nullable=False, index=True)
    canonical_id    = Column(Text, ForeignKey("payment_canonical.id", ondelete="CASCADE"), nullable=False, index=True)
    reason_code     = Column(Text, nullable=False, index=True)
    reason_text     = Column(Text, nullable=False)
    unresolved_after_tier = Column(Text, default="ai_assisted")


class PaymentAuditLog(Base):
    __tablename__ = "payment_audit_log"

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    run_id          = Column(Text, ForeignKey("payment_recon_run.id", ondelete="CASCADE"), nullable=False, index=True)
    canonical_id    = Column(Text, index=True)
    group_id        = Column(Text, index=True)
    tier            = Column(Text, nullable=False, index=True)
    action          = Column(Text, nullable=False)
    confidence      = Column(Numeric(6, 4))
    reason          = Column(Text)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
