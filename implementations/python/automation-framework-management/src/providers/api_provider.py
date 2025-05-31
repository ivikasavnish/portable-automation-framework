src/main.py:

import sys
from api.routes.scenarios import scenario_routes
from api.routes.executions import execution_routes
from api.routes.data_providers import data_provider_routes
from api.routes.ai_services import ai_service_routes
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register API routes
    app.register_blueprint(scenario_routes)
    app.register_blueprint(execution_routes)
    app.register_blueprint(data_provider_routes)
    app.register_blueprint(ai_service_routes)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)