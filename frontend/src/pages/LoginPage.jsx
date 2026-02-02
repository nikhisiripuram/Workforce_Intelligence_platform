import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [role, setRole] = useState("hr"); // hr or manager
    const navigate = useNavigate();

    const handleLogin = (e) => {
        e.preventDefault();
        // Mock login logic for now
        localStorage.setItem("user_role", role);
        localStorage.setItem("user_email", email);

        if (role === "hr") {
            navigate("/dashboard");
        } else {
            navigate("/manager");
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
            <div className="bg-white/10 backdrop-blur-md p-8 rounded-2xl shadow-xl w-full max-w-md border border-white/20">
                <h1 className="text-3xl font-bold text-white mb-2 text-center">WorkForce AI</h1>
                <p className="text-blue-200 text-center mb-8">HR & Performance Platform</p>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label className="block text-gray-300 mb-2 text-sm">Email Address</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                            placeholder="name@company.com"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-gray-300 mb-2 text-sm">Role</label>
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                type="button"
                                onClick={() => setRole("hr")}
                                className={`py-2 px-4 rounded-lg border transition-all ${role === "hr"
                                        ? "bg-blue-600 border-blue-500 text-white"
                                        : "bg-slate-700/30 border-slate-600 text-slate-300 hover:bg-slate-700/50"
                                    }`}
                            >
                                HR Admin
                            </button>
                            <button
                                type="button"
                                onClick={() => setRole("manager")}
                                className={`py-2 px-4 rounded-lg border transition-all ${role === "manager"
                                        ? "bg-blue-600 border-blue-500 text-white"
                                        : "bg-slate-700/30 border-slate-600 text-slate-300 hover:bg-slate-700/50"
                                    }`}
                            >
                                Manager
                            </button>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 rounded-lg shadow-lg hover:shadow-blue-500/30 transition-all transform hover:-translate-y-0.5"
                    >
                        Sign In
                    </button>
                </form>
            </div>

            <div className="absolute bottom-4 text-center text-slate-500 text-xs">
                &copy; 2026 Workforce AI. All rights reserved.
            </div>
        </div>
    );
}
