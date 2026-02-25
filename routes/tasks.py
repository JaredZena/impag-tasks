from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta, date
from auth import require_auth
from models import get_db, Task, TaskUser, TaskCategory, TaskComment, get_current_task_user, get_next_task_number
from services.archive_service import auto_archive_completed_tasks
from services.import_service import parse_import_text, detect_duplicates_with_ai, create_imported_tasks

tasks_bp = Blueprint("tasks", __name__)

VALID_STATUSES = {"pending", "in_progress", "done", "archived"}
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}


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


def serialize_category(cat):
    if not cat:
        return None
    return {
        "id": cat.id,
        "name": cat.name,
        "color": cat.color,
        "icon": cat.icon,
        "sort_order": cat.sort_order,
    }


def serialize_task(task):
    return {
        "id": task.id,
        "task_number": task.task_number,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "category_id": task.category_id,
        "created_by": task.created_by,
        "assigned_to": task.assigned_to,
        "completed_at": task.completed_at,
        "archived_at": task.archived_at,
        "created_at": task.created_at,
        "last_updated": task.last_updated,
        "creator": serialize_user(task.creator),
        "assignee": serialize_user(task.assignee),
        "category": serialize_category(task.category),
        "comment_count": len(task.comments) if task.comments else 0,
    }


# NOTE: /archive must be registered BEFORE /<int:id> to avoid route conflicts
@tasks_bp.route("/archive", methods=["GET"])
@require_auth
def list_archive():
    db = next(get_db())
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)

        tasks = db.query(Task).options(
            joinedload(Task.creator),
            joinedload(Task.assignee),
            joinedload(Task.category),
            joinedload(Task.comments),
        ).filter(
            Task.status == "archived",
            Task.archived_at >= cutoff
        ).order_by(Task.archived_at.desc()).all()

        return jsonify({"success": True, "data": [serialize_task(t) for t in tasks], "error": None, "message": None})
    finally:
        db.close()


@tasks_bp.route("/import", methods=["POST"])
@require_auth
def import_tasks():
    db = next(get_db())
    try:
        current_user = get_current_task_user(db)
        if not current_user:
            return jsonify({"success": False, "data": None, "error": "User not found in task system", "message": None}), 404

        body = request.get_json()
        text = body.get("text", "").strip() if body else ""
        if not text:
            return jsonify({"success": False, "data": None, "error": "No text provided", "message": None}), 400

        # Default assignee: Hernan (id=1) or override from body
        assigned_to = body.get("assigned_to", 1)

        # Step 1: Parse incoming text
        parsed = parse_import_text(text)
        if not parsed:
            return jsonify({"success": False, "data": None, "error": "No tasks could be parsed from the text", "message": None}), 400

        # Step 2: Fetch existing active tasks for duplicate comparison
        existing_tasks = db.query(Task).filter(Task.status != "archived").all()
        existing_for_ai = [
            {"id": t.id, "task_number": t.task_number, "title": t.title}
            for t in existing_tasks
        ]

        # Step 3: AI duplicate detection
        analyzed = detect_duplicates_with_ai(parsed, existing_for_ai)

        # Step 4: Separate new vs duplicates
        to_create = [t for t in analyzed if not t["is_duplicate"]]
        duplicates = [t for t in analyzed if t["is_duplicate"]]

        # Step 5: Create non-duplicate tasks
        created_tasks = create_imported_tasks(db, to_create, assigned_to=assigned_to, created_by=current_user.id)
        db.commit()

        # Reload with relationships for response
        created_ids = [t.id for t in created_tasks]
        if created_ids:
            created_tasks = db.query(Task).options(
                joinedload(Task.creator),
                joinedload(Task.assignee),
                joinedload(Task.category),
                joinedload(Task.comments),
            ).filter(Task.id.in_(created_ids)).all()

        return jsonify({
            "success": True,
            "data": {
                "created": [serialize_task(t) for t in created_tasks],
                "duplicates": [
                    {
                        "title": d["title"],
                        "task_number": d.get("task_number"),
                        "matched_existing_id": d.get("matched_existing_id"),
                        "reason": d.get("match_reason"),
                    }
                    for d in duplicates
                ],
                "total_parsed": len(parsed),
                "total_created": len(created_tasks),
                "total_duplicates": len(duplicates),
            },
            "error": None,
            "message": f"{len(created_tasks)} tareas creadas, {len(duplicates)} duplicadas omitidas",
        })
    finally:
        db.close()


@tasks_bp.route("/", methods=["GET"])
@tasks_bp.route("", methods=["GET"])
@require_auth
def list_tasks():
    db = next(get_db())
    try:
        # Lazy archival: auto-archive tasks done for > 3 days
        auto_archive_completed_tasks(db)

        query = db.query(Task).options(
            joinedload(Task.creator),
            joinedload(Task.assignee),
            joinedload(Task.category),
            joinedload(Task.comments),
        )

        # By default, exclude archived tasks
        status_filter = request.args.get("status")
        if status_filter:
            query = query.filter(Task.status == status_filter)
        else:
            query = query.filter(Task.status != "archived")

        # Filter: assigned_to
        assigned_to = request.args.get("assigned_to")
        if assigned_to:
            query = query.filter(Task.assigned_to == int(assigned_to))

        # Filter: created_by
        created_by = request.args.get("created_by")
        if created_by:
            query = query.filter(Task.created_by == int(created_by))

        # Filter: priority
        priority = request.args.get("priority")
        if priority:
            query = query.filter(Task.priority == priority)

        # Filter: category_id (0 or "none" means uncategorized)
        category_id = request.args.get("category_id")
        if category_id is not None:
            if category_id in ("0", "none"):
                query = query.filter(Task.category_id.is_(None))
            else:
                query = query.filter(Task.category_id == int(category_id))

        # Filter: due_before / due_after
        due_before = request.args.get("due_before")
        if due_before:
            query = query.filter(Task.due_date <= date.fromisoformat(due_before))

        due_after = request.args.get("due_after")
        if due_after:
            query = query.filter(Task.due_date >= date.fromisoformat(due_after))

        # Filter: search (ILIKE on title and description)
        search = request.args.get("search")
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term)
                )
            )

        # Pagination
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 50))

        # Order: priority (urgent first), due date (earliest first, nulls last), created date
        tasks = query.order_by(
            Task.created_at.desc()
        ).offset(skip).limit(limit).all()

        return jsonify({"success": True, "data": [serialize_task(t) for t in tasks], "error": None, "message": None})
    finally:
        db.close()


@tasks_bp.route("/<int:id>", methods=["GET"])
@require_auth
def get_task(id):
    db = next(get_db())
    try:
        task = db.query(Task).options(
            joinedload(Task.creator),
            joinedload(Task.assignee),
            joinedload(Task.category),
            joinedload(Task.comments).joinedload(TaskComment.user),
        ).filter(Task.id == id).first()

        if not task:
            return jsonify({"success": False, "data": None, "error": "Task not found", "message": None}), 404

        task_data = serialize_task(task)
        # Include full comments with user info for the detail view
        task_data["comments"] = [
            {
                "id": c.id,
                "task_id": c.task_id,
                "user_id": c.user_id,
                "content": c.content,
                "created_at": c.created_at,
                "last_updated": c.last_updated,
                "user": serialize_user(c.user),
            }
            for c in task.comments
        ]

        return jsonify({"success": True, "data": task_data, "error": None, "message": None})
    finally:
        db.close()


@tasks_bp.route("/", methods=["POST"])
@tasks_bp.route("", methods=["POST"])
@require_auth
def create_task():
    db = next(get_db())
    try:
        current_user = get_current_task_user(db)
        if not current_user:
            return jsonify({"success": False, "data": None, "error": "User not found in task system", "message": None}), 404

        body = request.get_json()
        if not body or not body.get("title", "").strip():
            return jsonify({"success": False, "data": None, "error": "Title is required", "message": None}), 400

        priority = body.get("priority", "medium")
        if priority not in VALID_PRIORITIES:
            return jsonify({"success": False, "data": None, "error": f"Invalid priority. Must be one of: {', '.join(VALID_PRIORITIES)}", "message": None}), 400

        task = Task(
            title=body["title"].strip(),
            description=body.get("description", "").strip() or None,
            priority=priority,
            due_date=date.fromisoformat(body["due_date"]) if body.get("due_date") else None,
            category_id=body.get("category_id"),
            assigned_to=body.get("assigned_to"),
            created_by=current_user.id,
            task_number=get_next_task_number(db),
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Eagerly load relationships for the response
        task = db.query(Task).options(
            joinedload(Task.creator),
            joinedload(Task.assignee),
            joinedload(Task.category),
            joinedload(Task.comments),
        ).filter(Task.id == task.id).first()

        return jsonify({"success": True, "data": serialize_task(task), "error": None, "message": "Task created"}), 201
    finally:
        db.close()


@tasks_bp.route("/<int:id>", methods=["PUT"])
@require_auth
def update_task(id):
    db = next(get_db())
    try:
        task = db.query(Task).filter(Task.id == id).first()
        if not task:
            return jsonify({"success": False, "data": None, "error": "Task not found", "message": None}), 404

        body = request.get_json()
        if not body:
            return jsonify({"success": False, "data": None, "error": "Request body is required", "message": None}), 400

        # Update allowed fields
        if "title" in body:
            title = body["title"].strip()
            if not title:
                return jsonify({"success": False, "data": None, "error": "Title cannot be empty", "message": None}), 400
            task.title = title

        if "description" in body:
            task.description = body["description"].strip() if body["description"] else None

        if "priority" in body:
            if body["priority"] not in VALID_PRIORITIES:
                return jsonify({"success": False, "data": None, "error": f"Invalid priority", "message": None}), 400
            task.priority = body["priority"]

        if "due_date" in body:
            task.due_date = date.fromisoformat(body["due_date"]) if body["due_date"] else None

        if "category_id" in body:
            task.category_id = body["category_id"]

        if "assigned_to" in body:
            task.assigned_to = body["assigned_to"]

        task.last_updated = datetime.utcnow()
        db.commit()

        # Reload with relationships
        task = db.query(Task).options(
            joinedload(Task.creator),
            joinedload(Task.assignee),
            joinedload(Task.category),
            joinedload(Task.comments),
        ).filter(Task.id == id).first()

        return jsonify({"success": True, "data": serialize_task(task), "error": None, "message": "Task updated"})
    finally:
        db.close()


@tasks_bp.route("/<int:id>/status", methods=["PUT"])
@require_auth
def update_task_status(id):
    db = next(get_db())
    try:
        task = db.query(Task).filter(Task.id == id).first()
        if not task:
            return jsonify({"success": False, "data": None, "error": "Task not found", "message": None}), 404

        body = request.get_json()
        new_status = body.get("status") if body else None
        if not new_status or new_status not in VALID_STATUSES:
            return jsonify({"success": False, "data": None, "error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}", "message": None}), 400

        old_status = task.status

        # Status transition logic
        task.status = new_status

        if new_status == "done" and old_status != "done":
            task.completed_at = datetime.utcnow()
        elif new_status != "done" and old_status == "done":
            task.completed_at = None

        if new_status == "archived":
            task.archived_at = datetime.utcnow()
            task.task_number = None  # Release number for reuse
        elif old_status == "archived" and new_status != "archived":
            task.archived_at = None
            task.task_number = get_next_task_number(db)  # Re-assign number

        task.last_updated = datetime.utcnow()
        db.commit()

        # Reload with relationships
        task = db.query(Task).options(
            joinedload(Task.creator),
            joinedload(Task.assignee),
            joinedload(Task.category),
            joinedload(Task.comments),
        ).filter(Task.id == id).first()

        return jsonify({"success": True, "data": serialize_task(task), "error": None, "message": f"Status changed to {new_status}"})
    finally:
        db.close()


@tasks_bp.route("/<int:id>", methods=["DELETE"])
@require_auth
def delete_task(id):
    db = next(get_db())
    try:
        task = db.query(Task).filter(Task.id == id).first()
        if not task:
            return jsonify({"success": False, "data": None, "error": "Task not found", "message": None}), 404

        # Soft delete: archive the task
        task.status = "archived"
        task.archived_at = datetime.utcnow()
        task.task_number = None  # Release number for reuse
        task.last_updated = datetime.utcnow()
        db.commit()

        return jsonify({"success": True, "data": {"id": id}, "error": None, "message": "Task archived"})
    finally:
        db.close()
