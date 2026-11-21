import base64
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from database.db import (
    create_complaint, 
    get_all_complaints, 
    get_complaint_by_ticket,
    get_complaint_metrics
)
from services.gemini_service import classify_civic_issue

citizen_bp = Blueprint("citizen", __name__)

@citizen_bp.route("/")
def index():
    """Citizen landing page with quick report form, platform metrics, and recent issues."""
    metrics = get_complaint_metrics()
    recent_complaints = get_all_complaints()[:3]
    return render_template(
        "index.html",
        categories=Config.CATEGORIES,
        metrics=metrics,
        recent_complaints=recent_complaints
    )

@citizen_bp.route("/report", methods=["POST"])
def submit_report():
    """Handle civic issue reporting with AI analysis and database storage."""
    try:
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        user_category = request.form.get("user_category", "").strip()
        
        # Coordinates if geolocation was granted
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        
        lat_val = float(latitude) if latitude and latitude.strip() else None
        lng_val = float(longitude) if longitude and longitude.strip() else None

        # Basic input validation
        if not title or len(title) < 5:
            flash("Please provide a descriptive title (at least 5 characters).", "error")
            return redirect(url_for("citizen.index"))

        if not description or len(description) < 15:
            flash("Please provide more detailed information in the description (at least 15 characters).", "error")
            return redirect(url_for("citizen.index"))

        if not location:
            flash("Please provide the location of the issue.", "error")
            return redirect(url_for("citizen.index"))

        # Process uploaded image (kept lightweight/base64 to strictly maintain repo size under 10MB)
        image_data = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename != "":
                # Ensure reasonable file size (under 3MB)
                raw_bytes = file.read()
                if len(raw_bytes) > 3 * 1024 * 1024:
                    flash("Uploaded image is too large. Please upload an image under 3 MB.", "warning")
                else:
                    mime = file.mimetype or "image/jpeg"
                    encoded = base64.b64encode(raw_bytes).decode("utf-8")
                    image_data = f"data:{mime};base64,{encoded}"

        # Run AI-Powered Classification via Gemini
        ai_result = classify_civic_issue(
            title=title,
            description=description,
            location=location,
            user_category=user_category,
            image_data=image_data
        )

        # Prepare record
        complaint_data = {
            "title": title,
            "description": description,
            "location": location,
            "latitude": lat_val,
            "longitude": lng_val,
            "user_category": user_category or ai_result.get("category", "General"),
            "category": ai_result.get("category", user_category or "Roads & Infrastructure"),
            "priority": ai_result.get("priority", "Medium"),
            "department": ai_result.get("department", "Department of Roads & Infrastructure"),
            "ai_summary": ai_result.get("ai_summary", "Citizen complaint registered."),
            "urgency_reason": ai_result.get("urgency_reason", "Standard municipal queue triage."),
            "sla_target": ai_result.get("sla_target", "24 Hours"),
            "upvotes": 1,
            "image_data": image_data,
            "status": "Reported"
        }

        new_issue = create_complaint(complaint_data)
        ticket_id = new_issue["ticket_id"]
        
        flash(f"Complaint successfully logged! Your tracking ticket is #{ticket_id}. Gemini classified this as {new_issue['priority']} priority routed to {new_issue['department']}.", "success")
        return redirect(url_for("citizen.issue_detail", ticket_id=ticket_id))

    except Exception as e:
        flash(f"An unexpected error occurred while processing your report: {str(e)}", "error")
        return redirect(url_for("citizen.index"))

@citizen_bp.route("/track")
def track():
    """Citizen Issue Tracking Dashboard with live filterable status, priority badges, and search."""
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
        "tracker.html",
        complaints=complaints,
        metrics=metrics,
        categories=Config.CATEGORIES,
        priorities=Config.PRIORITIES,
        departments=Config.DEPARTMENTS,
        current_status=status,
        current_priority=priority,
        current_department=department,
        current_search=search
    )

@citizen_bp.route("/issue/<ticket_id>")
def issue_detail(ticket_id):
    """Detailed single issue view with AI classification breakdown and progress tracker."""
    complaint = get_complaint_by_ticket(ticket_id)
    if not complaint:
        flash(f"No civic complaint found with Ticket ID #{ticket_id}.", "error")
        return redirect(url_for("citizen.track"))

    return render_template("detail.html", complaint=complaint)
