"""Analytics and reporting over stored violation records."""

from __future__ import annotations

from collections import Counter
from datetime import datetime

from storage.database import get_all_violations, count_by_type, get_total_count, delete_all_violations


def violation_statistics() -> dict:
    by_type = count_by_type()
    records = get_all_violations(limit=1000)
    confidences = [r["confidence"] for r in records if r.get("confidence")]
    plates_found = sum(1 for r in records if r.get("license_plate") not in (None, "", "UNKNOWN"))

    daily = Counter()
    for r in records:
        ts = r.get("timestamp", "")
        try:
            day = datetime.strptime(ts[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
            daily[day] += 1
        except ValueError:
            continue

    return {
        "total_violations": get_total_count(),
        "by_type": by_type,
        "avg_confidence": round(sum(confidences) / len(confidences), 3) if confidences else 0.0,
        "ocr_success_rate": round(plates_found / max(len(records), 1), 3),
        "daily_counts": dict(sorted(daily.items())),
    }


def generate_summary_report() -> str:
    stats = violation_statistics()
    lines = [
        "TRAFFIC VIOLATION ANALYTICS REPORT",
        "=" * 40,
        f"Total violations logged: {stats['total_violations']}",
        f"Average model confidence: {stats['avg_confidence'] * 100:.1f}%",
        f"OCR success rate: {stats['ocr_success_rate'] * 100:.1f}%",
        "",
        "Violations by type:",
    ]
    for vtype, count in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        lines.append(f"  - {vtype}: {count}")
    if stats["daily_counts"]:
        lines.extend(["", "Daily trend:"])
        for day, count in stats["daily_counts"].items():
            lines.append(f"  - {day}: {count}")
    return "\n".join(lines)


def clear_all_violation_data() -> dict:
    """Delete all violation records and return confirmation."""
    stats_before = violation_statistics()
    deleted_count = delete_all_violations()
    stats_after = violation_statistics()
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "violations_before": stats_before["total_violations"],
        "violations_after": stats_after["total_violations"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"Successfully deleted {deleted_count} violation records"
    }
