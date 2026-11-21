import os
from flask import Flask, render_template
from config import Config
from database.db import init_db
from routes.citizen import citizen_bp
from routes.admin import admin_bp
from routes.api import api_bp

def create_app():
    """Application factory for CivicResolve."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database tables and pre-populated sample complaints
    init_db()

    # Register blueprints
    app.register_blueprint(citizen_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Custom Jinja Template Filters
    @app.template_filter("priority_badge")
    def priority_badge_filter(priority):
        """Return styled badge HTML for priority classes with terracotta, sage, and ochre palette."""
        mapping = {
            "Critical": "bg-rose-100 dark:bg-rose-950/70 text-rose-800 dark:text-rose-200 border-rose-300 dark:border-rose-800 ring-1 ring-rose-500/20",
            "High": "bg-amber-100 dark:bg-amber-950/70 text-amber-900 dark:text-amber-200 border-amber-300 dark:border-amber-800 ring-1 ring-amber-500/20",
            "Medium": "bg-[#FAF0E6] dark:bg-stone-800 text-[#C84B31] dark:text-[#E06D53] border-[#F2D7CE] dark:border-stone-700 ring-1 ring-[#C84B31]/20",
            "Low": "bg-emerald-50 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-200 border-emerald-200 dark:border-emerald-800 ring-1 ring-emerald-500/20"
        }
        return mapping.get(priority, "bg-stone-100 dark:bg-stone-800 text-stone-800 dark:text-stone-200 border-stone-200 dark:border-stone-700")

    @app.template_filter("status_badge")
    def status_badge_filter(status):
        """Return styled badge HTML for issue progress statuses."""
        mapping = {
            "Reported": "bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 border-stone-300 dark:border-stone-700",
            "In Progress": "bg-amber-50 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800",
            "Resolved": "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800"
        }
        return mapping.get(status, "bg-stone-50 text-stone-700 border-stone-200")

    @app.template_filter("status_step")
    def status_step_filter(status):
        """Return step number for visual progress tracker (1=Reported, 2=In Progress, 3=Resolved)."""
        mapping = {
            "Reported": 1,
            "In Progress": 2,
            "Resolved": 3
        }
        return mapping.get(status, 1)

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("404.html", error_message="An internal server error occurred. Please try again later."), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=bool(os.environ.get("FLASK_DEBUG", 0)))
