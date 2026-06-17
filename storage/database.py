"""SQLite persistence for violation records."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime


DB_PATH = os.path.join("storage", "violations.db")


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            violation_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            license_plate TEXT,
            plate_confidence REAL,
            vehicle_class TEXT,
            bbox TEXT,
            image_source TEXT,
            evidence_path TEXT,
            timestamp TEXT NOT NULL,
            metadata TEXT,
            speed REAL,
            speed_limit REAL
        )
    """)
    
    # Migration: Add speed columns if they don't exist (for existing databases)
    try:
        conn.execute("ALTER TABLE violations ADD COLUMN speed REAL")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        conn.execute("ALTER TABLE violations ADD COLUMN speed_limit REAL")
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    return conn


def save_violation(record: dict) -> int:
    conn = _connect()
    cur = conn.execute(
        """
        INSERT INTO violations
        (violation_type, confidence, license_plate, plate_confidence, vehicle_class,
         bbox, image_source, evidence_path, timestamp, metadata, speed, speed_limit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["violation_type"],
            record["confidence"],
            record.get("license_plate", "UNKNOWN"),
            record.get("plate_confidence", 0.0),
            record.get("vehicle_class", ""),
            json.dumps(record.get("bbox", [])),
            record.get("image_source", ""),
            record.get("evidence_path", ""),
            record.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            json.dumps(record.get("metadata", {})),
            record.get("speed", None),
            record.get("speed_limit", None),
        ),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def search_violations(
    query: str = "",
    violation_type: str = "",
    limit: int = 100,
) -> list[dict]:
    conn = _connect()
    sql = "SELECT * FROM violations WHERE 1=1"
    params: list = []
    if query:
        sql += " AND (license_plate LIKE ? OR image_source LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if violation_type:
        sql += " AND violation_type = ?"
        params.append(violation_type)
    sql += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_violations(limit: int = 500) -> list[dict]:
    return search_violations(limit=limit)


def count_by_type() -> dict[str, int]:
    conn = _connect()
    rows = conn.execute(
        "SELECT violation_type, COUNT(*) as cnt FROM violations GROUP BY violation_type"
    ).fetchall()
    conn.close()
    return {r["violation_type"]: r["cnt"] for r in rows}


def get_total_count() -> int:
    conn = _connect()
    row = conn.execute("SELECT COUNT(*) as cnt FROM violations").fetchone()
    conn.close()
    return row["cnt"] if row else 0


def delete_all_violations() -> int:
    """Delete all violation records from the database."""
    conn = _connect()
    cur = conn.execute("DELETE FROM violations")
    deleted_count = cur.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def delete_violation_by_id(violation_id: int) -> bool:
    """Delete a specific violation record by ID."""
    conn = _connect()
    cur = conn.execute("DELETE FROM violations WHERE id = ?", (violation_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
