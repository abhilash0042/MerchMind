import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router";
import {
  Wallet,
  Play,
  Database,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  IndianRupee,
  MessageSquare,
  BarChart3,
  Sparkles,
  Send,
  TrendingDown,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import { apiClient, ensureSeller, askPaymentsQuestion } from "../services/api";

const TIER_COLORS = ["#7c3aed", "#2563eb", "#64748b", "#e11d48"];

export function PaymentsPage() {
  const [sellerId, setSellerId] = useState<string | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [matches, setMatches] = useState<any[]>([]);
  const [matchTotal, setMatchTotal] = useState(0);
  const [exceptions, setExceptions] = useState<any[]>([]);
  const [busy, setBusy] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [tab, setTab] = useState<"analysis" | "matches" | "exceptions" | "qa">("analysis");
  const [qaInput, setQaInput] = useState("");
  const [qaMessages, setQaMessages] = useState<{ role: string; text: string }[]>([
    {
      role: "assistant",
      text: "Ask about STL batches, MDR/GST shortfalls, unmatched coffee orders, or why bank UTR differs from Razorpay net.",
    },
  ]);
  const [qaLoading, setQaLoading] = useState(false);

  const load = useCallback(async (sid: string) => {
    const [sum, m, e] = await Promise.all([
      apiClient.get(`/payments/summary?seller_id=${sid}`),
      apiClient.get(`/payments/matches?seller_id=${sid}&page_size=50`),
      apiClient.get(`/payments/exceptions?seller_id=${sid}`),
    ]);
    setSummary(sum);
    setAnalysis(sum);
    setMatches(m.results || []);
    setMatchTotal(m.total || 0);
    setExceptions(e.results || []);
  }, []);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const sid = await ensureSeller();
        setSellerId(sid);
        await load(sid);
      } catch (err: any) {
        setError(err.message || "Failed to load payments");
      } finally {
        setLoading(false);
      }
    })();
  }, [load]);

  const flash = (msg: string) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(null), 5000);
  };

  const buildCash = async () => {
    if (!sellerId) return;
    setBusy("seed");
    setError(null);
    try {
      const res = await apiClient.post("/payments/seed", { seller_id: sellerId }, sellerId);
      flash(`Built ${res.ledger_count} ledger + ${res.settlement_count} STL rows from Brew Boulevard orders.`);
      await load(sellerId);
    } catch (err: any) {
      setError(err.message || "Build cash failed");
    } finally {
      setBusy(null);
    }
  };

  const runRecon = async () => {
    if (!sellerId) return;
    setBusy("reconcile");
    setError(null);
    try {
      const res = await apiClient.post("/payments/reconcile", { seller_id: sellerId }, sellerId);
      flash(
        `Recon done — ${(res.match_rate * 100).toFixed(1)}% match (${res.tier_breakdown?.exact || 0} exact, ${res.tier_breakdown?.fuzzy || 0} fuzzy, ${res.tier_breakdown?.ai_assisted || 0} AI).`
      );
      await load(sellerId);
      setTab("analysis");
    } catch (err: any) {
      setError(err.message || "Reconciliation failed");
    } finally {
      setBusy(null);
    }
  };

  const sendQa = async (q?: string) => {
    const question = (q || qaInput).trim();
    if (!question || !sellerId) return;
    setQaInput("");
    setQaMessages((prev) => [...prev, { role: "user", text: question }]);
    setQaLoading(true);
    try {
      const res = await askPaymentsQuestion(sellerId, question, summary?.run_id);
      setQaMessages((prev) => [...prev, { role: "assistant", text: res.answer.replace(/\*\*/g, "") }]);
    } catch (err: any) {
      setQaMessages((prev) => [...prev, { role: "assistant", text: err.message || "Could not answer." }]);
    } finally {
      setQaLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    );
  }

  const matchPct = summary?.has_run ? Math.round((summary.match_rate || 0) * 1000) / 10 : null;
  const tiers = summary?.tier_breakdown || analysis?.tier_breakdown || {};
  const wf = analysis?.cash_waterfall || {};
  const tierData = analysis?.tier_funnel
    ? [
        { name: "Exact", value: analysis.tier_funnel.exact || 0 },
        { name: "Fuzzy", value: analysis.tier_funnel.fuzzy || 0 },
        { name: "AI", value: analysis.tier_funnel.ai_assisted || 0 },
        { name: "Exceptions", value: analysis.tier_funnel.exceptions || 0 },
      ].filter((d) => d.value > 0)
    : [];

  const waterfallData = wf.gross_gmv_rupees
    ? [
        { stage: "Gross GMV", amount: wf.gross_gmv_rupees },
        { stage: "Razorpay fees", amount: wf.razorpay_fees_rupees },
        { stage: "GST on fee", amount: wf.gst_on_fees_rupees },
        { stage: "Net STL", amount: wf.net_settlement_rupees },
        { stage: "Bank UTR", amount: wf.bank_credited_rupees },
      ]
    : [];

  const suggested = [
    "Why is my payout short after 2% MDR and GST?",
    "How many exceptions are still open?",
    "Explain STL-BB batch settlement timing",
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-purple-600 mb-2">
            <Wallet className="w-6 h-6" />
            <span className="text-sm font-semibold uppercase tracking-wider">Brew Boulevard</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Payments analysis</h1>
          <p className="text-gray-500 mt-1 max-w-2xl">
            Coffee GMV → Razorpay net → bank UTR. reconnAIssance 3-tier engine with fee-aware fuzzy matching and settlement Q&A.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={buildCash}
            disabled={!sellerId || !!busy}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 bg-white text-gray-800 font-medium hover:bg-gray-50 disabled:opacity-50"
          >
            {busy === "seed" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Database className="w-4 h-4" />}
            Build cash from orders
          </button>
          <button
            type="button"
            onClick={runRecon}
            disabled={!sellerId || !!busy}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 text-white font-medium hover:bg-purple-500 disabled:opacity-50"
          >
            {busy === "reconcile" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Run recon
          </button>
        </div>
      </div>

      {success && (
        <div className="flex items-center gap-2 text-emerald-800 bg-emerald-50 border border-emerald-100 px-4 py-3 rounded-xl">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" /> {success}
        </div>
      )}
      {error && (
        <div className="flex items-center gap-2 text-red-700 bg-red-50 border border-red-100 px-4 py-3 rounded-xl">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" /> {error}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Ledger orders", value: summary?.ledger_count ?? "—", icon: IndianRupee },
          { label: "Match rate", value: matchPct != null ? `${matchPct}%` : "—", icon: CheckCircle2 },
          { label: "Exact / fuzzy / AI", value: summary?.has_run ? `${tiers.exact || 0} / ${tiers.fuzzy || 0} / ${tiers.ai_assisted || 0}` : "—", icon: BarChart3 },
          { label: "Unsettled GMV", value: analysis?.unsettled_gmv_rupees != null ? `₹${Number(analysis.unsettled_gmv_rupees).toLocaleString()}` : "—", icon: TrendingDown },
        ].map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div key={kpi.label} className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
              <p className="text-xs uppercase tracking-wider text-gray-500 font-semibold flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4 text-purple-500" /> {kpi.label}
              </p>
              <p className="text-2xl font-semibold text-gray-900">{kpi.value}</p>
            </div>
          );
        })}
      </div>

      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="flex border-b border-gray-100 overflow-x-auto">
          {(
            [
              ["analysis", "Payments analysis", BarChart3],
              ["matches", `Matches (${matchTotal})`, CheckCircle2],
              ["exceptions", `Exceptions (${exceptions.length})`, AlertTriangle],
              ["qa", "Settlement Q&A", MessageSquare],
            ] as const
          ).map(([key, label, Icon]) => (
            <button
              key={key}
              type="button"
              onClick={() => setTab(key)}
              className={`flex items-center gap-2 px-5 py-3 text-sm font-semibold whitespace-nowrap ${
                tab === key ? "text-purple-600 border-b-2 border-purple-600 bg-purple-50/50" : "text-gray-500 hover:text-gray-700"
              }`}
            >
              <Icon className="w-4 h-4" /> {label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {tab === "analysis" && (
            <div className="space-y-6">
              {!summary?.has_run && (
                <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 text-amber-900 text-sm">
                  Run recon to unlock tier funnel, predictions, and settlement Q&A on your latest coffee cash data.
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <IndianRupee className="w-4 h-4 text-purple-500" /> Cash waterfall
                  </h3>
                  {waterfallData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={waterfallData} layout="vertical" margin={{ left: 80 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                        <XAxis type="number" tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
                        <YAxis type="category" dataKey="stage" width={75} tick={{ fontSize: 11 }} />
                        <Tooltip formatter={(v: number) => [`₹${v.toLocaleString()}`, "Amount"]} />
                        <Bar dataKey="amount" fill="#7c3aed" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-gray-400 text-sm">Build cash from orders first.</p>
                  )}
                  {wf.fee_drag_pct != null && (
                    <p className="text-xs text-gray-500 mt-2">
                      Fee drag: {wf.fee_drag_pct}% of gross · Bank vs net gap: ₹{Number(wf.bank_vs_net_gap_rupees || 0).toLocaleString()}
                    </p>
                  )}
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Matching cascade (reconn tiers)</h3>
                  {tierData.length > 0 ? (
                    <div className="flex items-center gap-4">
                      <ResponsiveContainer width="50%" height={200}>
                        <PieChart>
                          <Pie data={tierData} dataKey="value" innerRadius={50} outerRadius={75} paddingAngle={3}>
                            {tierData.map((_, i) => (
                              <Cell key={i} fill={TIER_COLORS[i % TIER_COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                      <ul className="text-sm space-y-2 flex-1">
                        {tierData.map((d, i) => (
                          <li key={d.name} className="flex justify-between">
                            <span className="flex items-center gap-2">
                              <span className="w-2 h-2 rounded-full" style={{ background: TIER_COLORS[i] }} />
                              {d.name}
                            </span>
                            <span className="font-semibold text-gray-800">{d.value}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : (
                    <p className="text-gray-400 text-sm">No recon run yet.</p>
                  )}
                </div>
              </div>

              {analysis?.insights?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-500" /> AI finance insights
                  </h3>
                  <ul className="space-y-2">
                    {analysis.insights.map((line: string, i: number) => (
                      <li key={i} className="text-sm text-gray-700 bg-gray-50 rounded-lg px-4 py-3 border border-gray-100">
                        {line.replace(/\*\*/g, "")}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {analysis?.predictions?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Cash forecasts</h3>
                  <div className="grid md:grid-cols-3 gap-3">
                    {analysis.predictions.map((p: any, i: number) => (
                      <div key={i} className="border border-purple-100 bg-purple-50/50 rounded-xl p-4">
                        <p className="text-xs uppercase text-purple-600 font-semibold mb-1">{p.label}</p>
                        <p className="text-xl font-bold text-gray-900">
                          {p.value_rupees != null ? `₹${Number(p.value_rupees).toLocaleString()}` : `${p.value_pct?.toFixed?.(1) ?? p.value_pct}%`}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">{p.explanation}</p>
                        <span className="text-[10px] uppercase tracking-wider text-purple-400">{p.confidence} confidence</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {analysis?.risk_board?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">SKU settlement risk</h3>
                  <p className="text-xs text-gray-500 mb-3">
                    Scored from refunds, marketplace vs Shopify/Razorpay, and payment mode — same signals the matcher uses. Not a trained neural net.
                  </p>
                  <table className="w-full text-sm">
                    <thead className="text-left text-gray-500 bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 font-medium">SKU</th>
                        <th className="px-3 py-2 font-medium">Orders</th>
                        <th className="px-3 py-2 font-medium">GMV</th>
                        <th className="px-3 py-2 font-medium">Risk</th>
                        <th className="px-3 py-2 font-medium">Why</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.risk_board.map((r: any) => (
                        <tr key={r.sku} className="border-t border-gray-100">
                          <td className="px-3 py-2 font-mono text-xs font-semibold text-gray-900">{r.sku}</td>
                          <td className="px-3 py-2">{r.orders}</td>
                          <td className="px-3 py-2">₹{Number(r.gmv_rupees).toLocaleString()}</td>
                          <td className="px-3 py-2">
                            <span
                              className={`text-xs font-semibold uppercase px-2 py-0.5 rounded-full ${
                                r.risk_band === "high"
                                  ? "bg-rose-100 text-rose-700"
                                  : r.risk_band === "medium"
                                    ? "bg-amber-100 text-amber-800"
                                    : "bg-emerald-100 text-emerald-700"
                              }`}
                            >
                              {r.risk_band} {Math.round(r.risk_score * 100)}
                            </span>
                          </td>
                          <td className="px-3 py-2 text-gray-500 text-xs">{String(r.top_reason).replaceAll("_", " ")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {tab === "matches" && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left text-gray-600">
                  <tr>
                    <th className="px-3 py-2 font-medium">Tier</th>
                    <th className="px-3 py-2 font-medium">Coffee order</th>
                    <th className="px-3 py-2 font-medium">SKU</th>
                    <th className="px-3 py-2 font-medium">Gross → Net</th>
                    <th className="px-3 py-2 font-medium">STL / Bank</th>
                    <th className="px-3 py-2 font-medium">Why matched</th>
                  </tr>
                </thead>
                <tbody>
                  {matches.map((g) => {
                    const led = g.members?.find((m: any) => m.role === "ledger_entry");
                    const stl = g.members?.find((m: any) => m.role === "settlement_entry");
                    const bank = g.members?.find((m: any) => m.role === "bank_entry");
                    const orderId = led?.order_id || led?.normalized_ref || "—";
                    const sku = led?.sku || led?.details?.sku || "—";
                    return (
                      <tr key={g.group_id} className="border-t border-gray-100 hover:bg-gray-50/50">
                        <td className="px-3 py-3 capitalize font-medium text-purple-700">{g.tier.replace("_", " ")}</td>
                        <td className="px-3 py-3 font-mono text-xs text-gray-900 uppercase">{orderId}</td>
                        <td className="px-3 py-3 text-gray-800 font-medium">{sku}</td>
                        <td className="px-3 py-3 text-gray-900">
                          ₹{led?.gross_rupees ?? led?.amount_rupees ?? "—"}
                          {stl ? ` → ₹${stl.net_rupees ?? stl.amount_rupees}` : ""}
                        </td>
                        <td className="px-3 py-3 text-xs text-gray-600">
                          {stl?.batch_id && <div className="font-mono">{stl.batch_id}</div>}
                          {bank && <div className="text-emerald-600">Bank ₹{bank.amount_rupees}</div>}
                        </td>
                        <td className="px-3 py-3 text-gray-500 max-w-xs text-xs">{g.reason}</td>
                      </tr>
                    );
                  })}
                  {matches.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-3 py-12 text-center text-gray-400">
                        No matches — run recon after building cash data.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {tab === "exceptions" && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-left text-gray-600">
                  <tr>
                    <th className="px-3 py-2 font-medium">Code</th>
                    <th className="px-3 py-2 font-medium">Source</th>
                    <th className="px-3 py-2 font-medium">Ref</th>
                    <th className="px-3 py-2 font-medium">SKU</th>
                    <th className="px-3 py-2 font-medium">Amount</th>
                    <th className="px-3 py-2 font-medium">Detail</th>
                  </tr>
                </thead>
                <tbody>
                  {exceptions.map((e) => (
                    <tr key={e.exception_id} className="border-t border-gray-100">
                      <td className="px-3 py-3 font-medium text-rose-600">{e.reason_code}</td>
                      <td className="px-3 py-3 text-gray-800">{e.source}</td>
                      <td className="px-3 py-3 font-mono text-xs uppercase text-gray-900">{e.normalized_ref}</td>
                      <td className="px-3 py-3 text-gray-800">{e.sku || e.details?.sku || "—"}</td>
                      <td className="px-3 py-3 text-gray-900 font-medium">₹{e.amount_rupees}</td>
                      <td className="px-3 py-3 text-gray-500 text-xs max-w-sm">{e.reason_text}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === "qa" && (
            <div className="max-w-2xl">
              <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                {qaMessages.map((m, i) => (
                  <div
                    key={i}
                    className={`text-sm px-4 py-3 rounded-xl ${
                      m.role === "user" ? "bg-purple-100 text-purple-900 ml-8" : "bg-gray-50 text-gray-800 mr-8 border border-gray-100"
                    }`}
                  >
                    {m.text}
                  </div>
                ))}
                {qaLoading && (
                  <div className="flex items-center gap-2 text-gray-400 text-sm">
                    <Loader2 className="w-4 h-4 animate-spin" /> Analyzing settlement context…
                  </div>
                )}
              </div>
              <div className="flex flex-wrap gap-2 mb-3">
                {suggested.map((q) => (
                  <button
                    key={q}
                    type="button"
                    onClick={() => sendQa(q)}
                    className="text-xs px-3 py-1.5 rounded-full border border-purple-200 text-purple-700 hover:bg-purple-50"
                  >
                    {q}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  value={qaInput}
                  onChange={(e) => setQaInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendQa()}
                  placeholder="Why did STL-BB-1001 fall short?"
                  className="flex-1 border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-300"
                />
                <button
                  type="button"
                  onClick={() => sendQa()}
                  disabled={qaLoading || !summary?.has_run}
                  className="px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-500 disabled:opacity-40"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              {!summary?.has_run && (
                <p className="text-xs text-gray-400 mt-2">Run recon first to enable settlement Q&A.</p>
              )}
            </div>
          )}
        </div>
      </div>

      <p className="text-sm text-gray-400">
        SKU-level sold vs settled on{" "}
        <Link to="/ai/intelligence" className="text-purple-600 hover:underline">
          AI product analysis
        </Link>
        .
      </p>
    </div>
  );
}
