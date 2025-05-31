from fastapi import FastAPI
from api.routes import scenarios, executions, data_providers, ai_services

app = FastAPI()

app.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
app.include_router(executions.router, prefix="/executions", tags=["executions"])
app.include_router(data_providers.router, prefix="/data-providers", tags=["data providers"])
app.include_router(ai_services.router, prefix="/ai-services", tags=["AI services"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)