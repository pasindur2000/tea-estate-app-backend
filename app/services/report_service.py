"""
services/report_service.py
--------------------------
Generates summary reports that are only accessible to directors.

Currently supports:
  - Monthly tea harvest summary (total kg, total earnings per worker)
  - Attendance summary for a given date range
  - Worker expense list

These can be extended as the project grows.
"""

from app.config import get_firestore_client
from datetime import date


async def monthly_tea_summary(estate_id: str, year: int, month: int) -> dict:
    """
    Return total kg picked and earnings per worker for a given month.
    Example: year=2026, month=5 → all entries in 2026-05-xx
    """
    db = get_firestore_client()

    # Build date prefix for filtering, e.g. "2026-05"
    prefix = f"{year}-{str(month).zfill(2)}"

    docs = (
        db.collection("Tea_entries")
        .where("estateId", "==", estate_id)
        .stream()
    )

    worker_totals: dict[str, dict] = {}

    for doc in docs:
        entry = doc.to_dict()
        if not entry.get("date", "").startswith(prefix):
            continue

        wid = entry["workerId"]
        if wid not in worker_totals:
            worker_totals[wid] = {
                "workerId": wid,
                "workerName": entry["workerName"],
                "totalKg": 0.0,
                "totalEarnings": 0.0,
            }

        worker_totals[wid]["totalKg"] += entry.get("kg", 0)
        worker_totals[wid]["totalEarnings"] += entry.get("totalAmount", 0)

    # Round values
    for w in worker_totals.values():
        w["totalKg"] = round(w["totalKg"], 2)
        w["totalEarnings"] = round(w["totalEarnings"], 2)

    grand_kg = sum(w["totalKg"] for w in worker_totals.values())
    grand_earnings = sum(w["totalEarnings"] for w in worker_totals.values())

    return {
        "estateId": estate_id,
        "period": prefix,
        "workers": list(worker_totals.values()),
        "grandTotalKg": round(grand_kg, 2),
        "grandTotalEarnings": round(grand_earnings, 2),
    }


async def attendance_summary(estate_id: str, from_date: str, to_date: str) -> dict:
    """
    Return present / absent / half_day counts per worker
    between from_date and to_date (inclusive, format: 'YYYY-MM-DD').
    """
    db = get_firestore_client()

    docs = (
        db.collection("Attendance")
        .where("estateId", "==", estate_id)
        .where("date", ">=", from_date)
        .where("date", "<=", to_date)
        .stream()
    )

    worker_summary: dict[str, dict] = {}

    for doc in docs:
        rec = doc.to_dict()
        wid = rec["workerId"]
        if wid not in worker_summary:
            worker_summary[wid] = {
                "workerId": wid,
                "workerName": rec["workerName"],
                "present": 0,
                "absent": 0,
                "half_day": 0,
            }
        att_status = rec.get("status", "absent")
        worker_summary[wid][att_status] = worker_summary[wid].get(att_status, 0) + 1

    return {
        "estateId": estate_id,
        "fromDate": from_date,
        "toDate": to_date,
        "workers": list(worker_summary.values()),
    }
