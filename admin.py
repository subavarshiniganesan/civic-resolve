from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from database.db import (
    get_all_complaints, 
    get_complaint_metrics, 
    update_complaint_status, 
    get_complaint_by_ticket
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
def dashboard():
    """Admin Authority Dashboard for triaging, filtering, and updating civic complaints."""
    status = request.args.get("status", "All")
    priority = request.args.get("priority", "All")
    department = request.args.get("department", "All")
    search = request.args.get("search", "")

    complaints = get_all_complaints(
        status=status,
        priority=priority,
        department=department,
        search=search
    )
    metrics = get_complaint_metrics()

    return render_template(
        "admin.html",
        complaints=complaints,
        metrics=metrics,
        priorities=Config.PRIORITIES,
        departments=Config.DEPARTMENTS,
        statuses=Config.STATUSES,
        current_status=status,
        current_priority=priority,
        current_department=department,
        current_search=search
    )

@admin_bp.route("/update-status", methods=["POST"])
def update_status():
    """Handle status changes ('Reported', 'In Progress', 'Resolved') and official remarks."""
    ticket_id = request.form.get("ticket_id")
    new_status = request.form.get("status")
    admin_notes = request.form.get("admin_notes", "").strip()

    if not ticket_id or not new_status:
        flash("Invalid request. Ticket ID and Status are required.", "error")
        return redirect(url_for("admin.dashboard"))

    if new_status not in Config.STATUSES:
        flash(f"Invalid status value: {new_status}", "error")
        return redirect(url_for("admin.dashboard"))

    success = update_complaint_status(
        complaint_id=ticket_id,
        status=new_status,
        admin_notes=admin_notes if admin_notes else None
    )

    if success:
        flash(f"Ticket #{ticket_id} status updated to '{new_status}' successfully.", "success")
    else:
        flash(f"Failed to find or update Ticket #{ticket_id}.", "error")

    # Redirect back to referring page or admin dashboard
    ref = request.referrer
    if ref and "/issue/" in ref:
        return redirect(ref)
    return redirect(url_for("admin.dashboard"))
