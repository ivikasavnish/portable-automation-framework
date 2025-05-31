import sys
from flask import Flask
from flask_cors import CORS

from api.routes.scenarios import scenario_routes
from api.routes.executions import execution_routes
from api.routes.data_providers import data_provider_routes
from api.routes.ai_services import ai_service_routes
from core.runner import Runner
from core.logger import Logger
from utils.config import Config

app = Flask(__name__)
CORS(app)

# Load configuration
config = Config()
app.config.update(config.get_flask_config())

# Initialize logger
logger = Logger()

# Register API routes
app.register_blueprint(scenario_routes, url_prefix='/api/v1/scenarios')
app.register_blueprint(execution_routes, url_prefix='/api/v1/executions')
app.register_blueprint(data_provider_routes, url_prefix='/api/v1/data-providers')
app.register_blueprint(ai_service_routes, url_prefix='/api/v1/ai')

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'automation-framework-management'}

def start_management_service():
    try:
        logger.info("Starting automation framework management service...")
        app.run(
            host=config.get('server.host', '0.0.0.0'),
            port=config.get('server.port', 8000),
            debug=config.get('server.debug', False)
        )
        logger.info("Management service started successfully.")
    except Exception as e:
        logger.error(f"Failed to start management service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_management_service()