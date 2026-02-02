import React, { useEffect, useState } from "react";
import axios from "axios";

const OrgNode = ({ node }) => {
    const [isOpen, setIsOpen] = useState(true);
    const hasChildren = node.children && node.children.length > 0;

    return (
        <div className="ml-6 border-l border-slate-700 pl-4 py-2">
            <div className="flex items-center gap-3">
                {hasChildren && (
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="w-4 h-4 flex items-center justify-center bg-slate-700 rounded text-[10px] text-slate-300 hover:bg-slate-600"
                    >
                        {isOpen ? "−" : "+"}
                    </button>
                )}
                <div className={`p-3 rounded-lg border ${node.position_level === 'Top' ? 'bg-blue-900/40 border-blue-500/50' : 'bg-slate-800 border-slate-700'} min-w-[200px] shadow-sm`}>
                    <div className="font-bold text-white">{node.name}</div>
                    <div className="text-xs text-slate-400">{node.job_title || 'Employee'}</div>
                    <div className="text-[10px] uppercase tracking-wider text-blue-400 mt-1">{node.department}</div>
                </div>
            </div>

            {isOpen && hasChildren && (
                <div className="mt-2 text-slate-300">
                    {node.children.map(child => (
                        <OrgNode key={child.id} node={child} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default function OrgTreePage() {
    const [treeData, setTreeData] = useState([]);
    const [loading, setLoading] = useState(true);

    // Get month from URL
    const searchParams = new URLSearchParams(window.location.search);
    const runMonth = searchParams.get("month");

    useEffect(() => {
        const url = runMonth
            ? `http://127.0.0.1:8002/employees/org-tree?run_month=${runMonth}`
            : "http://127.0.0.1:8002/employees/org-tree";

        axios.get(url)
            .then(res => {
                setTreeData(res.data);
            })
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, [runMonth]);

    if (loading) return (
        <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-900 p-8">
            <div className="max-w-6xl mx-auto">
                <header className="mb-10 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-white">Organizational Structure</h1>
                        <p className="text-slate-400 mt-2">Visualizing hierarchy and department reporting lines</p>
                    </div>
                    <button
                        onClick={() => window.history.back()}
                        className="px-4 py-2 text-slate-300 hover:text-white transition"
                    >
                        &larr; Back to Dashboard
                    </button>
                </header>

                <div className="bg-slate-800/30 p-8 rounded-3xl border border-slate-700/50 overflow-x-auto">
                    {treeData.length > 0 ? (
                        treeData.map(root => (
                            <OrgNode key={root.id} node={root} />
                        ))
                    ) : (
                        <div className="text-center py-20">
                            <p className="text-slate-500 text-lg">No organizational data found.</p>
                            <p className="text-slate-600 text-sm mt-1">Make sure you've uploaded payroll data and assigned managers.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
