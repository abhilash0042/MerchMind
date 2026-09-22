import { useState, useEffect } from "react";
import { useParams, Link } from "react-router";
import { 
  ArrowLeft, Brain, TrendingUp, ShieldAlert, CheckCircle2, AlertTriangle, 
  Target, Globe, Lightbulb, Activity, ShoppingCart, Truck, RotateCcw,
  IndianRupee, MousePointerClick, Package, BarChart3, Store, Sparkles, Loader2
} from "lucide-react";
import { getProductAnalysis, ensureSeller, triggerProductAnalysis, getProductMetrics, getProductPayments } from "../services/api";

export function AIProductAnalysisPage() {
  const { id: productId } = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const [productDetails, setProductDetails] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  const [cash, setCash] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, [productId]);

  const loadData = async () => {
    if (!productId) return;
    try {
      setLoading(true);
      const sellerId = await ensureSeller();
      
      // Always fetch live metrics so we don't show stale/zeroed DB metrics
      try {
        const metricsData = await getProductMetrics(sellerId, productId);
        setProductDetails(metricsData);
      } catch (e) {
        console.error("Metrics fetch failed", e);
      }

      try {
        const cashData = await getProductPayments(sellerId, productId);
        setCash(cashData);
      } catch (e) {
        console.warn("Payments strip unavailable", e);
      }

      const res = await getProductAnalysis(sellerId, productId);
      if (res.status === 'success') {
        setData(res.data);
      }
    } catch (error) {
      console.error("Failed to load product analysis:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartAnalysis = async () => {
    if (!productId) return;
    try {
      setIsAnalyzing(true);
      const sellerId = await ensureSeller();
      await triggerProductAnalysis(sellerId, productId);
      await loadData();
    } catch (error: any) {
      console.error("Failed to trigger analysis:", error);
      alert(error.response?.data?.detail || "The AI Agent service is currently unreachable or failed to process this request. Please ensure the AI server is running on port 8001.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#0a0a1a] -m-8">
        <div className="w-16 h-16 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
      </div>
    );
  }

  if (!data && !productDetails) {
    return (
      <div className="min-h-screen bg-[#0a0a1a] text-white -m-8 p-8">
        <Link to="/ai/intelligence" className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 mb-8 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Intelligence Grid
        </Link>
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 text-center max-w-2xl mx-auto">
          <Brain className="w-16 h-16 text-purple-500/50 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Product Not Found</h2>
          <p className="text-purple-200/60 mb-6">We couldn't retrieve metadata for this product.</p>
          <Link to="/ai/intelligence" className="px-6 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg font-medium transition-colors">
            Return to Grid
          </Link>
        </div>
      </div>
    );
  }

  const hasAnalysis = !!(data && data.executive_summary);
  const metrics = productDetails || data?.product_metrics || {
    product_name: "Whole Bean Coffee",
    sku: "",
    category: "Coffee",
    total_revenue: 0,
    total_orders: 0,
    margin_pct: 0,
    stock_level: 0,
    roas: 0,
  };
  const ai = data?.executive_summary || {};
  const recommendations = ai.recommendations || [];

  // Determine colors based on health score
  const score = hasAnalysis ? (ai.product_health_score || 0) : null;
  let themeColor = "purple";
  if (score !== null) {
    if (score >= 80) themeColor = "emerald";
    else if (score >= 50) themeColor = "amber";
    else themeColor = "rose";
  }

  const themeMap: Record<string, any> = {
    emerald: { 
      from: "from-emerald-900/40", 
      bg: "bg-emerald-500/10", 
      text: "text-emerald-400", 
      glow: "shadow-[0_0_30px_rgba(52,211,153,0.3)]" 
    },
    amber: { 
      from: "from-amber-900/40", 
      bg: "bg-amber-500/10", 
      text: "text-amber-400", 
      glow: "shadow-[0_0_30px_rgba(251,191,36,0.3)]" 
    },
    rose: { 
      from: "from-rose-900/40", 
      bg: "bg-rose-500/10", 
      text: "text-rose-400", 
      glow: "shadow-[0_0_30px_rgba(244,63,94,0.3)]" 
    },
    purple: { 
      from: "from-purple-900/40", 
      bg: "bg-purple-500/10", 
      text: "text-purple-400", 
      glow: "shadow-[0_0_30px_rgba(168,85,247,0.3)]" 
    }
  };

  const theme = themeMap[themeColor] || themeMap.purple;

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white -m-8 font-sans">
      {/* Header section with gradient background */}
      <div className={`bg-gradient-to-br ${theme.from} via-[#0a0a1a] to-black pt-8 px-8 pb-12 border-b border-white/10 relative overflow-hidden`}>
        <div className={`absolute top-0 right-0 w-[500px] h-[500px] ${theme.bg} rounded-full blur-[100px] pointer-events-none`} />
        
        <div className="max-w-6xl mx-auto relative z-10">
          <Link to="/ai/intelligence" className="inline-flex items-center gap-2 text-white/50 hover:text-white mb-6 transition-colors text-sm font-medium uppercase tracking-wider">
            <ArrowLeft className="w-4 h-4" /> AI Intelligence Grid
          </Link>
          
          <div className="flex items-end justify-between">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <span className="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold uppercase tracking-wider border border-white/5 backdrop-blur-md">
                  {metrics.category}
                </span>
                <span className="text-sm font-mono text-white/50">{metrics.sku}</span>
              </div>
              <h1 className="text-4xl font-bold tracking-tight mb-2">
                {(() => {
                  if (!metrics.sku) return metrics.product_name;
                  if (metrics.product_name !== metrics.sku) return metrics.product_name;
                  if (metrics.sku.includes('BB-WB')) return "Brew Boulevard Whole Bean Coffee (250g)";
                  if (metrics.sku.includes('BB-GR')) return "Brew Boulevard Ground Roast Coffee (500g)";
                  if (metrics.sku.includes('BB-CB')) return "Brew Boulevard Cold Brew Blend (1L)";
                  if (metrics.sku.includes('BB-IN')) return "Brew Boulevard Premium Instant Coffee (100g)";
                  return metrics.product_name;
                })()}
              </h1>
              <p className="text-xl text-white/70 max-w-2xl">{ai.primary_observation || "No active AI diagnostics. Start the intelligence cycle to run multi-agent inference."}</p>
            </div>
            
            <div className="flex gap-6 items-center">
              <div className="flex flex-col gap-2 items-end mr-4">
                {hasAnalysis ? (
                  <button
                    onClick={async () => {
                      try {
                        setLoading(true);
                        const sellerId = await ensureSeller();
                        await triggerProductAnalysis(sellerId, productId!);
                        await loadData();
                      } catch (err) {
                        console.error(err);
                        setLoading(false);
                      }
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-bold text-white transition-all"
                  >
                    <Sparkles className="w-4 h-4" /> RE-ANALYZE
                  </button>
                ) : (
                  <button
                    onClick={handleStartAnalysis}
                    disabled={isAnalyzing}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 border border-purple-500/30 rounded-lg text-sm font-bold text-white transition-all disabled:opacity-50 shadow-[0_0_15px_rgba(168,85,247,0.4)]"
                  >
                    {isAnalyzing ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Sparkles className="w-4 h-4" />
                    )}
                    {isAnalyzing ? "ANALYZING" : "START ANALYSIS"}
                  </button>
                )}
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-white/50 uppercase tracking-widest mb-1">Health Score</p>
                <div className={`text-6xl font-black ${theme.text} ${theme.glow}`}>
                  {score !== null ? score : "--"}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-8 space-y-8">
        
        {/* Business KPI Dashboard */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { icon: IndianRupee, label: 'Total Revenue', value: `₹${metrics.total_revenue?.toLocaleString()}`, color: 'cyan' },
            { icon: ShoppingCart, label: 'Avg Order Value', value: `₹${metrics.avg_order_value?.toLocaleString() || '0'}`, color: 'purple' },
            { icon: MousePointerClick, label: 'Ad Spend', value: `₹${metrics.total_ad_spend?.toLocaleString() || '0'}`, color: 'amber' },
            { icon: Target, label: 'ROAS', value: metrics.roas || '0', color: (metrics.roas || 0) >= 3 ? 'emerald' : 'rose' },
            { icon: RotateCcw, label: 'Return Rate', value: `${metrics.return_rate_pct || 0}%`, color: (metrics.return_rate_pct || 0) > 5 ? 'rose' : 'emerald' },
            { icon: Package, label: 'Stock Level', value: `${metrics.stock_level || 0} units`, color: 'cyan' },
            { icon: Truck, label: 'Avg Delivery', value: `${metrics.avg_delivery_days || 0} days`, color: (metrics.avg_delivery_days || 0) > 5 ? 'rose' : 'emerald' },
            { icon: BarChart3, label: 'Click-Through', value: `${metrics.ctr_pct || 0}%`, color: 'purple' },
          ].map((kpi, i) => {
            const Icon = kpi.icon;
            const colorMap: Record<string, string> = { cyan: 'text-cyan-400', emerald: 'text-emerald-400', amber: 'text-amber-400', purple: 'text-purple-400', rose: 'text-rose-400' };
            return (
              <div key={i} className="bg-white/5 border border-white/10 rounded-2xl p-5 backdrop-blur-xl hover:bg-white/8 transition-all duration-200 shadow-lg group">
                <p className="text-[11px] text-white/50 uppercase tracking-wider mb-2 flex items-center gap-2 font-semibold">
                  <Icon className={`w-4 h-4 ${colorMap[kpi.color] || 'text-white/50'}`} /> {kpi.label}
                </p>
                <p className={`text-2xl font-mono font-bold ${colorMap[kpi.color] || 'text-white'}`}>{kpi.value}</p>
              </div>
            );
          })}
        </div>

        {cash && cash.order_count > 0 && (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-white/60">Payments analysis</h3>
              <Link to="/payments" className="text-xs text-purple-300 hover:text-purple-200">Open Settlements</Link>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-white/40 mb-1">Sold (ledger)</p>
                <p className="text-xl font-mono font-bold text-cyan-300">₹{cash.sold_rupees?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-white/40 mb-1">Settled (Razorpay)</p>
                <p className="text-xl font-mono font-bold text-emerald-300">₹{cash.settled_rupees?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-white/40 mb-1">Unmatched</p>
                <p className="text-xl font-mono font-bold text-rose-300">₹{cash.exception_rupees?.toLocaleString()}</p>
              </div>
            </div>
            <p className="text-xs text-white/40 mt-3">
              {cash.exception_count || 0} cash exceptions on this SKU after 2% MDR + GST. Same orders as product analysis.
            </p>
          </div>
        )}

        {/* Per-Marketplace P&L Breakdown */}
        {metrics.pricing_by_marketplace && metrics.pricing_by_marketplace.length > 0 && (
          <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl shadow-xl">
            <div className="mb-6 flex items-center gap-3">
              <Store className="w-6 h-6 text-cyan-400" />
              <h3 className="text-xl font-bold text-white">Per-Marketplace Unit Economics</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    {['Channel', 'Selling Price', 'Cost Price', 'MRP', 'Commission %', 'Discount %', 'Net Margin %', 'Profit/Unit'].map(h => (
                      <th key={h} className="text-left py-3 px-4 text-[11px] uppercase tracking-wider text-white/40 font-bold">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {metrics.pricing_by_marketplace.map((mp: any, idx: number) => (
                    <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4 font-semibold text-white">{mp.marketplace}</td>
                      <td className="py-3 px-4 font-mono text-white/80">₹{mp.selling_price?.toLocaleString()}</td>
                      <td className="py-3 px-4 font-mono text-white/80">₹{mp.cost_price?.toLocaleString()}</td>
                      <td className="py-3 px-4 font-mono text-white/60">₹{mp.mrp?.toLocaleString()}</td>
                      <td className="py-3 px-4 font-mono text-amber-400">{mp.commission_pct}%</td>
                      <td className="py-3 px-4 font-mono text-rose-400">{mp.discount_percentage}%</td>
                      <td className={`py-3 px-4 font-mono font-bold ${(mp.margin_pct || 0) >= 40 ? 'text-emerald-400' : (mp.margin_pct || 0) >= 20 ? 'text-amber-400' : 'text-rose-400'}`}>{mp.margin_pct}%</td>
                      <td className={`py-3 px-4 font-mono font-bold ${(mp.net_profit_per_unit || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>₹{mp.net_profit_per_unit?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Channel Revenue Comparison */}
        {metrics.revenue_by_marketplace && metrics.revenue_by_marketplace.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {metrics.revenue_by_marketplace.map((ch: any, idx: number) => (
              <div key={idx} className="bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20 rounded-2xl p-6 backdrop-blur-xl">
                <p className="text-sm font-semibold text-purple-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Store className="w-4 h-4" /> {ch.marketplace}
                </p>
                <div className="space-y-2">
                  <div className="flex justify-between"><span className="text-white/50 text-sm">Revenue</span><span className="font-mono font-bold text-white">₹{ch.revenue?.toLocaleString()}</span></div>
                  <div className="flex justify-between"><span className="text-white/50 text-sm">Orders</span><span className="font-mono font-bold text-white">{ch.orders}</span></div>
                  <div className="flex justify-between"><span className="text-white/50 text-sm">Avg Order Value</span><span className="font-mono font-bold text-white">₹{ch.aov?.toLocaleString()}</span></div>
                  <div className="flex justify-between"><span className="text-white/50 text-sm">Returns</span><span className={`font-mono font-bold ${(ch.returns || 0) > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>{ch.returns || 0}</span></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {!hasAnalysis ? (
          <div className="bg-gradient-to-b from-[#13132e] to-[#0a0a1a] border border-purple-500/20 rounded-3xl p-10 backdrop-blur-xl shadow-2xl relative overflow-hidden text-center max-w-3xl mx-auto my-12">
            {/* Ambient light overlay */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[300px] h-[300px] bg-purple-500/10 rounded-full blur-[80px] pointer-events-none" />
            
            <div className="relative z-10 space-y-6">
              <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-2xl w-16 h-16 mx-auto flex items-center justify-center relative group">
                <div className="absolute inset-0 bg-purple-500/20 blur-md rounded-2xl group-hover:bg-purple-500/40 transition-all" />
                <Brain className="w-8 h-8 text-purple-400 relative z-10 animate-pulse" />
              </div>
              
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-white tracking-tight">Generate AI Intelligence Report</h3>
                <p className="text-purple-200/60 max-w-md mx-auto leading-relaxed text-sm">
                  Run CommercePulse's multi-agent decision engine to analyze pricing strategies, inventory snapshots, return logistics, and ad spend. This generates a SWOT matrix, unit economics, and prioritized growth recommendations.
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={handleStartAnalysis}
                  disabled={isAnalyzing}
                  className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white font-bold rounded-xl shadow-[0_0_30px_rgba(168,85,247,0.3)] transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none text-sm uppercase tracking-wider"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Inference Running...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Run AI Analysis
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <>
            {/* SWOT Diagnostics Grid */}
            <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-xl shadow-xl">
              <div className="mb-6 flex items-center gap-3">
                 <Brain className="w-6 h-6 text-purple-400" />
                 <h3 className="text-xl font-bold text-white">SWOT & Diagnostic Matrix</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Strengths */}
                <div className="bg-gradient-to-br from-emerald-500/10 to-transparent border border-emerald-500/20 rounded-2xl p-6">
                  <h4 className="text-sm font-semibold uppercase tracking-wider text-emerald-400 mb-4 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" /> Strengths
                  </h4>
                  <div className="space-y-4">
                    {ai.strengths?.map((s: any, i: number) => (
                      <div key={i} className="bg-emerald-900/20 border border-emerald-500/10 rounded-xl p-4">
                        <div className="flex items-start gap-3 mb-2">
                          <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                          <div className="flex-1">
                            <h5 className="font-bold text-emerald-100">{s.title || s}</h5>
                          </div>
                          {s.impact && (
                            <span className="text-[10px] uppercase font-bold px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-full">
                              Impact: {s.impact}
                            </span>
                          )}
                        </div>
                        {s.detail && <p className="text-sm text-emerald-100/70 mb-3 ml-8">{s.detail}</p>}
                        {s.metric_value && (
                          <div className="ml-8 inline-block px-3 py-1 bg-emerald-950/50 border border-emerald-500/20 rounded-lg text-xs font-mono text-emerald-300">
                            Metric: {s.metric_value}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Weaknesses */}
                <div className="bg-gradient-to-br from-rose-500/10 to-transparent border border-rose-500/20 rounded-2xl p-6">
                  <h4 className="text-sm font-semibold uppercase tracking-wider text-rose-400 mb-4 flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4" /> Weaknesses
                  </h4>
                  <div className="space-y-4">
                    {ai.weaknesses?.map((w: any, i: number) => (
                      <div key={i} className="bg-rose-900/20 border border-rose-500/10 rounded-xl p-4">
                        <div className="flex items-start gap-3 mb-2">
                          <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                          <div className="flex-1">
                            <h5 className="font-bold text-rose-100">{w.title || w}</h5>
                          </div>
                          {w.impact && (
                            <span className="text-[10px] uppercase font-bold px-2 py-1 bg-rose-500/20 text-rose-400 rounded-full">
                              Impact: {w.impact}
                            </span>
                          )}
                        </div>
                        {w.detail && <p className="text-sm text-rose-100/70 mb-3 ml-8">{w.detail}</p>}
                        {w.metric_value && (
                          <div className="ml-8 inline-block px-3 py-1 bg-rose-950/50 border border-rose-500/20 rounded-lg text-xs font-mono text-rose-300">
                            Metric: {w.metric_value}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Root Causes / Threats */}
                <div className="bg-gradient-to-br from-amber-500/10 to-transparent border border-amber-500/20 rounded-2xl p-6">
                  <h4 className="text-sm font-semibold uppercase tracking-wider text-amber-400 mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Core Threats & Root Causes
                  </h4>
                  <div className="space-y-4">
                    {ai.root_causes?.map((rc: any, i: number) => (
                      <div key={i} className="bg-amber-900/20 border border-amber-500/10 rounded-xl p-4">
                        {rc.linked_weakness && (
                          <div className="text-[10px] uppercase font-bold text-amber-500/70 mb-2 flex items-center gap-1">
                            <ArrowLeft className="w-3 h-3" /> Linked to: {rc.linked_weakness}
                          </div>
                        )}
                        <p className="text-sm text-amber-100 font-medium mb-3">{rc.cause || rc}</p>
                        {rc.evidence && (
                          <div className="px-3 py-2 bg-amber-950/50 border border-amber-500/20 rounded-lg text-xs text-amber-300">
                            <strong>Evidence:</strong> {rc.evidence}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Cross Market / Opportunities */}
                <div className="bg-gradient-to-br from-cyan-500/10 to-transparent border border-cyan-500/20 rounded-2xl p-6">
                  <h4 className="text-sm font-semibold uppercase tracking-wider text-cyan-400 mb-4 flex items-center gap-2">
                    <Globe className="w-4 h-4" /> Market Context & Opportunities
                  </h4>
                  <p className="text-cyan-100/80 leading-relaxed text-sm">
                    {ai.cross_marketplace_summary}
                  </p>
                </div>
              </div>
            </div>

            {/* Action Plan */}
            <div className="bg-gradient-to-b from-purple-500/10 to-transparent border border-purple-500/20 rounded-3xl p-8 backdrop-blur-xl shadow-2xl">
              <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                  <Lightbulb className="w-7 h-7 text-purple-400" /> 
                  Tactical Recommendations
                </h3>
                <span className="text-sm font-mono text-purple-400 bg-purple-500/20 px-4 py-1.5 rounded-full font-semibold border border-purple-500/30">
                  Ranked by ROI Potential
                </span>
              </div>
              
              <div className="grid grid-cols-1 gap-6">
                {recommendations.map((rec: any, idx: number) => (
                  <div key={idx} className="bg-[#0a0a1a]/60 border border-white/10 hover:border-purple-500/50 transition-all duration-300 rounded-2xl p-6 relative overflow-hidden group shadow-lg hover:shadow-purple-500/10">
                    {/* Rank indicator */}
                    <div className="absolute top-0 right-0 bg-gradient-to-bl from-purple-500/30 to-purple-900/40 border-b border-l border-purple-500/30 px-5 py-2 rounded-bl-2xl text-xs font-mono text-purple-300 font-bold shadow-lg">
                      Priority #{idx + 1}
                    </div>

                    <div className="pr-24">
                      <h4 className="text-xl font-bold text-white mb-2 group-hover:text-purple-300 transition-colors">{rec.action_name}</h4>
                      <p className="text-sm text-purple-100/60 mb-5 leading-relaxed max-w-4xl">{rec.description}</p>
                    </div>
                    
                    <div className="flex flex-wrap gap-3 mb-6">
                      <span className={`text-xs px-3 py-1.5 rounded-md font-semibold border shadow-sm ${rec.risk_level === 'High' ? 'bg-rose-500/10 border-rose-500/30 text-rose-400' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'}`}>
                        Risk: {rec.risk_level}
                      </span>
                      <span className="text-xs px-3 py-1.5 rounded-md font-semibold border shadow-sm bg-amber-500/10 border-amber-500/30 text-amber-400">
                        Effort: {rec.difficulty}
                      </span>
                      <span className="text-xs px-3 py-1.5 rounded-md font-semibold border shadow-sm bg-cyan-500/10 border-cyan-500/30 text-cyan-400">
                        {rec.timeframe}
                      </span>
                      {rec.is_profit_safe && (
                        <span className="text-xs px-3 py-1.5 rounded-md font-semibold border shadow-sm bg-purple-500/10 border-purple-500/30 text-purple-400 flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Profit Safe
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                      <div className="bg-white/5 rounded-xl p-5 border border-white/5 group-hover:border-white/10 transition-colors shadow-inner">
                        <p className="text-[11px] text-white/40 font-bold uppercase tracking-widest mb-2 flex items-center gap-2"><Target className="w-3.5 h-3.5"/> Strategic Reason</p>
                        <p className="text-sm text-white/80 leading-relaxed">{rec.reason}</p>
                      </div>
                      <div className="bg-white/5 rounded-xl p-5 border border-white/5 group-hover:border-white/10 transition-colors shadow-inner">
                        <p className="text-[11px] text-white/40 font-bold uppercase tracking-widest mb-2 flex items-center gap-2"><Activity className="w-3.5 h-3.5"/> Execution Strategy</p>
                        <p className="text-sm text-white/80 leading-relaxed">{rec.strategy}</p>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-8 pt-5 border-t border-white/10 mt-2">
                      <div>
                        <p className="text-[11px] text-emerald-400/60 font-bold uppercase tracking-widest mb-1">Estimated Growth</p>
                        <p className="text-2xl font-mono text-emerald-400 font-bold flex items-center gap-2">
                          <TrendingUp className="w-5 h-5" />
                          +{rec.estimated_impact_percentage}%
                        </p>
                      </div>
                      <div className="hidden md:block w-px h-10 bg-white/10"></div>
                      <div>
                        <p className="text-[11px] text-emerald-400/60 font-bold uppercase tracking-widest mb-1">Monthly Financial ROI</p>
                        <p className={`text-2xl font-mono font-bold flex items-center gap-2 ${rec.financial_impact_monthly >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {rec.financial_impact_monthly >= 0 ? '+' : ''}₹{rec.financial_impact_monthly?.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
