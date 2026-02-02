import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function UploadPayrollPage() {
  const [file, setFile] = useState(null);
  const [runMonth, setRunMonth] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleUpload() {
    if (!file || !runMonth) return alert("Missing file or run month");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      await axios.post(
        `http://127.0.0.1:8002/payroll/upload`,
        formData,
        {
          params: {
            run_month: runMonth,
            executed_by: "frontend",
          },
        }
      );

      navigate("/dashboard");
    } catch (err) {
      alert("Upload failed");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6">
      <div className="bg-slate-800 p-8 rounded-3xl border border-slate-700 w-full max-w-xl shadow-2xl">
        <h2 className="text-3xl font-bold text-white mb-2">Upload Payroll</h2>
        <p className="text-slate-400 mb-8">Process monthly employee data and generate AI insights.</p>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Target Month</label>
            <input
              type="month"
              value={runMonth}
              onChange={(e) => setRunMonth(e.target.value)}
              className="w-full bg-slate-700/50 border border-slate-600 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Payroll CSV File</label>
            <div className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center hover:border-blue-500 transition cursor-pointer relative">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setFile(e.target.files[0])}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <div className="text-slate-400">
                {file ? (
                  <span className="text-blue-400 font-medium">{file.name}</span>
                ) : (
                  <>
                    <p className="mb-2 text-lg">Click or drag CSV here</p>
                    <p className="text-xs">Standard payroll export format required</p>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="pt-4 flex gap-4">
            <button
              onClick={() => navigate(-1)}
              className="flex-1 bg-slate-700 hover:bg-slate-600 text-white font-semibold py-3 rounded-xl transition"
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={loading || !file || !runMonth}
              className="flex-[2] bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 text-white font-semibold py-3 rounded-xl shadow-lg shadow-blue-500/20 transition transform hover:-translate-y-0.5 active:translate-y-0"
            >
              {loading ? "Processing..." : "Start Upload"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
