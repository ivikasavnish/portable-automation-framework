from fastapi import FastAPI
from api.routes import scenarios, executions, data_providers, ai_services

app = FastAPI()

app.include_router(scenarios.router)
app.include_router(executions.router)
app.include_router(data_providers.router)
app.include_router(ai_services.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)