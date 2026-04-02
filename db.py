"""
Competitive Intelligence Monitor — SQLite database operations.
8 tables: competitors, competitor_sources, raw_competitive_data, competitive_moves,
ai_insights, roadmap_signals, market_position, data_collection_log.
"""

import sqlite3
import json
from datetime import datetime, timezone
from contextlib import contextmanager

DB_PATH = "competitive_intelligence.db"


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    """Initialize database schema."""
    with get_db() as conn:
        c = conn.cursor()

        # Competitors table
        c.execute("""
            CREATE TABLE IF NOT EXISTS competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                website TEXT,
                market_segment TEXT,
                logo_url TEXT,
                threat_baseline TEXT DEFAULT 'MEDIUM',
                status TEXT DEFAULT 'ACTIVE',
                added_date TEXT NOT NULL,
                last_monitored_at TEXT
            )
        """)

        # Competitor data sources
        c.execute("""
            CREATE TABLE IF NOT EXISTS competitor_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER NOT NULL,
                source_type TEXT NOT NULL,
                source_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                auth_token TEXT,
                last_check_at TEXT,
                next_check_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id)
            )
        """)

        # Raw competitive data (before processing)
        c.execute("""
            CREATE TABLE IF NOT EXISTS raw_competitive_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER NOT NULL,
                source_type TEXT NOT NULL,
                raw_content TEXT,
                detected_change BOOLEAN DEFAULT 0,
                collected_at TEXT NOT NULL,
                processed BOOLEAN DEFAULT 0,
                processed_at TEXT,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id)
            )
        """)

        # Competitive moves (processed intelligence)
        c.execute("""
            CREATE TABLE IF NOT EXISTS competitive_moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER NOT NULL,
                source_data_id INTEGER,
                dimension TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                announced_date TEXT,
                observed_date TEXT,
                collected_by TEXT DEFAULT 'AUTO',
                collected_by_source TEXT,
                validation_status TEXT DEFAULT 'AUTO_DETECTED',
                validated_by TEXT,
                validation_date TEXT,
                impact_score INTEGER,
                threat_level TEXT,
                opportunity BOOLEAN DEFAULT 0,
                source_url TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id),
                FOREIGN KEY (source_data_id) REFERENCES raw_competitive_data(id)
            )
        """)

        # AI-generated insights
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                move_id INTEGER NOT NULL,
                insight_type TEXT,
                generated_summary TEXT,
                strategic_implication TEXT,
                recommended_response TEXT,
                confidence_score REAL,
                generated_at TEXT NOT NULL,
                FOREIGN KEY (move_id) REFERENCES competitive_moves(id)
            )
        """)

        # Roadmap signals (how moves impact our roadmap)
        c.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                move_id INTEGER NOT NULL,
                our_roadmap_item_id TEXT,
                signal_type TEXT,
                reasoning TEXT,
                confidence_score REAL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (move_id) REFERENCES competitive_moves(id)
            )
        """)

        # Market position snapshots
        c.execute("""
            CREATE TABLE IF NOT EXISTS market_position (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER NOT NULL,
                feature_gaps TEXT,
                price_comparison TEXT,
                positioning_diff TEXT,
                calculated_at TEXT NOT NULL,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id)
            )
        """)

        # Data collection run logs
        c.execute("""
            CREATE TABLE IF NOT EXISTS data_collection_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collector_name TEXT NOT NULL,
                competitor_id INTEGER,
                items_found INTEGER DEFAULT 0,
                items_processed INTEGER DEFAULT 0,
                errors TEXT,
                ran_at TEXT NOT NULL,
                duration_seconds REAL,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id)
            )
        """)

        # App settings (key-value store for API keys and config)
        c.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.commit()


# ── COMPETITOR CRUD ──────────────────────────────────────────────────────────

def create_competitor(name: str, website: str = None, market_segment: str = None, threat_baseline: str = "MEDIUM"):
    """Add a new competitor."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO competitors (name, website, market_segment, threat_baseline, added_date)
            VALUES (?, ?, ?, ?, ?)
        """, (name, website, market_segment, threat_baseline, now))
        return c.lastrowid


def get_competitor(competitor_id: int) -> dict:
    """Get competitor by ID."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM competitors WHERE id = ?", (competitor_id,))
        row = c.fetchone()
        return dict(row) if row else None


def get_all_competitors() -> list:
    """Get all competitors."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM competitors ORDER BY added_date DESC")
        return [dict(row) for row in c.fetchall()]


def update_competitor(competitor_id: int, **kwargs):
    """Update competitor fields."""
    with get_db() as conn:
        c = conn.cursor()
        allowed_fields = ["threat_baseline", "status", "last_monitored_at"]
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
            c.execute(f"UPDATE competitors SET {set_clause} WHERE id = ?",
                     list(updates.values()) + [competitor_id])


# ── COMPETITOR SOURCES CRUD ──────────────────────────────────────────────────

def register_source(competitor_id: int, source_type: str, source_url: str = None):
    """Register a data source for a competitor."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO competitor_sources (competitor_id, source_type, source_url, created_at)
            VALUES (?, ?, ?, ?)
        """, (competitor_id, source_type, source_url, now))
        return c.lastrowid


def get_sources_for_competitor(competitor_id: int, active_only: bool = True) -> list:
    """Get data sources for a competitor."""
    with get_db() as conn:
        c = conn.cursor()
        if active_only:
            c.execute("SELECT * FROM competitor_sources WHERE competitor_id = ? AND is_active = 1",
                     (competitor_id,))
        else:
            c.execute("SELECT * FROM competitor_sources WHERE competitor_id = ?", (competitor_id,))
        return [dict(row) for row in c.fetchall()]


# ── RAW DATA CRUD ────────────────────────────────────────────────────────────

def log_raw_data(competitor_id: int, source_type: str, raw_content: str, detected_change: bool = False):
    """Log raw collected data."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO raw_competitive_data (competitor_id, source_type, raw_content, detected_change, collected_at)
            VALUES (?, ?, ?, ?, ?)
        """, (competitor_id, source_type, raw_content, detected_change, now))
        return c.lastrowid


def get_unprocessed_data() -> list:
    """Get raw data that hasn't been processed yet."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM raw_competitive_data WHERE processed = 0 ORDER BY collected_at DESC")
        return [dict(row) for row in c.fetchall()]


def mark_data_processed(data_id: int):
    """Mark raw data as processed."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("UPDATE raw_competitive_data SET processed = 1, processed_at = ? WHERE id = ?",
                 (now, data_id))


# ── COMPETITIVE MOVES CRUD ──────────────────────────────────────────────────

def log_move(competitor_id: int, dimension: str, title: str, description: str = None,
            threat_level: str = "MEDIUM", opportunity: bool = False, source_url: str = None,
            source_data_id: int = None, collected_by_source: str = None):
    """Log a competitive move."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO competitive_moves
            (competitor_id, source_data_id, dimension, title, description, threat_level,
             opportunity, source_url, collected_by_source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (competitor_id, source_data_id, dimension, title, description, threat_level,
              opportunity, source_url, collected_by_source, now, now))
        return c.lastrowid


def get_moves_for_competitor(competitor_id: int, validation_status: str = None) -> list:
    """Get moves for a competitor."""
    with get_db() as conn:
        c = conn.cursor()
        if validation_status:
            c.execute("""
                SELECT * FROM competitive_moves
                WHERE competitor_id = ? AND validation_status = ?
                ORDER BY created_at DESC
            """, (competitor_id, validation_status))
        else:
            c.execute("""
                SELECT * FROM competitive_moves
                WHERE competitor_id = ?
                ORDER BY created_at DESC
            """, (competitor_id,))
        return [dict(row) for row in c.fetchall()]


def get_unvalidated_moves() -> list:
    """Get all moves awaiting validation."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM competitive_moves
            WHERE validation_status = 'AUTO_DETECTED'
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in c.fetchall()]


def validate_move(move_id: int, validated_by: str = "PM"):
    """Validate a move (PM confirmed it)."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            UPDATE competitive_moves
            SET validation_status = 'VALIDATED', validated_by = ?, validation_date = ?, updated_at = ?
            WHERE id = ?
        """, (validated_by, now, now, move_id))


def dismiss_move(move_id: int):
    """Dismiss a move (PM said it's not relevant)."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            UPDATE competitive_moves
            SET validation_status = 'DISMISSED', updated_at = ?
            WHERE id = ?
        """, (now, move_id))


def get_all_moves(limit: int = 100) -> list:
    """Get recent validated moves across all competitors."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM competitive_moves
            WHERE validation_status = 'VALIDATED'
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in c.fetchall()]


# ── AI INSIGHTS CRUD ─────────────────────────────────────────────────────────

def save_insight(move_id: int, insight_type: str, generated_summary: str,
                strategic_implication: str = None, recommended_response: str = None,
                confidence_score: float = 0.9):
    """Save AI-generated insight for a move."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO ai_insights
            (move_id, insight_type, generated_summary, strategic_implication, recommended_response, confidence_score, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (move_id, insight_type, generated_summary, strategic_implication, recommended_response, confidence_score, now))
        return c.lastrowid


def get_insights_for_move(move_id: int) -> dict:
    """Get AI insights for a specific move."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM ai_insights WHERE move_id = ? ORDER BY generated_at DESC", (move_id,))
        row = c.fetchone()
        return dict(row) if row else None


# ── ROADMAP SIGNALS ──────────────────────────────────────────────────────────

def save_roadmap_signal(move_id: int, signal_type: str, reasoning: str = None,
                       our_roadmap_item_id: str = None, confidence_score: float = 0.85):
    """Save roadmap impact signal."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO roadmap_signals
            (move_id, our_roadmap_item_id, signal_type, reasoning, confidence_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (move_id, our_roadmap_item_id, signal_type, reasoning, confidence_score, now))
        return c.lastrowid


def get_roadmap_signals() -> list:
    """Get all roadmap signals."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM roadmap_signals ORDER BY created_at DESC")
        return [dict(row) for row in c.fetchall()]


# ── COLLECTION LOGGING ───────────────────────────────────────────────────────

def log_collection_run(collector_name: str, items_found: int = 0, items_processed: int = 0,
                      errors: str = None, duration_seconds: float = 0, competitor_id: int = None):
    """Log a data collection run."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO data_collection_log
            (collector_name, competitor_id, items_found, items_processed, errors, ran_at, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (collector_name, competitor_id, items_found, items_processed, errors, now, duration_seconds))


def get_collection_logs(limit: int = 50) -> list:
    """Get recent collection logs."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM data_collection_log
            ORDER BY ran_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in c.fetchall()]


def get_last_collection_run() -> dict:
    """Get the most recent collection run across all collectors."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM data_collection_log
            ORDER BY ran_at DESC
            LIMIT 1
        """)
        row = c.fetchone()
        return dict(row) if row else None


def get_newsapi_usage() -> dict:
    """Get NewsAPI usage tracking (1,000/month limit)."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) as total_calls
            FROM data_collection_log
            WHERE collector_name = 'news_monitor'
            AND ran_at >= datetime('now', 'start of month')
        """)
        row = c.fetchone()
        total = row['total_calls'] if row else 0
        # Estimate: ~30-35 API calls per day = 1000/month
        return {
            "used": min(total * 30, 1000),  # Rough estimate
            "limit": 1000,
            "percentage": min((total * 30 / 1000) * 100, 100)
        }


# ── STATS ────────────────────────────────────────────────────────────────────

def get_stats() -> dict:
    """Get dashboard stats."""
    with get_db() as conn:
        c = conn.cursor()

        c.execute("SELECT COUNT(*) as count FROM competitors WHERE status = 'ACTIVE'")
        tracked = c.fetchone()['count']

        c.execute("SELECT COUNT(*) as count FROM competitive_moves WHERE validation_status = 'AUTO_DETECTED'")
        unvalidated = c.fetchone()['count']

        c.execute("SELECT COUNT(*) as count FROM competitive_moves WHERE threat_level = 'HIGH'")
        high_threats = c.fetchone()['count']

        c.execute("SELECT COUNT(*) as count FROM competitive_moves WHERE validation_status = 'VALIDATED'")
        validated = c.fetchone()['count']

        c.execute("SELECT COUNT(*) as count FROM competitive_moves WHERE opportunity = 1")
        opportunities = c.fetchone()['count']

        return {
            "tracked_competitors": tracked,
            "auto_detected_moves": unvalidated,
            "high_threats": high_threats,
            "validated_moves": validated,
            "opportunities": opportunities
        }


# ── APP SETTINGS ─────────────────────────────────────────────────────────────

def save_setting(key: str, value: str):
    """Save an app setting (e.g., API key) to the database."""
    with get_db() as conn:
        c = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """, (key, value, now))


def get_setting(key: str) -> str:
    """Get an app setting value by key. Returns None if not found."""
    try:
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
            row = c.fetchone()
            return row["value"] if row else None
    except Exception:
        return None


if __name__ == "__main__":
    init_db()
    print("✓ Database initialized")
