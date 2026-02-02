import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import {
    fetchEmployeeInsights,
    generateManagerReview,
    generateIndividualFeedback,
    fetchLatestRun
} from "../api/analytics";

export default function EmployeeSnapshotPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [runMonth, setRunMonth] = useState(null);
    const [employee, setEmployee] = useState(null);
    const [viewMode, setViewMode] = useState("MANAGER"); // or INDIVIDUAL
    const [aiContent, setAiContent] = useState("");
    const [loading, setLoading] = useState(false);

    // 1. Get Run Month
    useEffect(() => {
        fetchLatestRun().then((res) => {
            if (res?.ready) setRunMonth(res.run_month);
        });
    }, []);

    // 2. Load Basic Employee Data
    useEffect(() => {
        if (runMonth && id) {
            fetchEmployeeInsights(id, runMonth).then(setEmployee);
        }
    }, [runMonth, id]);

    // 3. Load AI Content when viewMode changes
    useEffect(() => {
        if (!runMonth || !id) return;

        setLoading(true);
        setAiContent(""); // clear previous

        const apiCall =
            viewMode === "MANAGER"
                ? generateManagerReview(id, runMonth)
                : generateIndividualFeedback(id, runMonth);

        apiCall
            .then((res) => {
                setAiContent(res.review || res.feedback);
            })
            .catch((err) => {
                setAiContent("Failed to generate AI snapshot.");
                console.error(err);
            })
            .finally(() => setLoading(false));
    }, [runMonth, id, viewMode]);

    if (!employee) return (
        <div className="flex items-center justify-center min-h-screen bg-slate-900">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-900 text-white p-6 md:p-12">
            <div className="max-w-5xl mx-auto">
                <header className="flex justify-between items-start mb-10">
                    <div>
                        <button
                            onClick={() => navigate(-1)}
                            className="text-slate-400 hover:text-white mb-4 flex items-center gap-2 transition"
                        >
                            &larr; Back
                        </button>
                        <h1 className="text-4xl font-bold">{employee.name}</h1>
                        <p className="text-blue-400 font-medium text-lg mt-1">
                            {employee.role || 'Professional'} | {employee.department}
                        </p>
                    </div>
                    <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-700 text-sm text-slate-400">
                        Period: {runMonth}
                    </div>
                </header>

                <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
                        <h3 className="text-slate-400 text-sm font-medium mb-1">Efficiency</h3>
                        <p className="text-3xl font-bold">{(employee.efficiency_score * 100).toFixed(1)}%</p>
                        <div className="w-full bg-slate-700 h-1.5 rounded-full mt-3 overflow-hidden">
                            <div
                                className="bg-green-500 h-full rounded-full"
                                style={{ width: `${Math.min(100, employee.efficiency_score * 100)}%` }}
                            ></div>
                        </div>
                        <p className="text-xs text-slate-500 mt-2">Peer Rank: Top {100 - employee.peer_percentile}%</p>
                    </div>

                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
                        <h3 className="text-slate-400 text-sm font-medium mb-1">Monthly Cost</h3>
                        <p className="text-3xl font-bold">${employee.monthly_cost?.toLocaleString() || employee.hourly_rate * 160}</p>
                        <p className="text-xs text-slate-500 mt-2">${employee.hourly_rate}/hr rate</p>
                    </div>

                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
                        <h3 className="text-slate-400 text-sm font-medium mb-1">Retention Risk</h3>
                        <p className={`text-3xl font-bold ${employee.risk_score > 70 ? 'text-red-400' : employee.risk_score > 40 ? 'text-yellow-400' : 'text-green-400'}`}>
                            {employee.risk_score}%
                        </p>
                        <p className="text-xs text-slate-500 mt-2">Based on AI engagement analysis</p>
                    </div>
                </section>

                <div className="bg-slate-800 rounded-3xl border border-slate-700 shadow-xl overflow-hidden">
                    <div className="flex border-b border-slate-700">
                        <button
                            className={`flex-1 py-4 font-semibold transition ${viewMode === "MANAGER" ? "bg-slate-700 text-white" : "text-slate-400 hover:text-slate-200"}`}
                            onClick={() => setViewMode("MANAGER")}
                        >
                            Manager Review
                        </button>
                        <button
                            className={`flex-1 py-4 font-semibold transition ${viewMode === "INDIVIDUAL" ? "bg-slate-700 text-white" : "text-slate-400 hover:text-slate-200"}`}
                            onClick={() => setViewMode("INDIVIDUAL")}
                        >
                            Individual Feedback
                        </button>
                    </div>

                    <div className="p-8 min-h-[400px]">
                        {loading ? (
                            <div className="flex flex-col items-center justify-center py-20 gap-4">
                                <div className="animate-pulse rounded-full h-12 w-12 bg-blue-500/20 flex items-center justify-center">
                                    <div className="h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                </div>
                                <p className="text-slate-400 animate-pulse font-medium">Synthesizing AI Insights...</p>
                            </div>
                        ) : (
                            <div className="prose prose-invert max-w-none">
                                {aiContent.split("\n\n").map((para, i) => (
                                    <p key={i} className="text-slate-300 leading-relaxed mb-4 whitespace-pre-wrap">
                                        {para}
                                    </p>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
