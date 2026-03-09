import Link from "next/link";
import {
    Brain,
    Upload,
    Shield,
    TrendingUp,
    FileText,
    Zap,
    ChevronRight,
    BarChart3,
    Search,
    CheckCircle,
} from "lucide-react";

const features = [
    {
        icon: Upload,
        title: "Document Ingestor",
        desc: "Upload PDF Annual Reports, GST Returns, Bank Statements, and Excel files. AI extracts all financial data automatically.",
        color: "from-blue-500 to-cyan-500",
    },
    {
        icon: Search,
        title: "Research Agents",
        desc: "AI agents search for fraud cases, lawsuits, regulatory actions, and industry trends — saving hours of manual research.",
        color: "from-purple-500 to-pink-500",
    },
    {
        icon: Shield,
        title: "Risk Detection",
        desc: "Three-layer risk analysis: rule-based financial checks, XGBoost ML model, and FinBERT NLP sentiment analysis.",
        color: "from-orange-500 to-red-500",
    },
    {
        icon: FileText,
        title: "CAM Generator",
        desc: "Automatically generates a full Credit Appraisal Memo with risk score, loan recommendation, and interest rate.",
        color: "from-emerald-500 to-teal-500",
    },
];

const stats = [
    { label: "Processing Time", value: "< 3 min", sub: "vs. weeks manually" },
    { label: "Analysis Layers", value: "3", sub: "rules + ML + NLP" },
    { label: "Report Sections", value: "6", sub: "full CAM memo" },
    { label: "Research Agents", value: "3", sub: "news, legal, industry" },
];

const pipeline = [
    { step: "01", label: "Upload Documents", icon: Upload },
    { step: "02", label: "Extract Financials", icon: BarChart3 },
    { step: "03", label: "Score Risk", icon: Shield },
    { step: "04", label: "Research Company", icon: Search },
    { step: "05", label: "Generate CAM", icon: FileText },
];

export default function HomePage() {
    return (
        <div className="min-h-screen">
            {/* Hero */}
            <section className="relative overflow-hidden px-6 pt-24 pb-32">
                {/* Background glow */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-[-100px] left-1/2 -translate-x-1/2 w-[800px] h-[500px] rounded-full bg-brand-600/10 blur-[120px]" />
                    <div className="absolute top-1/2 right-[-100px] w-[400px] h-[400px] rounded-full bg-purple-600/8 blur-[100px]" />
                </div>

                <div className="relative max-w-4xl mx-auto text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-brand-500/20 bg-brand-500/10 text-brand-400 text-xs font-semibold mb-8">
                        <Zap className="w-3 h-3" />
                        AI-Powered Corporate Loan Analysis
                    </div>

                    <h1 className="text-5xl sm:text-6xl font-black leading-tight tracking-tight mb-6">
                        Credit Decisions in{" "}
                        <span className="gradient-text">Minutes</span>
                        <br />
                        Not Weeks.
                    </h1>

                    <p className="text-slate-400 text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
                        IntelliCredit AI reads financial documents, extracts data, scores
                        risk using ML models, researches company reputation, and generates
                        a complete Credit Appraisal Memo — automatically.
                    </p>

                    <div className="flex items-center justify-center gap-4 flex-wrap">
                        <Link
                            href="/upload"
                            className="btn-primary flex items-center gap-2 px-8 py-3 text-base glow-blue"
                        >
                            <Upload className="w-4 h-4" />
                            Analyze a Loan Application
                        </Link>
                        <Link
                            href="/dashboard"
                            className="px-8 py-3 rounded-xl border border-white/10 text-slate-300 hover:text-white hover:bg-white/5 transition-all text-base font-medium flex items-center gap-2"
                        >
                            <BarChart3 className="w-4 h-4" />
                            View Dashboard
                        </Link>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section className="px-6 py-16 border-y border-white/5">
                <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
                    {stats.map((s) => (
                        <div key={s.label} className="text-center">
                            <div className="metric-value gradient-text">{s.value}</div>
                            <div className="text-sm font-semibold text-white mt-1">{s.label}</div>
                            <div className="text-xs text-slate-500 mt-0.5">{s.sub}</div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Pipeline */}
            <section className="px-6 py-20">
                <div className="max-w-5xl mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-4">
                        How It Works
                    </h2>
                    <p className="text-slate-400 text-center mb-12 text-sm">
                        5-step AI pipeline replaces weeks of manual analyst work
                    </p>
                    <div className="flex flex-col md:flex-row items-center gap-3">
                        {pipeline.map(({ step, label, icon: Icon }, i) => (
                            <div key={step} className="flex items-center gap-3">
                                <div className="glass p-4 rounded-xl flex flex-col items-center gap-2 min-w-[120px] text-center hover:border-brand-500/30 transition-colors">
                                    <div className="text-xs font-mono text-brand-400 font-bold">{step}</div>
                                    <Icon className="w-5 h-5 text-slate-300" />
                                    <div className="text-xs text-slate-300 font-medium">{label}</div>
                                </div>
                                {i < pipeline.length - 1 && (
                                    <ChevronRight className="w-4 h-4 text-slate-600 flex-shrink-0 hidden md:block" />
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features */}
            <section className="px-6 pb-20">
                <div className="max-w-5xl mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-3">
                        Three Pillars of Analysis
                    </h2>
                    <p className="text-slate-400 text-center mb-12 text-sm">
                        Covering the complete credit appraisal workflow
                    </p>
                    <div className="grid md:grid-cols-2 gap-6">
                        {features.map(({ icon: Icon, title, desc, color }) => (
                            <div key={title} className="glass p-6 rounded-2xl hover:border-white/15 transition-all group">
                                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                                    <Icon className="w-5 h-5 text-white" />
                                </div>
                                <h3 className="text-base font-bold text-white mb-2">{title}</h3>
                                <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="px-6 pb-24">
                <div className="max-w-3xl mx-auto glass rounded-2xl p-10 text-center glow-blue">
                    <Brain className="w-10 h-10 text-brand-400 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold mb-3">Ready to Analyze?</h2>
                    <p className="text-slate-400 text-sm mb-6">
                        Upload any company's financial documents and get a full credit appraisal in minutes.
                    </p>
                    <Link href="/upload" className="btn-primary inline-flex items-center gap-2 px-8 py-3">
                        <Upload className="w-4 h-4" />
                        Start Analysis
                        <ChevronRight className="w-4 h-4" />
                    </Link>
                </div>
            </section>
        </div>
    );
}
