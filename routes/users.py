from flask import Blueprint, jsonify
from auth import require_auth
from models import get_db, TaskUser, get_current_task_user

users_bp = Blueprint("users", __name__)


def serialize_user(user):
    if not user:
        return None
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "is_active": user.is_active,
    }


@users_bp.route("/", methods=["GET"])
@users_bp.route("", methods=["GET"])
@require_auth
def list_users():
    db = next(get_db())
    try:
        users = db.query(TaskUser).filter(TaskUser.is_active == True).all()
        return jsonify({"success": True, "data": [serialize_user(u) for u in users], "error": None, "message": None})
    finally:
        db.close()


@users_bp.route("/me", methods=["GET"])
@require_auth
def get_me():
    db = next(get_db())
    try:
        user = get_current_task_user(db)
        if not user:
            return jsonify({"success": False, "data": None, "error": "User not found in task system", "message": None}), 404
        return jsonify({"success": True, "data": serialize_user(user), "error": None, "message": None})
    finally:
        db.close()
