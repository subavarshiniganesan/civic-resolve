import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

class Config:
    """Application configuration settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "civic-resolve-hackathon-2026-key")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "civic_resolve.db"))
    
    # Supported Civic Categories
    CATEGORIES = [
        "Roads & Infrastructure",
        "Waste Management",
        "Water & Drainage",
        "Streetlights & Electrical",
        "Public Safety",
        "Parks & Public Spaces",
        "Sanitation & Health",
        "Traffic & Parking",
        "Other"
    ]
    
    # Priority Levels with Color Badges
    PRIORITIES = ["Low", "Medium", "High", "Critical"]
    
    # Complaint Status Workflow
    STATUSES = ["Reported", "In Progress", "Resolved"]
    
    # Department Mappings
    DEPARTMENTS = [
        "Department of Roads & Infrastructure",
        "Municipal Solid Waste Management",
        "Water Supply & Sewerage Board",
        "Electrical & Lighting Utility",
        "Public Safety & Civil Defence",
        "Department of Public Health & Sanitation",
        "Traffic Police & Transportation Authority",
        "Parks & Recreation Department"
    ]
