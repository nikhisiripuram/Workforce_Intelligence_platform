from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import payroll, ai, payroll_upload
from backend.app.api.routes import analytics
from backend.app.api.routes import analytics_charts
from backend.app.api.routes import run_state



app = FastAPI(title="Workforce AI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # OK for local + demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(run_state.router)
app.include_router(payroll_upload.router)
app.include_router(payroll.router)
app.include_router(analytics.router)
app.include_router(analytics_charts.router)
app.include_router(ai.router)
# New routers
from backend.app.api.routes import employees, performance
app.include_router(employees.router)
app.include_router(performance.router)



@app.get("/health")
def health_check():
    return {"status": "ok"}
