import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8002",
});

export async function uploadPayrollCSV(file, runMonth) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await API.post(
    `/payroll/upload`,
    formData,
    {
      params: { run_month: runMonth, executed_by: "frontend" },
      headers: { "Content-Type": "multipart/form-data" },
    }
  );

  return res.data;
}
