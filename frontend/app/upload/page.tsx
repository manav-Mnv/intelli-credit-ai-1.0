"use client";
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { Upload, FileText, Loader2, CheckCircle, AlertCircle, X } from "lucide-react";
import toast from "react-hot-toast";
import { uploadDocument, runRiskAnalysis, runResearch, generateCAM } from "@/lib/api";

const INDUSTRIES = [
    "Manufacturing", "Steel & Metals", "Textile", "Chemicals",
    "FMCG", "Pharma & Healthcare", "IT & Technology", "Real Estate",
    "Construction", "Retail", "Hospitality", "Education",
    "Infrastructure", "Power & Energy", "Telecom", "Aviation", "Other",
];

type Step = "idle" | "uploading" | "risk" | "research" | "cam" | "done" | "error";

const STEP_LABELS: Record<Step, string> = {
    idle: "",
    uploading: "📄 Processing document & extracting financials...",
    risk: "🔬 Running risk analysis (rules + ML + NLP)...",
    research: "🔎 Research agents searching news & litigation...",
    cam: "📝 Generating Credit Appraisal Memo...",
    done: "✅ Analysis complete!",
    error: "❌ An error occurred",
};

export default function UploadPage() {
    const router = useRouter();
    const [file, setFile] = useState<File | null>(null);
    const [companyName, setCompanyName] = useState("");
    const [industry, setIndustry] = useState("Manufacturing");
    const [loanAmount, setLoanAmount] = useState("");
    const [step, setStep] = useState<Step>("idle");
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState("");

    const onDrop = useCallback((accepted: File[]) => {
        if (accepted[0]) setFile(accepted[0]);
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            "application/pdf": [".pdf"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
            "application/vnd.ms-excel": [".xls"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
            "text/plain": [".txt"],
        },
        maxFiles: 1,
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file || !companyName.trim()) {
            toast.error("Please select a file and enter a company name");
            return;
        }

        setError("");
        setProgress(0);

        try {
            // Step 1: Upload
            setStep("uploading");
            setProgress(15);
            const uploadResult = await uploadDocument(file, companyName, industry);
            const companyId = uploadResult.company_id;
            setProgress(35);

            // Step 2: Risk analysis
            setStep("risk");
            setProgress(50);
            await runRiskAnalysis(companyId, industry);
            setProgress(65);

            // Step 3: Research
            setStep("research");
            setProgress(75);
            await runResearch(companyId, companyName, industry);
            setProgress(88);

            // Step 4: CAM
            setStep("cam");
            setProgress(92);
            const loanAmt = loanAmount ? parseFloat(loanAmount) * 10_000_000 : undefined;
            await generateCAM(companyId, loanAmt);
            setProgress(100);

            setStep("done");
            toast.success("Analysis complete! Redirecting...");
            setTimeout(() => router.push(`/analysis/${companyId}`), 1200);

        } catch (err: any) {
            setStep("error");
            const rawMsg = err?.response?.data?.detail;
            const msg = typeof rawMsg === 'string' ? rawMsg : (Array.isArray(rawMsg) ? rawMsg[0]?.msg : err?.message || "Upload failed");
            setError(msg);
            toast.error(msg);
        }
    };

    const isProcessing = !["idle", "done", "error"].includes(step);

    return (
        <div className="max-w-2xl mx-auto px-6 py-14">
            <div className="mb-10">
                <h1 className="text-3xl font-black text-white mb-2">Analyze Loan Application</h1>
                <p className="text-slate-400 text-sm">
                    Upload financial documents — AI will extract data, score risk, and generate a full CAM report.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Company Name */}
                <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
                        Company Name *
                    </label>
                    <input
                        className="input-dark"
                        placeholder="e.g. ABC Steel Ltd."
                        value={companyName}
                        onChange={(e) => setCompanyName(e.target.value)}
                        required
                        disabled={isProcessing}
                    />
                </div>

                {/* Industry */}
                <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
                        Industry
                    </label>
                    <select
                        className="input-dark"
                        value={industry}
                        onChange={(e) => setIndustry(e.target.value)}
                        disabled={isProcessing}
                    >
                        {INDUSTRIES.map((ind) => (
                            <option key={ind} value={ind}>{ind}</option>
                        ))}
                    </select>
                </div>

                {/* Loan Amount */}
                <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
                        Requested Loan Amount (₹ Crore) — Optional
                    </label>
                    <input
                        className="input-dark"
                        type="number"
                        placeholder="e.g. 10"
                        value={loanAmount}
                        onChange={(e) => setLoanAmount(e.target.value)}
                        disabled={isProcessing}
                        min="0"
                    />
                </div>

                {/* File Drop */}
                <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
                        Financial Document *
                    </label>
                    <div
                        {...getRootProps()}
                        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${isDragActive
                            ? "border-brand-500 bg-brand-500/10"
                            : file
                                ? "border-emerald-500/50 bg-emerald-500/5"
                                : "border-white/10 hover:border-white/20 hover:bg-white/3"
                            } ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}`}
                    >
                        <input {...getInputProps()} disabled={isProcessing} />
                        {file ? (
                            <div className="flex items-center justify-center gap-3">
                                <FileText className="w-8 h-8 text-emerald-400" />
                                <div className="text-left">
                                    <div className="text-sm font-semibold text-emerald-400">{file.name}</div>
                                    <div className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                                </div>
                                {!isProcessing && (
                                    <button
                                        type="button"
                                        onClick={(e) => { e.stopPropagation(); setFile(null); }}
                                        className="ml-auto text-slate-500 hover:text-white"
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        ) : (
                            <>
                                <Upload className="w-8 h-8 text-slate-500 mx-auto mb-3" />
                                <div className="text-sm text-slate-300 font-medium">
                                    {isDragActive ? "Drop file here" : "Drag & drop, or click to browse"}
                                </div>
                                <div className="text-xs text-slate-500 mt-1">
                                    PDF, Excel (.xlsx), Word (.docx), TXT — Max 50 MB
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {/* Progress */}
                {isProcessing && (
                    <div className="glass rounded-xl p-5 animate-in">
                        <div className="flex items-center gap-3 mb-3">
                            <Loader2 className="w-4 h-4 text-brand-400 animate-spin" />
                            <span className="text-sm text-slate-300">{STEP_LABELS[step]}</span>
                        </div>
                        <div className="w-full bg-dark-700 rounded-full h-1.5">
                            <div
                                className="bg-gradient-to-r from-brand-600 to-purple-500 h-1.5 rounded-full transition-all duration-700"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                        <div className="text-xs text-slate-500 mt-1.5 text-right">{progress}%</div>
                    </div>
                )}

                {/* Done */}
                {step === "done" && (
                    <div className="flex items-center gap-3 glass rounded-xl p-4 border-emerald-500/20 animate-in">
                        <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                        <span className="text-sm text-emerald-300">Analysis complete! Redirecting to results...</span>
                    </div>
                )}

                {/* Error */}
                {step === "error" && error && (
                    <div className="flex items-start gap-3 glass rounded-xl p-4 border-red-500/20 animate-in">
                        <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                        <div>
                            <div className="text-sm text-red-300 font-medium">Error</div>
                            <div className="text-xs text-red-400/80 mt-0.5">{error}</div>
                        </div>
                    </div>
                )}

                {/* Submit */}
                <button
                    type="submit"
                    disabled={isProcessing || !file || !companyName}
                    className="btn-primary w-full flex items-center justify-center gap-2 py-3 text-base disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                    {isProcessing ? (
                        <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
                    ) : (
                        <><Upload className="w-4 h-4" /> Start AI Analysis</>
                    )}
                </button>

                <p className="text-xs text-slate-500 text-center">
                    Your documents are processed locally and securely.
                </p>
            </form>
        </div>
    );
}
