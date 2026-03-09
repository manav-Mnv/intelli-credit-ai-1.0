"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Brain, Upload, BarChart3, FileText } from "lucide-react";

const navLinks = [
    { href: "/", label: "Home" },
    { href: "/upload", label: "Upload", icon: Upload },
    { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
];

export default function Navbar() {
    const pathname = usePathname();

    return (
        <nav className="sticky top-0 z-50 border-b border-white/5 bg-dark-950/80 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2.5 group">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-600 to-purple-600 flex items-center justify-center shadow-lg group-hover:shadow-brand-500/30 transition-shadow">
                        <Brain className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-bold text-base text-white">
                        IntelliCredit <span className="gradient-text">AI</span>
                    </span>
                </Link>

                {/* Links */}
                <div className="flex items-center gap-1">
                    {navLinks.map(({ href, label, icon: Icon }) => {
                        const active = pathname === href;
                        return (
                            <Link
                                key={href}
                                href={href}
                                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all ${active
                                        ? "bg-brand-600/20 text-brand-400 border border-brand-500/30"
                                        : "text-slate-400 hover:text-white hover:bg-white/5"
                                    }`}
                            >
                                {Icon && <Icon className="w-3.5 h-3.5" />}
                                {label}
                            </Link>
                        );
                    })}
                </div>

                {/* CTA */}
                <Link
                    href="/upload"
                    className="btn-primary text-sm px-5 py-2 hidden sm:flex items-center gap-2"
                >
                    <Upload className="w-3.5 h-3.5" />
                    Analyze Loan
                </Link>
            </div>
        </nav>
    );
}
