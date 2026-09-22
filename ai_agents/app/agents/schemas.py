from pydantic import BaseModel, Field
from typing import List, Optional

# -------------------------------------------------------------------
# Common Structures
# -------------------------------------------------------------------
class SWOTItem(BaseModel):
    """A single item in the SWOT analysis with full strategic detail."""
    title: str = Field(description="Short headline (e.g., 'Strong Ad Efficiency on Amazon')")
    detail: str = Field(description="2-3 sentence explanation with specific numbers from the data. Reference actual Rs values, percentages, and marketplace names.")
    impact: str = Field(description="Business impact: 'High', 'Medium', or 'Low'")
    metric_value: str = Field(default="", description="The key metric that supports this finding (e.g., 'ROAS: 4.79', 'Margin: 45.6%')")

class RootCauseItem(BaseModel):
    """A root cause that explains WHY a weakness exists — must NOT restate the weakness."""
    cause: str = Field(description="The deep systemic reason (e.g., 'Platform commission structure makes sub-₹500 products unprofitable on Flipkart')")
    linked_weakness: str = Field(description="Which weakness this root cause explains")
    evidence: str = Field(description="Data point that proves this root cause (e.g., 'Commission: 15% + discount: 10% = 25% erosion on ₹499 selling price')")

class ActionItem(BaseModel):
    action_name: str = Field(description="Short title of the recommended action (e.g., 'Reprice Cold Brew on Amazon')")
    reason: str = Field(description="Root cause analysis — WHY this action is needed. Reference specific data points, SKUs, or metrics.")
    strategy: str = Field(description="Step-by-step HOW to implement this action. Be specific and practical for a small D2C team.")
    description: str = Field(description="Detailed explanation of the action and its expected outcome")
    estimated_impact_percentage: float = Field(description="Estimated positive impact on revenue/conversion as a percentage")
    financial_impact_monthly: float = Field(description="Estimated monetary value of this action per month in INR")
    is_profit_safe: bool = Field(description="True only if this action maintains or improves net profit margin after all costs")
    risk_level: str = Field(description="Low, Medium, or High risk associated with this action")
    difficulty: str = Field(description="Low, Medium, or High implementation difficulty for a small D2C team")
    timeframe: str = Field(description="When to execute: 'Immediate' (today), 'This Week', 'This Month', or 'Next Quarter'")


# -------------------------------------------------------------------
# Agent Outputs (Domain Insights)
# -------------------------------------------------------------------

class RevenueInsights(BaseModel):
    """Output schema for the Revenue Intelligence Agent (CFO persona)"""
    conversion_drop_impact_pct: float = Field(default=0.0, description="Percentage impact of conversion drop on overall revenue")
    price_gap_impact_pct: float = Field(default=0.0, description="Percentage impact of competitor pricing gaps")
    stockout_impact_pct: float = Field(default=0.0, description="Percentage impact of out-of-stock items")
    discount_misuse_pct: float = Field(default=0.0, description="Percentage impact of misused or inefficient discounting")
    recommended_actions: List[ActionItem] = Field(description="CFO-approved actions (validated for profit margin)")


class OperationsInsights(BaseModel):
    """Output schema for the Operations & Cost Intelligence Agent (COO persona)"""
    delivery_delay_increase_days: float = Field(default=0.0, description="Average increase in delivery SLA delays")
    return_probability_increase_pct: float = Field(default=0.0, description="Increase in return probability due to operational issues")
    revenue_loss_contribution_pct: float = Field(default=0.0, description="How much of the total revenue loss is driven by operations")
    recommended_actions: List[ActionItem] = Field(description="COO-approved operational fixes (e.g., warehouse SLAs, shipping adjustments)")


class MarketInsights(BaseModel):
    """Output schema for the Customer & Market Intelligence Agent (Brand Strategist persona)"""
    sentiment_drift_topic: str = Field(default="None detected", description="Primary topic of negative sentiment drift (e.g., 'Delivery complaints', 'Quality issues')")
    sentiment_revenue_impact_pct: float = Field(default=0.0, description="Estimated revenue drop contribution from sentiment shifts")
    competitor_shock_detected: bool = Field(default=False, description="True if a major competitor moved prices or launched an aggressive campaign")
    churn_risk_probability: float = Field(default=0.0, description="Probability (0.0 to 1.0) of increased customer churn")
    recommended_actions: List[ActionItem] = Field(description="Brand-approved actions to correct sentiment or market positioning")

class MarketingInsights(BaseModel):
    """Output schema for the Marketing & Growth Intelligence Agent (CMO persona)"""
    inefficient_ad_spend_pct: float = Field(default=0.0, description="Percentage of total ad spend currently yielding negative ROAS or sub-optimal conversion")
    wasted_ad_spend_monthly: float = Field(default=0.0, description="Estimated monetary value of wasted or inefficient ad spend per month (in original currency)")
    primary_traffic_bottleneck: str = Field(default="Insufficient data", description="The main reason traffic isn't converting (e.g., 'Low CTR on main image', 'High bounce rate due to pricing')")
    recommended_campaign_kills: List[str] = Field(default_factory=list, description="Specific campaigns or keyword strategies to pause instantly to save money")
    recommended_actions: List[ActionItem] = Field(description="CMO-approved actions to optimize ROAS, shift budget, or capture competitor traffic")


# -------------------------------------------------------------------
# Final Output (Synthesizer)
# -------------------------------------------------------------------

class ExecutiveActionPlan(BaseModel):
    """Final output from the Synthesizer Agent (CEO persona) combining all insights into a sales growth plan."""
    primary_problem_statement: str = Field(default="Analysis in progress", description="A concise 1-2 sentence summary of the CORE issue holding back sales growth for this D2C brand.")
    quick_wins: List[str] = Field(default_factory=list, description="2-3 specific actions the seller can execute TODAY or within 48 hours to immediately improve sales or stop bleeding money.")
    total_revenue_recovery_potential_pct: float = Field(default=0.0, description="Summed expected revenue recovery/growth percentage from all approved actions.")
    total_financial_recovery_monthly: float = Field(default=0.0, description="Estimated total additional monthly revenue in INR from implementing all actions.")
    ranked_actions: List[ActionItem] = Field(default_factory=list, description="The finalized, merged list of actions ranked by ROI and urgency. MUST eliminate redundant suggestions. Each action must have a clear reason, strategy, and timeframe.")
    confidence_score: float = Field(default=0.5, description="Confidence score (0.0 to 1.0) in this overall strategy based on data completeness and quality.")

class ProductAnalysisResult(BaseModel):
    """Final output for per-product analysis."""
    product_health_score: float = Field(default=50.0, description="Health score from 0.0 to 100.0 based on performance and metrics.")
    performance_verdict: str = Field(default="Needs Review", description="'Strong Performer' | 'Underperformer' | 'At Risk' | 'Growth Opportunity'")
    primary_observation: str = Field(default="Insufficient data for full analysis", description="1-2 sentence headline observation summarizing the core finding for this product.")
    strengths: List[SWOTItem] = Field(default_factory=list, description="What's working well for this product based on data.")
    weaknesses: List[SWOTItem] = Field(default_factory=list, description="What's hurting this product based on data.")
    root_causes: List[RootCauseItem] = Field(default_factory=list, description="WHY performance is good/bad based on deep analysis.")
    recommendations: List[ActionItem] = Field(default_factory=list, description="Specific, ranked actions tailored to improving THIS product.")
    cross_marketplace_summary: str = Field(default="Multi-channel analysis pending", description="Narrative summarizing how this product performs across different channels.")
    confidence_score: float = Field(default=0.5, description="Confidence score (0.0 to 1.0) for this product's analysis.")
