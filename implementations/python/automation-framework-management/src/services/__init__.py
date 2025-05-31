src/main.py:

import sys
from api.routes.scenarios import scenario_routes
from api.routes.executions import execution_routes
from api.routes.data_providers import data_provider_routes
from api.routes.ai_services import ai_service_routes
from core.runner import Runner
from core.logger import Logger
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.register_blueprint(scenario_routes)
    app.register_blueprint(execution_routes)
    app.register_blueprint(data_provider_routes)
    app.register_blueprint(ai_service_routes)
    
    return app

if __name__ == "__main__":
    app = create_app()
    logger = Logger()
    logger.info("Starting Management Service...")
    try:
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Error starting the service: {e}")
        sys.exit(1)