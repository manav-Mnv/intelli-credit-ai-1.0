import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
    title: "IntelliCredit AI — Automated Loan Analysis",
    description:
        "AI-powered corporate loan analysis. Upload financial documents, get risk scores and CAM reports in minutes.",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className="bg-dark-950 text-slate-100 min-h-screen">
                <Navbar />
                <main>{children}</main>
                <Toaster
                    position="top-right"
                    toastOptions={{
                        style: {
                            background: "#1f2937",
                            color: "#e2e8f0",
                            border: "1px solid rgba(255,255,255,0.08)",
                            borderRadius: "12px",
                        },
                    }}
                />
            </body>
        </html>
    );
}
