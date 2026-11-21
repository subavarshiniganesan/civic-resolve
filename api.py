from flask import Blueprint, request, jsonify
from config import Config
from database.db import (
    get_all_complaints,
    get_complaint_by_ticket,
    update_complaint_status,
    get_complaint_metrics,
    upvote_complaint
)
from services.gemini_service import classify_civic_issue

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route("/classify", methods=["POST"])
def api_classify():
    """
    Live real-time preview classification endpoint.
    Allows frontend form to preview AI classification instantly.
    """
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    location = data.get("location", "").strip()
    user_category = data.get("user_category", "").strip()
    image_data = data.get("image_data")

    if not title and not description:
        return jsonify({"error": "Title or description required for classification"}), 400

    result = classify_civic_issue(
        title=title,
        description=description,
        location=location,
        user_category=user_category,
        image_data=image_data
    )
    return jsonify(result), 200

@api_bp.route("/complaints", methods=["GET"])
def api_get_complaints():
    """API endpoint to query complaints with filters."""
    status = request.args.get("status")
    priority = request.args.get("priority")
    department = request.args.get("department")
    search = request.args.get("search")

    complaints = get_all_complaints(
        status=status,
        priority=priority,
        department=department,
        search=search
    )
    return jsonify({"count": len(complaints), "complaints": complaints}), 200

@api_bp.route("/complaints/<ticket_id>", methods=["GET"])
def api_get_complaint(ticket_id):
    """Retrieve single complaint details."""
    complaint = get_complaint_by_ticket(ticket_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404
    return jsonify(complaint), 200

@api_bp.route("/complaints/<ticket_id>/status", methods=["POST"])
def api_update_status(ticket_id):
    """Update complaint status via JSON payload."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    admin_notes = data.get("admin_notes")

    if not new_status or new_status not in Config.STATUSES:
        return jsonify({"error": f"Invalid status. Must be one of {Config.STATUSES}"}), 400

    success = update_complaint_status(
        complaint_id=ticket_id,
        status=new_status,
        admin_notes=admin_notes
    )

    if not success:
        return jsonify({"error": "Failed to update complaint status"}), 404

    updated = get_complaint_by_ticket(ticket_id)
    return jsonify({"message": "Status updated successfully", "complaint": updated}), 200

@api_bp.route("/complaints/<ticket_id>/upvote", methods=["POST"])
def api_upvote(ticket_id):
    """Increment the public confirmation impact counter for an issue."""
    complaint = get_complaint_by_ticket(ticket_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404
        
    new_count = upvote_complaint(ticket_id)
    return jsonify({
        "success": True,
        "ticket_id": ticket_id,
        "upvotes": new_count
    }), 200

@api_bp.route("/metrics", methods=["GET"])
def api_metrics():
    """Get aggregate civic complaint metrics."""
    metrics = get_complaint_metrics()
    return jsonify(metrics), 200
