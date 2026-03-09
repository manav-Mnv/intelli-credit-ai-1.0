"use client";
import { useEffect, useState } from "react";
import { api, formatCrore } from "@/lib/api";
import Link from "next/link";
import { Building2, FileText, TrendingUp, Clock, ChevronRight, Loader2, Upload } from "lucide-react";

export default function DashboardPage() {
    const [companies, setCompanies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get("/api/companies/").then((r) => setCompanies(r.data)).catch(() => { }).finally(() => setLoading(false));
    }, []);

    return (
        <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h1 className="text-3xl font-black text-white">Dashboard</h1>
                    <p className="text-slate-400 text-sm mt-1">All analyzed companies and their credit status</p>
                </div>
                <Link href="/upload" className="btn-primary flex items-center gap-2">
                    <Upload className="w-4 h-4" /> New Analysis
                </Link>
            </div>

            {loading ? (
                <div className="flex items-center gap-3 py-20 justify-center">
                    <Loader2 className="w-5 h-5 text-brand-400 animate-spin" />
                    <span className="text-slate-400">Loading companies...</span>
                </div>
            ) : companies.length === 0 ? (
                <div className="text-center py-24">
                    <Building2 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <h2 className="text-lg font-bold text-slate-400 mb-2">No companies analyzed yet</h2>
                    <p className="text-slate-500 text-sm mb-6">Upload a financial document to start your first analysis.</p>
                    <Link href="/upload" className="btn-primary inline-flex items-center gap-2">
                        <Upload className="w-4 h-4" /> Analyze First Loan
                    </Link>
                </div>
            ) : (
                <div className="space-y-3">
                    {companies.map((c: any) => (
                        <div key={c.id} className="glass rounded-xl p-5 flex items-center justify-between gap-4 hover:border-white/15 transition-all group">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-xl bg-brand-600/20 flex items-center justify-center flex-shrink-0">
                                    <Building2 className="w-5 h-5 text-brand-400" />
                                </div>
                                <div>
                                    <div className="font-bold text-white text-sm">{c.company_name}</div>
                                    <div className="text-xs text-slate-500 mt-0.5">{c.industry || "Unknown industry"}</div>
                                </div>
                            </div>
                            <div className="flex items-center gap-3 text-xs text-slate-500">
                                <Clock className="w-3.5 h-3.5" />
                                {new Date(c.created_at).toLocaleDateString("en-IN")}
                            </div>
                            <div className="flex items-center gap-2 ml-auto">
                                <Link
                                    href={`/analysis/${c.id}`}
                                    className="px-3 py-1.5 rounded-lg bg-dark-700 text-slate-300 text-xs font-medium hover:text-white hover:bg-brand-600/20 transition-all flex items-center gap-1.5"
                                >
                                    <TrendingUp className="w-3 h-3" /> Analysis
                                </Link>
                                <Link
                                    href={`/cam/${c.id}`}
                                    className="px-3 py-1.5 rounded-lg bg-dark-700 text-slate-300 text-xs font-medium hover:text-white hover:bg-brand-600/20 transition-all flex items-center gap-1.5"
                                >
                                    <FileText className="w-3 h-3" /> CAM
                                </Link>
                                <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-slate-400 transition-colors" />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
