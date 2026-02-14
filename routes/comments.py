from flask import Blueprint, jsonify, request
from datetime import datetime
from auth import require_auth
from models import get_db, Task, TaskComment, get_current_task_user

comments_bp = Blueprint("comments", __name__)


def serialize_user(user):
    if not user:
        return None
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "role": user.role,
    }


def serialize_comment(comment):
    if not comment:
        return None
    return {
        "id": comment.id,
        "task_id": comment.task_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": comment.created_at,
        "last_updated": comment.last_updated,
        "user": serialize_user(comment.user),
    }


@comments_bp.route("/<int:task_id>/comments", methods=["GET"])
@require_auth
def list_comments(task_id):
    db = next(get_db())
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({"success": False, "data": None, "error": "Task not found", "message": None}), 404

        comments = db.query(TaskComment).filter(
            TaskComment.task_id == task_id
        ).order_by(TaskComment.created_at.asc()).all()

        return jsonify({"success": True, "data": [serialize_comment(c) for c in comments], "error": None, "message": None})
    finally:
        db.close()


@comments_bp.route("/<int:task_id>/comments", methods=["POST"])
@require_auth
def create_comment(task_id):
    db = next(get_db())
    try:
        current_user = get_current_task_user(db)
        if not current_user:
            return jsonify({"success": False, "data": None, "error": "User not found in task system", "message": None}), 404

        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({"success": False, "data": None, "error": "Task not found", "message": None}), 404

        body = request.get_json()
        if not body or not body.get("content", "").strip():
            return jsonify({"success": False, "data": None, "error": "Content is required", "message": None}), 400

        comment = TaskComment(
            task_id=task_id,
            user_id=current_user.id,
            content=body["content"].strip(),
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        return jsonify({"success": True, "data": serialize_comment(comment), "error": None, "message": "Comment added"}), 201
    finally:
        db.close()


@comments_bp.route("/<int:task_id>/comments/<int:comment_id>", methods=["PUT"])
@require_auth
def update_comment(task_id, comment_id):
    db = next(get_db())
    try:
        current_user = get_current_task_user(db)
        if not current_user:
            return jsonify({"success": False, "data": None, "error": "User not found in task system", "message": None}), 404

        comment = db.query(TaskComment).filter(
            TaskComment.id == comment_id,
            TaskComment.task_id == task_id
        ).first()
        if not comment:
            return jsonify({"success": False, "data": None, "error": "Comment not found", "message": None}), 404

        if comment.user_id != current_user.id:
            return jsonify({"success": False, "data": None, "error": "You can only edit your own comments", "message": None}), 403

        body = request.get_json()
        if not body or not body.get("content", "").strip():
            return jsonify({"success": False, "data": None, "error": "Content is required", "message": None}), 400

        comment.content = body["content"].strip()
        comment.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(comment)

        return jsonify({"success": True, "data": serialize_comment(comment), "error": None, "message": "Comment updated"})
    finally:
        db.close()


@comments_bp.route("/<int:task_id>/comments/<int:comment_id>", methods=["DELETE"])
@require_auth
def delete_comment(task_id, comment_id):
    db = next(get_db())
    try:
        current_user = get_current_task_user(db)
        if not current_user:
            return jsonify({"success": False, "data": None, "error": "User not found in task system", "message": None}), 404

        comment = db.query(TaskComment).filter(
            TaskComment.id == comment_id,
            TaskComment.task_id == task_id
        ).first()
        if not comment:
            return jsonify({"success": False, "data": None, "error": "Comment not found", "message": None}), 404

        if comment.user_id != current_user.id:
            return jsonify({"success": False, "data": None, "error": "You can only delete your own comments", "message": None}), 403

        db.delete(comment)
        db.commit()

        return jsonify({"success": True, "data": {"id": comment_id}, "error": None, "message": "Comment deleted"})
    finally:
        db.close()
