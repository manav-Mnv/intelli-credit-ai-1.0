"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
    RadarChart, PolarGrid, PolarAngleAxis, Radar,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer,
} from "recharts";
import {
    Shield, TrendingUp, Search, FileText, AlertTriangle,
    CheckCircle, XCircle, ChevronRight, Loader2, ArrowLeft,
} from "lucide-react";
import { getFullAnalysis, formatCrore, getRiskColor, getDecisionColor } from "@/lib/api";
import Link from "next/link";

export default function AnalysisPage() {
    const { id } = useParams<{ id: string }>();
    const router = useRouter();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        getFullAnalysis(id)
            .then(setData)
            .catch((e) => setError(e?.response?.data?.detail || "Failed to load analysis"))
            .finally(() => setLoading(false));
    }, [id]);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh] gap-3">
                <Loader2 className="w-6 h-6 text-brand-400 animate-spin" />
                <span className="text-slate-400">Loading analysis...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-lg mx-auto px-6 py-20 text-center">
                <XCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                <h2 className="text-xl font-bold mb-2">Analysis Not Found</h2>
                <p className="text-slate-400 text-sm mb-6">{error}</p>
                <Link href="/upload" className="btn-primary inline-flex gap-2 items-center">
                    <ArrowLeft className="w-4 h-4" /> Upload Document
                </Link>
            </div>
        );
    }

    const company = data?.company || {};
    const financials = data?.financials || {};
    const riskScore = data?.risk_scores?.[data?.risk_scores.length - 1] || {};
    const research = data?.research_reports?.[data?.research_reports.length - 1] || {};
    const cam = data?.cam_reports?.[data?.cam_reports.length - 1] || {};

    const riskGrade = riskScore.risk_grade || "N/A";
    const overallScore = riskScore.overall_risk_score ?? 0;

    // Recharts data
    const radarData = [
        { metric: "Profit Margin", value: Math.max(0, 100 - ((financials.profit_margin ?? 10) < 0 ? 50 : (10 - Math.min(10, financials.profit_margin ?? 0)) * 5)) },
        { metric: "D/E Ratio", value: Math.max(0, 100 - (financials.debt_equity_ratio ?? 1) * 25) },
        { metric: "Liquidity", value: Math.max(0, Math.min(100, (financials.current_ratio ?? 1) * 40)) },
        { metric: "Interest Cover", value: Math.max(0, Math.min(100, (financials.interest_coverage ?? 2) * 15)) },
        { metric: "ROE", value: Math.max(0, Math.min(100, financials.roe ?? 10)) },
    ];

    const barData = [
        { name: "Revenue", value: (financials.revenue ?? 0) / 10_000_000 },
        { name: "Profit", value: (financials.net_profit ?? 0) / 10_000_000 },
        { name: "EBITDA", value: (financials.ebitda ?? 0) / 10_000_000 },
        { name: "Debt", value: (financials.total_debt ?? 0) / 10_000_000 },
    ].filter((d) => d.value > 0);

    const riskColor = riskGrade === "Low" ? "#34d399" : riskGrade === "Medium" ? "#fbbf24" : riskGrade === "High" ? "#f97316" : "#ef4444";

    return (
        <div className="max-w-6xl mx-auto px-6 py-10 space-y-8 animate-in">
            {/* Header */}
            <div className="flex items-start justify-between flex-wrap gap-4">
                <div>
                    <button onClick={() => router.back()} className="flex items-center gap-1.5 text-slate-400 hover:text-white text-sm mb-3 transition-colors">
                        <ArrowLeft className="w-3.5 h-3.5" /> Back
                    </button>
                    <h1 className="text-3xl font-black text-white">{company.company_name || "Company Analysis"}</h1>
                    <div className="flex items-center gap-3 mt-2 flex-wrap">
                        <span className="badge badge-info">{company.industry || "Industry"}</span>
                        {cam.decision && (
                            <span className={`badge ${cam.decision === "Approve" ? "badge-success" : cam.decision?.includes("Condition") ? "badge-warning" : "badge-danger"}`}>
                                {cam.decision}
                            </span>
                        )}
                    </div>
                </div>
                <Link href={`/cam/${id}`} className="btn-primary flex items-center gap-2">
                    <FileText className="w-4 h-4" /> View Full CAM Report
                    <ChevronRight className="w-3.5 h-3.5" />
                </Link>
            </div>

            {/* Key Metrics Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: "Risk Score", value: `${overallScore}/100`, sub: riskGrade, color: riskColor },
                    { label: "Default Probability", value: `${((riskScore.default_probability ?? 0) * 100).toFixed(1)}%`, sub: "ML prediction", color: "#94a3b8" },
                    { label: "Recommended Loan", value: formatCrore(cam.recommended_loan_amount), sub: `@ ${cam.interest_rate ?? "N/A"}% p.a.`, color: "#34d399" },
                    { label: "Loan Tenor", value: cam.loan_tenor_months ? `${cam.loan_tenor_months}mo` : "N/A", sub: "Recommended", color: "#94a3b8" },
                ].map(({ label, value, sub, color }) => (
                    <div key={label} className="glass rounded-xl p-4">
                        <div className="text-xs text-slate-500 mb-1">{label}</div>
                        <div className="metric-value text-xl" style={{ color }}>{value}</div>
                        <div className="text-xs text-slate-500 mt-1">{sub}</div>
                    </div>
                ))}
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Financial Health Radar */}
                <div className="glass rounded-xl p-5">
                    <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-brand-400" /> Financial Health Radar
                    </h3>
                    <ResponsiveContainer width="100%" height={220}>
                        <RadarChart data={radarData}>
                            <PolarGrid stroke="rgba(255,255,255,0.06)" />
                            <PolarAngleAxis dataKey="metric" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                            <Radar dataKey="value" stroke="#5c7cfa" fill="#5c7cfa" fillOpacity={0.2} strokeWidth={2} />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>

                {/* Financial Bar Chart */}
                <div className="glass rounded-xl p-5">
                    <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-emerald-400" /> Key Financials (₹ Crore)
                    </h3>
                    {barData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={220}>
                            <BarChart data={barData} barCategoryGap="30%">
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} />
                                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
                                <Tooltip
                                    contentStyle={{ background: "#1f2937", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 12 }}
                                    formatter={(v: number) => [`₹${v.toFixed(2)} Cr`, ""]}
                                />
                                <Bar dataKey="value" fill="#5c7cfa" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="flex items-center justify-center h-[220px] text-slate-500 text-sm">No financial data extracted</div>
                    )}
                </div>
            </div>

            {/* Risk Factors */}
            <div className="glass rounded-xl p-5">
                <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-orange-400" /> Risk Factors Detected
                </h3>
                {riskScore.risk_factors?.length > 0 ? (
                    <div className="space-y-2">
                        {riskScore.risk_factors.map((f: string, i: number) => (
                            <div key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
                                <AlertTriangle className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
                                {f}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="flex items-center gap-2 text-emerald-400 text-sm">
                        <CheckCircle className="w-4 h-4" /> No significant risk factors detected
                    </div>
                )}
            </div>

            {/* Research Summary */}
            <div className="grid md:grid-cols-3 gap-4">
                {[
                    { label: "News Risk", value: research.news_risk_level, summary: research.news_summary },
                    { label: "Litigation Risk", value: research.litigation_risk_level, summary: research.litigation_summary },
                    { label: "Industry Risk", value: research.industry_risk_level, summary: research.industry_summary },
                ].map(({ label, value, summary }) => (
                    <div key={label} className="glass rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-semibold text-slate-400">{label}</span>
                            {value && (
                                <span className={`badge ${value === "Low" ? "badge-success" : value === "Medium" ? "badge-warning" : "badge-danger"}`}>
                                    {value}
                                </span>
                            )}
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">{summary || "No data available"}</p>
                    </div>
                ))}
            </div>

            {/* Key Ratios */}
            <div className="glass rounded-xl p-5">
                <h3 className="text-sm font-bold text-white mb-4">Key Financial Ratios</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                        { label: "Profit Margin", value: financials.profit_margin != null ? `${financials.profit_margin}%` : "N/A" },
                        { label: "D/E Ratio", value: financials.debt_equity_ratio != null ? financials.debt_equity_ratio : "N/A" },
                        { label: "Current Ratio", value: financials.current_ratio != null ? financials.current_ratio : "N/A" },
                        { label: "Interest Coverage", value: financials.interest_coverage != null ? `${financials.interest_coverage}x` : "N/A" },
                        { label: "ROE", value: financials.roe != null ? `${financials.roe}%` : "N/A" },
                        { label: "EBITDA Margin", value: financials.ebitda_margin != null ? `${financials.ebitda_margin}%` : "N/A" },
                        { label: "Revenue", value: formatCrore(financials.revenue) },
                        { label: "Net Profit", value: formatCrore(financials.net_profit) },
                    ].map(({ label, value }) => (
                        <div key={label} className="bg-dark-800/60 rounded-lg p-3">
                            <div className="text-xs text-slate-500 mb-1">{label}</div>
                            <div className="text-sm font-bold text-white">{value}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
