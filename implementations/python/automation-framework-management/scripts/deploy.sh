from api.routes.scenarios import scenarios_blueprint
from api.routes.executions import executions_blueprint
from api.routes.data_providers import data_providers_blueprint
from api.routes.ai_services import ai_services_blueprint
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(scenarios_blueprint, url_prefix='/api/scenarios')
    app.register_blueprint(executions_blueprint, url_prefix='/api/executions')
    app.register_blueprint(data_providers_blueprint, url_prefix='/api/data-providers')
    app.register_blueprint(ai_services_blueprint, url_prefix='/api/ai-services')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)