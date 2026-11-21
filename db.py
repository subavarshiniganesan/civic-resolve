import sqlite3
import random
import string
import datetime
from pathlib import Path
from config import Config

def get_db_connection():
    """Create and return a database connection with row factory enabled."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_ticket_id():
    """Generate a clean, unique human-readable ticket ID like CR-2026-4821."""
    random_digits = "".join(random.choices(string.digits, k=4))
    return f"CR-2026-{random_digits}"

def init_db():
    """Initialize database tables and pre-populate sample data if table is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            user_category TEXT,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            department TEXT NOT NULL,
            ai_summary TEXT,
            urgency_reason TEXT,
            sla_target TEXT DEFAULT '24 Hours',
            upvotes INTEGER DEFAULT 1,
            image_data TEXT,
            status TEXT NOT NULL DEFAULT 'Reported',
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_ticket ON complaints(ticket_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_priority ON complaints(priority);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_department ON complaints(department);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaints_created_at ON complaints(created_at);")
    
    # Ensure backward-compatible column migrations
    cursor.execute("PRAGMA table_info(complaints)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if "sla_target" not in existing_cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN sla_target TEXT DEFAULT '24 Hours'")
    if "upvotes" not in existing_cols:
        cursor.execute("ALTER TABLE complaints ADD COLUMN upvotes INTEGER DEFAULT 1")

    conn.commit()
    
    # Check if empty to pre-populate 3 realistic civic complaints
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]
    
    if count == 0:
        seed_sample_complaints(cursor)
        conn.commit()
        
    conn.close()

def seed_sample_complaints(cursor):
    """Pre-populate 3 realistic sample civic complaints for hackathon demo."""
    now = datetime.datetime.now(datetime.timezone.utc)
    two_hours_ago = (now - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    one_day_ago = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    five_hours_ago = (now - datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")

    samples = [
        (
            "CR-2026-101",
            "Hazardous open pothole causing vehicle skidding at junction",
            "A dangerous pothole approximately 2.5 feet wide and 8 inches deep has emerged immediately after the zebra crossing. Two two-wheelers skidded during yesterday's evening shower. High collision risk during morning peak school transit hours.",
            "Crosscut Road, Near Town Hall Junction, Coimbatore",
            11.0168,
            76.9558,
            "Roads & Infrastructure",
            "Roads & Infrastructure",
            "Critical",
            "Department of Roads & Infrastructure",
            "Deep vehicular hazard on high-density arterial crossing posing acute skidding danger to two-wheelers and school transport.",
            "Immediate threat of vehicular collision and bodily injury during rain-induced road erosion in a congested intersection.",
            "4 Hours",
            28,
            None,
            "Reported",
            "Dispatched alert to zonal road maintenance supervisor.",
            two_hours_ago,
            two_hours_ago
        ),
        (
            "CR-2026-102",
            "Overflowing public waste bin obstructing pedestrian bus shelter",
            "Municipal waste bins opposite the PSG Tech entrance bus shelter have overflowed onto the walkway for 4 consecutive days. Debris is scattered across 15 meters, generating foul odor and attracting stray dogs.",
            "Avinashi Road, Opposite PSG Tech Main Gate, Peelamedu",
            11.0247,
            77.0028,
            "Waste Management",
            "Waste Management",
            "Medium",
            "Municipal Solid Waste Management",
            "Sidewalk blockage and uncollected organic waste accumulation adjacent to high-traffic educational transit stop.",
            "Public sanitation hazard, pedestrian pathway obstruction forcing commuters onto busy highway lane.",
            "72 Hours",
            14,
            None,
            "In Progress",
            "Compactor truck #14 assigned for clearance by 2:00 PM.",
            one_day_ago,
            one_day_ago
        ),
        (
            "CR-2026-103",
            "Sparking street lamp wiring near neighborhood children's park",
            "Streetlight pole #47 has an unlatched electrical junction box with frayed live wires sparking during rain. The entire adjacent walkway is unlit at night, creating severe electrocution and safety concerns.",
            "Park Avenue, 3rd Cross Street, Gandhipuram",
            11.0183,
            76.9688,
            "Streetlights & Electrical",
            "Streetlights & Electrical",
            "High",
            "Electrical & Lighting Utility",
            "Exposed live wiring sparking in damp conditions with localized blackout near public park perimeter.",
            "Severe electric shock risk to pedestrians and children, accompanied by complete nocturnal blindspot in residential corridor.",
            "24 Hours",
            19,
            None,
            "Reported",
            None,
            five_hours_ago,
            five_hours_ago
        )
    ]
    
    cursor.executemany("""
        INSERT INTO complaints (
            ticket_id, title, description, location, latitude, longitude,
            user_category, category, priority, department, ai_summary,
            urgency_reason, sla_target, upvotes, image_data, status, admin_notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, samples)

def create_complaint(data):
    """Insert a new civic complaint into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure ticket_id uniqueness
    ticket_id = generate_ticket_id()
    while True:
        cursor.execute("SELECT id FROM complaints WHERE ticket_id = ?", (ticket_id,))
        if not cursor.fetchone():
            break
        ticket_id = generate_ticket_id()
        
    cursor.execute("""
        INSERT INTO complaints (
            ticket_id, title, description, location, latitude, longitude,
            user_category, category, priority, department, ai_summary,
            urgency_reason, sla_target, upvotes, image_data, status, admin_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        data.get("title"),
        data.get("description"),
        data.get("location"),
        data.get("latitude"),
        data.get("longitude"),
        data.get("user_category"),
        data.get("category"),
        data.get("priority"),
        data.get("department"),
        data.get("ai_summary"),
        data.get("urgency_reason"),
        data.get("sla_target", "24 Hours"),
        data.get("upvotes", 1),
        data.get("image_data"),
        data.get("status", "Reported"),
        data.get("admin_notes", None)
    ))
    
    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return get_complaint_by_id(complaint_id)

def upvote_complaint(ticket_id):
    """Increment the community upvote/confirmation counter for a complaint."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE complaints 
        SET upvotes = COALESCE(upvotes, 0) + 1 
        WHERE ticket_id = ? OR id = ?
    """, (str(ticket_id), str(ticket_id)))
    conn.commit()
    cursor.execute("SELECT upvotes FROM complaints WHERE ticket_id = ? OR id = ?", (str(ticket_id), str(ticket_id)))
    row = cursor.fetchone()
    new_count = row[0] if row else 1
    conn.close()
    return new_count
    
    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return get_complaint_by_id(complaint_id)

def get_all_complaints(status=None, priority=None, department=None, search=None):
    """Retrieve all complaints with optional filtering and search."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM complaints WHERE 1=1"
    params = []
    
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
        
    if priority and priority != "All":
        query += " AND priority = ?"
        params.append(priority)
        
    if department and department != "All":
        query += " AND department = ?"
        params.append(department)
        
    if search:
        search_term = f"%{search.strip()}%"
        query += " AND (title LIKE ? OR description LIKE ? OR location LIKE ? OR ticket_id LIKE ?)"
        params.extend([search_term, search_term, search_term, search_term])
        
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_complaint_by_id(complaint_id):
    """Retrieve a single complaint by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_complaint_by_ticket(ticket_id):
    """Retrieve a single complaint by ticket ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_complaint_status(complaint_id, status, admin_notes=None):
    """Update issue status ('Reported', 'In Progress', 'Resolved') and optional admin notes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    if admin_notes is not None:
        cursor.execute("""
            UPDATE complaints 
            SET status = ?, admin_notes = ?, updated_at = ?
            WHERE id = ? OR ticket_id = ?
        """, (status, admin_notes, now, complaint_id, str(complaint_id)))
    else:
        cursor.execute("""
            UPDATE complaints 
            SET status = ?, updated_at = ?
            WHERE id = ? OR ticket_id = ?
        """, (status, now, complaint_id, str(complaint_id)))
        
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return updated

def get_complaint_metrics():
    """Compute aggregate analytics for dashboard cards and charts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Reported'")
    reported = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
    in_progress = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE priority = 'Critical' AND status != 'Resolved'")
    critical_pending = cursor.fetchone()[0]
    
    # Priority Breakdown
    cursor.execute("SELECT priority, COUNT(*) FROM complaints GROUP BY priority")
    priority_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Department Breakdown
    cursor.execute("SELECT department, COUNT(*) FROM complaints GROUP BY department")
    department_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "total": total,
        "reported": reported,
        "in_progress": in_progress,
        "resolved": resolved,
        "critical_pending": critical_pending,
        "priorities": priority_counts,
        "departments": department_counts
    }
