from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from datetime import datetime, date
from config import database_url, claude_api_key
from apscheduler.schedulers.background import BackgroundScheduler

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


def _run_daily_classify():
    """Background job: classify uncategorized tasks once a day."""
    if not claude_api_key:
        return
    from models import get_db, Task, TaskCategory, ClassifyLog
    from services.classify_service import classify_tasks_with_ai
    from datetime import datetime as dt, timedelta as td

    COOLDOWN_MINUTES = 60
    db = next(get_db())
    try:
        # Guard: skip if already ran in the last COOLDOWN_MINUTES (multi-worker safety)
        cutoff = dt.utcnow() - td(minutes=COOLDOWN_MINUTES)
        recent = db.query(ClassifyLog).filter(ClassifyLog.ran_at >= cutoff).first()
        if recent:
            print("[auto-classify] Skipped — ran recently")
            return

        categories = db.query(TaskCategory).order_by(TaskCategory.sort_order).all()
        tasks = db.query(Task).filter(
            Task.status != "archived",
            Task.category_id.is_(None),
        ).all()

        if not tasks or not categories:
            print("[auto-classify] Nothing to classify")
            return

        tasks_for_ai = [{"id": t.id, "title": t.title, "description": t.description} for t in tasks]
        categories_for_ai = [{"id": c.id, "name": c.name} for c in categories]

        try:
            assignments = classify_tasks_with_ai(tasks_for_ai, categories_for_ai)
        except Exception as e:
            log = ClassifyLog(triggered_by="scheduler", tasks_examined=len(tasks), tasks_classified=0, tasks_no_match=0, status="error", error_message=str(e))
            db.add(log)
            db.commit()
            print(f"[auto-classify] Error: {e}")
            return

        classified = 0
        no_match = 0
        for task in tasks:
            cat_id = assignments.get(task.id)
            if cat_id is not None:
                task.category_id = cat_id
                task.last_updated = dt.utcnow()
                classified += 1
            else:
                no_match += 1

        log = ClassifyLog(
            triggered_by="scheduler",
            tasks_examined=len(tasks),
            tasks_classified=classified,
            tasks_no_match=no_match,
            status="success",
        )
        db.add(log)
        db.commit()
        print(f"[auto-classify] {classified} classified, {no_match} no match")
    except Exception as e:
        print(f"[auto-classify] Unexpected error: {e}")
    finally:
        db.close()


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

    # Daily auto-classification scheduler
    if claude_api_key:
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(_run_daily_classify, "cron", hour=8, minute=0, id="daily_classify", replace_existing=True)
        scheduler.start()

    return app


app = create_app()

if __name__ == "__main__":
    print(f"DB connected: {'Yes' if database_url else 'No'}")
    app.run(host="0.0.0.0", port=8001, debug=True)
