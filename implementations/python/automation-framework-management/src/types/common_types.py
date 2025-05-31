from api.routes.scenarios import scenario_routes
from api.routes.executions import execution_routes
from api.routes.data_providers import data_provider_routes
from api.routes.ai_services import ai_service_routes
from core.runner import Runner
from flask import Flask

app = Flask(__name__)

# Register API routes
app.register_blueprint(scenario_routes)
app.register_blueprint(execution_routes)
app.register_blueprint(data_provider_routes)
app.register_blueprint(ai_service_routes)

@app.route('/')
def index():
    return "Welcome to the Management Service!"

if __name__ == '__main__':
    runner = Runner()
    runner.initialize()
    app.run(debug=True)