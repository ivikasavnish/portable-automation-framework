from api.routes.scenarios import scenario_routes
from api.routes.executions import execution_routes
from api.routes.data_providers import data_provider_routes
from api.routes.ai_services import ai_service_routes
from fastapi import FastAPI

app = FastAPI()

# Include API routes
app.include_router(scenario_routes)
app.include_router(execution_routes)
app.include_router(data_provider_routes)
app.include_router(ai_service_routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)