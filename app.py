from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from datetime import datetime, date
from config import database_url

from routes.users import users_bp
from routes.categories import categories_bp
from routes.tasks import tasks_bp
from routes.comments import comments_bp


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def create_app():
    app = Flask(__name__)
    app.json_provider_class = CustomJSONProvider
    app.json = CustomJSONProvider(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(categories_bp, url_prefix="/categories")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(comments_bp, url_prefix="/tasks")

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})

    @app.route("/")
    def root():
        return jsonify({"service": "impag-tasks", "status": "running"})

    return app


app = create_app()

if __name__ == "__main__":
    print(f"DB connected: {'Yes' if database_url else 'No'}")
    app.run(host="0.0.0.0", port=8001, debug=True)
