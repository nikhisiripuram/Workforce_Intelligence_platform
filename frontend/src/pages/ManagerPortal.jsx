import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { fetchAllRuns, fetchLatestRun } from "../api/analytics";

export default function ManagerPortal() {
    const [allEmployees, setAllEmployees] = useState([]);
    const [managers, setManagers] = useState([]);
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [managerId, setManagerId] = useState(null);

    const [runMonth, setRunMonth] = useState(null);
    const [availableRuns, setAvailableRuns] = useState([]);

    const navigate = useNavigate();

    // 1. Initial Load: Runs and Status
    useEffect(() => {
        Promise.all([fetchLatestRun(), fetchAllRuns()])
            .then(([latest, all]) => {
                setAvailableRuns(all);
                if (latest?.ready) {
                    setRunMonth(latest.run_month);
                } else if (all.length > 0) {
                    setRunMonth(all[0]);
                }
            });
    }, []);

    // 2. Fetch Data for Selected Month
    useEffect(() => {
        if (!runMonth) return;

        setLoading(true);
        axios.get(`http://127.0.0.1:8002/employees/?run_month=${runMonth}`)
            .then(res => {
                const employees = res.data;
                setAllEmployees(employees);

                // Identify all managers in this run
                const uniqueManagerIds = [...new Set(employees.map(e => e.manager_id).filter(id => id !== null))];
                const managerList = employees.filter(e => uniqueManagerIds.includes(e.id));
                setManagers(managerList);

                // Default to the first manager found if current selection is invalid
                if (!managerId || !managerList.find(m => m.id === managerId)) {
                    if (managerList.length > 0) {
                        setManagerId(managerList[0].id);
                    }
                }
            })
            .catch(err => console.error("Error fetching employees:", err))
            .finally(() => setLoading(false));
    }, [runMonth]);

    // 3. Filter Reports when Manager or Data Changes
    useEffect(() => {
        if (managerId && allEmployees.length > 0) {
            const absoluteReports = allEmployees.filter(emp => emp.manager_id === managerId);
            setReports(absoluteReports);
        } else {
            setReports([]);
        }
    }, [managerId, allEmployees]);

    const handleSubmitReview = async (empId, rating, feedback) => {
        setSubmitting(true);
        try {
            await axios.post("http://127.0.0.1:8002/performance/reviews/", {
                employee_id: empId,
                manager_id: managerId,
                quarter: 1,
                year: parseInt(runMonth.split("-")[0]),
                rating: parseFloat(rating),
                feedback: feedback
            });
            alert("Review submitted successfully!");
        } catch (err) {
            alert("Failed to submit review");
            console.error(err);
        } finally {
            setSubmitting(false);
        }
    };

    if (loading && availableRuns.length === 0) return (
        <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
    );

    const currentManager = managers.find(m => m.id === managerId);

    return (
        <div className="min-h-screen bg-slate-900 text-white p-6 md:p-12">
            <div className="max-w-6xl mx-auto">
                <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
                    <div>
                        <h1 className="text-4xl font-black tracking-tight mb-2">Manager Portal</h1>
                        <div className="flex flex-wrap items-center gap-6 mt-4">
                            <div className="flex items-center gap-3">
                                <span className="text-slate-500 font-bold uppercase text-[10px] tracking-widest">Payroll Run</span>
                                <select
                                    value={runMonth || ""}
                                    onChange={(e) => setRunMonth(e.target.value)}
                                    className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-blue-400 font-bold outline-none ring-blue-500/20 focus:ring-4 text-sm"
                                >
                                    {availableRuns.map(run => (
                                        <option key={run} value={run}>{run}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="flex items-center gap-3">
                                <span className="text-slate-500 font-bold uppercase text-[10px] tracking-widest">Acting As</span>
                                <select
                                    value={managerId || ""}
                                    onChange={(e) => setManagerId(parseInt(e.target.value))}
                                    className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-blue-400 font-bold outline-none ring-blue-500/20 focus:ring-4 text-sm"
                                >
                                    {managers.map(m => (
                                        <option key={m.id} value={m.id}>{m.name} ({m.job_title})</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => navigate("/dashboard")}
                            className="px-6 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl border border-slate-700 transition font-bold"
                        >
                            HR Dashboard
                        </button>
                    </div>
                </header>

                <div className="bg-blue-600/10 border border-blue-500/20 rounded-3xl p-8 mb-12 flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="flex items-center gap-6">
                        <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center text-3xl font-black shadow-lg shadow-blue-500/20">
                            {currentManager?.name.charAt(0)}
                        </div>
                        <div>
                            <h2 className="text-2xl font-black text-white">{currentManager?.name}</h2>
                            <p className="text-blue-400 font-bold uppercase tracking-widest text-xs mt-1">{currentManager?.job_title} • {currentManager?.department}</p>
                        </div>
                    </div>
                    <div className="flex gap-12 bg-slate-900/50 px-8 py-4 rounded-2xl border border-slate-800">
                        <div className="text-center">
                            <p className="text-3xl font-black text-white">{reports.length}</p>
                            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Direct Reports</p>
                        </div>
                        <div className="text-center">
                            <p className="text-3xl font-black text-blue-400">1</p>
                            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Pending Reviews</p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 gap-8">
                    {reports.length === 0 ? (
                        <div className="py-20 text-center bg-slate-800/20 rounded-[3rem] border-2 border-dashed border-slate-800">
                            <p className="text-slate-500 font-bold text-xl mb-2">Zero Reports Found</p>
                            <p className="text-slate-600 text-sm">This manager currently has no direct reports in the {runMonth} snapshot.</p>
                        </div>
                    ) : reports.map((emp) => (
                        <ReportCard
                            key={emp.id}
                            employee={emp}
                            onSubmit={handleSubmitReview}
                            isSubmitting={submitting}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}

function ReportCard({ employee, onSubmit, isSubmitting }) {
    const [rating, setRating] = useState(4);
    const [feedback, setFeedback] = useState("");

    return (
        <div className="bg-slate-800 p-8 rounded-[3rem] border border-slate-700/50 shadow-2xl flex flex-col lg:flex-row gap-12 group hover:border-blue-500/30 transition-all duration-500 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 blur-[100px] pointer-events-none"></div>

            <div className="flex-1 relative">
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <h3 className="text-4xl font-black text-white group-hover:text-blue-400 transition-colors uppercase italic tracking-tighter">{employee.name}</h3>
                        <p className="text-blue-500 font-bold text-sm tracking-[0.2em] mt-2 uppercase">{employee.job_title} • {employee.department}</p>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="bg-green-500/10 text-green-400 text-[10px] uppercase font-black tracking-widest px-4 py-1.5 rounded-full border border-green-500/20 mb-2">
                            Snapshot Active
                        </span>
                        <span className="text-slate-500 text-[10px] font-mono">ID: EMP-{employee.id}</span>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6 mt-12">
                    <div className="bg-slate-900/60 rounded-[2rem] p-6 border border-slate-700/30 group-hover:border-blue-500/20 transition-all">
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">Efficiency Score</p>
                        <div className="flex items-baseline gap-2">
                            <p className="text-3xl font-black text-white">0.94</p>
                            <span className="text-xs text-green-400 font-bold">+2%</span>
                        </div>
                    </div>
                    <div className="bg-slate-900/60 rounded-[2rem] p-6 border border-slate-700/30 group-hover:border-blue-500/20 transition-all">
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">Utilization</p>
                        <p className="text-3xl font-black text-white">100%</p>
                    </div>
                </div>
            </div>

            <div className="flex-1 space-y-8 bg-slate-900/40 p-10 rounded-[2.5rem] border border-slate-700/30 backdrop-blur-sm">
                <div>
                    <label className="block text-xs font-black text-slate-500 uppercase tracking-widest mb-6 flex justify-between">
                        <span>Performance Rating</span>
                        <span className="text-blue-400">{rating} / 5</span>
                    </label>
                    <div className="flex gap-4">
                        {[1, 2, 3, 4, 5].map((num) => (
                            <button
                                key={num}
                                onClick={() => setRating(num)}
                                className={`flex-1 aspect-square rounded-2xl font-black text-xl transition-all duration-300 border-2 ${rating === num
                                    ? "bg-blue-600 border-blue-400 text-white shadow-[0_0_30px_rgba(59,130,246,0.3)] scale-110"
                                    : "bg-slate-800 border-slate-700 text-slate-500 hover:border-slate-500 hover:bg-slate-750"
                                    }`}
                            >
                                {num}
                            </button>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="block text-xs font-black text-slate-500 uppercase tracking-widest mb-6">Strategic Feedback & Guidance</label>
                    <textarea
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        className="w-full bg-slate-950/80 border border-slate-800 rounded-3xl px-6 py-5 text-white h-40 resize-none focus:outline-none focus:ring-4 focus:ring-blue-500/20 transition-all font-medium placeholder:text-slate-800 text-sm leading-relaxed"
                        placeholder="What are the key priorities for this employee in the next sprint?"
                    />
                </div>

                <button
                    onClick={() => onSubmit(employee.id, rating, feedback)}
                    disabled={isSubmitting || !feedback}
                    className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white font-black py-5 rounded-2xl transition-all shadow-xl shadow-blue-900/40 disabled:opacity-20 active:scale-[0.98] uppercase tracking-[0.2em] text-sm"
                >
                    {isSubmitting ? "Syncing to Blockchain..." : "Commit Quarterly Review"}
                </button>
            </div>
        </div>
    );
}
