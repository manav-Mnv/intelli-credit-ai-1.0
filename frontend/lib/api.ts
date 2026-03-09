import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
    baseURL: API_BASE,
    timeout: 120000,
    headers: { "Content-Type": "application/json" },
});

export async function uploadDocument(
    file: File,
    companyName: string,
    industry: string
) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("company_name", companyName);
    formData.append("industry", industry);

    const res = await api.post("/api/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
}

export async function runRiskAnalysis(companyId: string, industry: string = "") {
    const res = await api.post("/api/risk/analyze", {
        company_id: companyId,
        industry,
    });
    return res.data;
}

export async function runResearch(
    companyId: string,
    companyName: string,
    industry: string = ""
) {
    const res = await api.post("/api/research/run", {
        company_id: companyId,
        company_name: companyName,
        industry,
    });
    return res.data;
}

export async function generateCAM(
    companyId: string,
    loanAmount?: number
) {
    const res = await api.post("/api/cam/generate", {
        company_id: companyId,
        requested_loan_amount: loanAmount || null,
    });
    return res.data;
}

export async function getFullAnalysis(companyId: string) {
    const res = await api.get(`/api/cam/full/${companyId}`);
    return res.data;
}

export function formatCrore(value: number | null | undefined): string {
    if (!value) return "N/A";
    const crore = value / 10_000_000;
    return `₹${crore.toFixed(2)} Cr`;
}

export function getRiskColor(grade: string): string {
    switch (grade?.toLowerCase()) {
        case "low": return "text-emerald-400";
        case "medium": return "text-amber-400";
        case "high": return "text-orange-400";
        case "critical": return "text-red-400";
        default: return "text-slate-400";
    }
}

export function getDecisionColor(decision: string): string {
    if (decision?.toLowerCase() === "approve") return "text-emerald-400";
    if (decision?.toLowerCase().includes("condition")) return "text-amber-400";
    return "text-red-400";
}
