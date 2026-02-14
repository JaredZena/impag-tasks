from flask import Blueprint, jsonify, request
from sqlalchemy import func
from auth import require_auth
from models import get_db, TaskCategory, Task, get_current_task_user

categories_bp = Blueprint("categories", __name__)


def serialize_category(cat, task_count=0):
    if not cat:
        return None
    return {
        "id": cat.id,
        "name": cat.name,
        "color": cat.color,
        "icon": cat.icon,
        "sort_order": cat.sort_order,
        "task_count": task_count,
    }


@categories_bp.route("/", methods=["GET"])
@categories_bp.route("", methods=["GET"])
@require_auth
def list_categories():
    db = next(get_db())
    try:
        # Subquery for task counts (non-archived tasks per category)
        task_count_subq = db.query(
            Task.category_id,
            func.count(Task.id).label("task_count")
        ).filter(Task.status != "archived").group_by(Task.category_id).subquery()

        results = db.query(TaskCategory, task_count_subq.c.task_count).outerjoin(
            task_count_subq, TaskCategory.id == task_count_subq.c.category_id
        ).filter(
            TaskCategory.is_active == True
        ).order_by(TaskCategory.sort_order.asc()).all()

        data = [serialize_category(cat, count or 0) for cat, count in results]
        return jsonify({"success": True, "data": data, "error": None, "message": None})
    finally:
        db.close()


@categories_bp.route("/", methods=["POST"])
@categories_bp.route("", methods=["POST"])
@require_auth
def create_category():
    db = next(get_db())
    try:
        current_user = get_current_task_user(db)
        if not current_user:
            return jsonify({"success": False, "data": None, "error": "User not found in task system", "message": None}), 404

        body = request.get_json()
        if not body or not body.get("name"):
            return jsonify({"success": False, "data": None, "error": "Name is required", "message": None}), 400

        # Auto-calculate sort_order as max + 1
        max_order = db.query(func.max(TaskCategory.sort_order)).filter(
            TaskCategory.is_active == True
        ).scalar() or 0

        category = TaskCategory(
            name=body["name"],
            color=body.get("color", "#6366f1"),
            icon=body.get("icon"),
            created_by=current_user.id,
            sort_order=max_order + 1,
        )
        db.add(category)
        db.commit()
        db.refresh(category)

        return jsonify({"success": True, "data": serialize_category(category), "error": None, "message": "Category created"}), 201
    finally:
        db.close()


# NOTE: /reorder must be registered BEFORE /<int:id> to avoid Flask matching "reorder" as an id
@categories_bp.route("/reorder", methods=["PUT"])
@require_auth
def reorder_categories():
    db = next(get_db())
    try:
        body = request.get_json()
        if not body or not body.get("order"):
            return jsonify({"success": False, "data": None, "error": "Order array is required", "message": None}), 400

        order = body["order"]
        for idx, category_id in enumerate(order):
            cat = db.query(TaskCategory).filter(TaskCategory.id == category_id).first()
            if cat:
                cat.sort_order = idx

        db.commit()
        return jsonify({"success": True, "data": None, "error": None, "message": "Categories reordered"})
    finally:
        db.close()


@categories_bp.route("/<int:id>", methods=["PUT"])
@require_auth
def update_category(id):
    db = next(get_db())
    try:
        category = db.query(TaskCategory).filter(
            TaskCategory.id == id,
            TaskCategory.is_active == True
        ).first()
        if not category:
            return jsonify({"success": False, "data": None, "error": "Category not found", "message": None}), 404

        body = request.get_json()
        if not body:
            return jsonify({"success": False, "data": None, "error": "Request body is required", "message": None}), 400

        for field in ["name", "color", "icon", "sort_order"]:
            if field in body:
                setattr(category, field, body[field])

        db.commit()
        db.refresh(category)

        return jsonify({"success": True, "data": serialize_category(category), "error": None, "message": "Category updated"})
    finally:
        db.close()


@categories_bp.route("/<int:id>", methods=["DELETE"])
@require_auth
def delete_category(id):
    db = next(get_db())
    try:
        category = db.query(TaskCategory).filter(
            TaskCategory.id == id,
            TaskCategory.is_active == True
        ).first()
        if not category:
            return jsonify({"success": False, "data": None, "error": "Category not found", "message": None}), 404

        category.is_active = False
        db.commit()

        return jsonify({"success": True, "data": {"id": id}, "error": None, "message": "Category deleted"})
    finally:
        db.close()
