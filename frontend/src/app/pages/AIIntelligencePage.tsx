import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router";
import { Brain, Search, TrendingUp, AlertTriangle, XCircle, Sparkles, Loader2, ArrowRight } from "lucide-react";
import { fetchProductsWithAnalysis, ensureSeller, triggerProductAnalysis } from "../services/api";

export function AIIntelligencePage() {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [analyzingIds, setAnalyzingIds] = useState<Set<string>>(new Set());
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const sellerId = await ensureSeller();
      const res = await fetchProductsWithAnalysis(sellerId);
      setProducts(res.data || []);
    } catch (error) {
      console.error("Failed to load products:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (productId: string, e: React.MouseEvent) => {
    e.preventDefault(); // Prevent navigating to detail page if clicked inside Link
    try {
      setAnalyzingIds((prev) => new Set(prev).add(productId));
      const sellerId = await ensureSeller();
      const res = await triggerProductAnalysis(sellerId, productId);
      
      if (res.status === 'success') {
        // Navigate to the analysis detail page immediately
        navigate(`/ai/products/${productId}`);
      } else {
        alert("Analysis completed with a partial state. Please check if all data was provided.");
      }
    } catch (error: any) {
      console.error("Failed to trigger analysis:", error);
      alert(error.message || "Analysis failed. Try again in a moment.");
    } finally {
      setAnalyzingIds((prev) => {
        const next = new Set(prev);
        next.delete(productId);
        return next;
      });
    }
  };

  const filteredProducts = products.filter((p) =>
    p.product_name.toLowerCase().includes(search.toLowerCase()) ||
    p.sku.toLowerCase().includes(search.toLowerCase())
  );

  const strongPerformers = products.filter(p => p.health_score >= 80).length;
  const atRisk = products.filter(p => p.health_score >= 50 && p.health_score < 80).length;
  const underperformers = products.filter(p => p.health_score > 0 && p.health_score < 50).length;

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white -m-8 p-8 relative overflow-hidden font-sans">
      {/* Background ambient light */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-cyan-600/10 rounded-full blur-[150px] pointer-events-none" />
      
      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz48L3N2Zz4=')] opacity-50 pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl relative group">
              <div className="absolute inset-0 bg-purple-500/20 blur-md rounded-xl group-hover:bg-purple-500/40 transition-all" />
              <Brain className="w-8 h-8 text-purple-400 relative z-10" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-cyan-400">
                AI Intelligence
              </h1>
              <p className="text-sm text-purple-200/60 mt-1 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                Multi-agent product analysis & optimization
              </p>
            </div>
          </div>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-purple-200/40" />
            <input
              type="text"
              placeholder="Search products..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-purple-200/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all w-64"
            />
          </div>
        </div>

        {/* Summary Orbs */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-purple-200/60 uppercase tracking-wider mb-1">Total Products</p>
              <p className="text-3xl font-mono text-white">{products.length}</p>
            </div>
            <div className="p-3 bg-white/5 rounded-full"><Brain className="w-6 h-6 text-purple-400" /></div>
          </div>
          <div className="bg-white/5 backdrop-blur-xl border border-emerald-500/20 rounded-2xl p-5 flex items-center justify-between relative overflow-hidden group">
            <div className="absolute inset-0 bg-emerald-500/5 group-hover:bg-emerald-500/10 transition-colors" />
            <div className="relative z-10">
              <p className="text-xs font-medium text-emerald-400/80 uppercase tracking-wider mb-1">Strong Performers</p>
              <p className="text-3xl font-mono text-emerald-400" style={{ textShadow: '0 0 10px rgba(52, 211, 153, 0.5)' }}>{strongPerformers}</p>
            </div>
            <TrendingUp className="w-6 h-6 text-emerald-400 relative z-10" />
          </div>
          <div className="bg-white/5 backdrop-blur-xl border border-amber-500/20 rounded-2xl p-5 flex items-center justify-between relative overflow-hidden group">
            <div className="absolute inset-0 bg-amber-500/5 group-hover:bg-amber-500/10 transition-colors" />
            <div className="relative z-10">
              <p className="text-xs font-medium text-amber-400/80 uppercase tracking-wider mb-1">At Risk</p>
              <p className="text-3xl font-mono text-amber-400" style={{ textShadow: '0 0 10px rgba(251, 191, 36, 0.5)' }}>{atRisk}</p>
            </div>
            <AlertTriangle className="w-6 h-6 text-amber-400 relative z-10" />
          </div>
          <div className="bg-white/5 backdrop-blur-xl border border-rose-500/20 rounded-2xl p-5 flex items-center justify-between relative overflow-hidden group">
            <div className="absolute inset-0 bg-rose-500/5 group-hover:bg-rose-500/10 transition-colors" />
            <div className="relative z-10">
              <p className="text-xs font-medium text-rose-400/80 uppercase tracking-wider mb-1">Needs Attention</p>
              <p className="text-3xl font-mono text-rose-400" style={{ textShadow: '0 0 10px rgba(244, 63, 94, 0.5)' }}>{underperformers}</p>
            </div>
            <XCircle className="w-6 h-6 text-rose-400 relative z-10" />
          </div>
        </div>

        {/* Product Grid */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-purple-500/10 border-t-purple-400 rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <Brain className="w-8 h-8 text-purple-400 animate-pulse" />
              </div>
            </div>
            <p className="text-purple-200/40 animate-pulse font-mono text-sm tracking-widest">INITIALIZING NEURAL NETWORKS...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map((product, i) => {
              const hasAnalysis = product.analysis_status === 'completed';
              const isAnalyzing = analyzingIds.has(product.product_id);
              
              let scoreColor = "text-purple-400";
              let ringColor = "stroke-purple-500/30";
              let glowColor = "rgba(168, 85, 247, 0.3)";
              let statusLabel = "PENDING ANALYSIS";
              
              if (hasAnalysis) {
                if (product.health_score >= 80) {
                  scoreColor = "text-emerald-400";
                  ringColor = "stroke-emerald-500";
                  glowColor = "rgba(52, 211, 153, 0.4)";
                  statusLabel = "HIGH PERFORMANCE";
                } else if (product.health_score >= 50) {
                  scoreColor = "text-amber-400";
                  ringColor = "stroke-amber-500";
                  glowColor = "rgba(251, 191, 36, 0.4)";
                  statusLabel = "NEEDS OPTIMIZATION";
                } else {
                  scoreColor = "text-rose-400";
                  ringColor = "stroke-rose-500";
                  glowColor = "rgba(244, 63, 94, 0.4)";
                  statusLabel = "CRITICAL ATTENTION";
                }
              }

              return (
                <Link 
                  key={product.product_id}
                  to={`/ai/products/${product.product_id}`}
                  className="relative group h-full block cursor-pointer text-left"
                  style={{ animation: `fadeUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) ${i * 0.05}s both` }}
                >
                  {/* Decorative glow background */}
                  <div className={`absolute -inset-0.5 bg-gradient-to-r ${hasAnalysis ? 'from-purple-500/20 to-cyan-500/20' : 'from-white/5 to-white/5'} rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-500`} />
                  
                  <div className="relative h-full bg-[#0d0d1f] border border-white/10 rounded-2xl p-6 flex flex-col transition-all duration-300 group-hover:border-white/20">
                    {/* Top Row: Meta & Score */}
                    <div className="flex justify-between items-start gap-4 mb-6">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border ${hasAnalysis ? 'bg-purple-500/10 border-purple-500/20 text-purple-300' : 'bg-white/5 border-white/10 text-white/40'}`}>
                            {product.category || "General"}
                          </span>
                          <span className="text-[10px] text-white/20 font-mono truncate">SKU: {product.sku}</span>
                        </div>
                        <h3 className="text-lg font-bold text-white group-hover:text-purple-300 transition-colors line-clamp-2" title={product.product_name}>
                          {(() => {
                            if (product.product_name !== product.sku) return product.product_name;
                            // Decode Brew Boulevard SKUs into human-readable product names
                            if (product.sku.includes('BB-WB')) return "Brew Boulevard Whole Bean Coffee (250g)";
                            if (product.sku.includes('BB-GR')) return "Brew Boulevard Ground Roast Coffee (500g)";
                            if (product.sku.includes('BB-CB')) return "Brew Boulevard Cold Brew Blend (1L)";
                            if (product.sku.includes('BB-IN')) return "Brew Boulevard Premium Instant Coffee (100g)";
                            return product.product_name;
                          })()}
                        </h3>
                      </div>

                      {/* Sci-fi Health Meter */}
                      <div className="relative shrink-0 w-16 h-16">
                        <svg className="w-16 h-16 -rotate-90">
                          <circle cx="32" cy="32" r="28" fill="transparent" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
                          {hasAnalysis && (
                            <circle
                              cx="32" cy="32" r="28" fill="transparent" className={ringColor} strokeWidth="3"
                              strokeDasharray={176} strokeDashoffset={176 - (product.health_score / 100) * 176}
                              strokeLinecap="round" style={{ filter: `drop-shadow(0 0 6px ${glowColor})`, transition: 'all 1.5s cubic-bezier(0.4, 0, 0.2, 1)' }}
                            />
                          )}
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className={`text-xl font-mono font-bold leading-none ${scoreColor}`}>
                            {hasAnalysis ? product.health_score : '--'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Quick Metrics Grid */}
                    <div className="grid grid-cols-2 gap-3 mb-6">
                      <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                        <p className="text-[10px] text-white/30 uppercase tracking-tighter mb-1">Monthly Revenue</p>
                        <p className="text-sm font-mono text-white/90">₹{product.total_revenue?.toLocaleString() || '0'}</p>
                      </div>
                      <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                        <p className="text-[10px] text-white/30 uppercase tracking-tighter mb-1">Margin Pct</p>
                        <p className={`text-sm font-mono ${product.margin_pct < 20 ? 'text-rose-400' : 'text-emerald-400'}`}>
                          {product.margin_pct || '0'}%
                        </p>
                      </div>
                    </div>

                    {/* Agent Status/Verdict */}
                    <div className="mt-auto pt-4 border-t border-white/5 flex items-center justify-between">
                      <div className="flex flex-col">
                        <p className={`text-[10px] font-bold tracking-widest ${hasAnalysis ? scoreColor : 'text-white/20'}`}>
                          {statusLabel}
                        </p>
                        <p className="text-xs text-white/40 mt-1 italic">
                          {product.performance_verdict || "Awaiting intelligence cycle..."}
                        </p>
                      </div>

                      {hasAnalysis ? (
                        <div 
                          className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-lg text-purple-400 group-hover:bg-purple-500/20 group-hover:text-white transition-all"
                        >
                          <ArrowRight className="w-5 h-5" />
                        </div>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            handleAnalyze(product.product_id, e);
                          }}
                          disabled={isAnalyzing}
                          className="flex items-center gap-2 px-3 py-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 rounded-lg text-xs font-bold text-purple-400 transition-all disabled:opacity-50"
                        >
                          {isAnalyzing ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <Sparkles className="w-3 h-3" />
                          )}
                          {isAnalyzing ? "Analyzing…" : "ANALYZE"}
                        </button>
                      )}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
      
      {/* Base animations */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .group { animation: fadeUp 0.5s ease-out; }
      `}} />
    </div>
  );
}
