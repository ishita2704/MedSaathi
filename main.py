from fastapi import FastAPI
from server.auth.route import router as auth_router
from server.reports.route import router as reports_router
from server.diagnosis.route import router as diagnosis_router

app=FastAPI()

app.include_router(auth_router)
app.include_router(reports_router)
app.include_router(diagnosis_router)

@app.get("/health")
def healthCheck():
    return {"message":"ok"}

def main():
    print("Hello from medicalreportdiagnosis!")


if __name__ == "__main__":
    main()
