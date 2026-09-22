"""Shared analytics + intelligence helpers used by student and faculty portals.

Single source of truth for CGPA/GPA math, grade distributions, attendance
metrics, at-risk detection, and performance rankings.
"""
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from academics.models import Attendance, AttendanceSession, Grade

GRADE_POINTS = {
    "S": 10.0,
    "A+": 9.0,
    "A": 8.0,
    "B+": 7.0,
    "B": 6.0,
    "C": 5.0,
    "D": 4.0,
    "F": 0.0,
}

GRADE_ORDER = ("S", "A+", "A", "B+", "B", "C", "D", "F")
AT_RISK_THRESHOLD_PERCENT = 75.0


def grade_points(grade):
    """Numeric grade points for a letter grade (10..0)."""
    return GRADE_POINTS.get(grade, 0.0)


def gpa_of_points(points):
    """Unweighted GPA (0-10) for a list of grade points, or None."""
    if not points:
        return None
    return round(sum(points) / len(points), 2)


def gpa_by_sem(profile):
    """List of {sem, gpa} for a student's graded semesters."""
    rows = {}
    for g in Grade.objects.filter(student=profile).select_related("subject"):
        rows.setdefault(g.sem, []).append(grade_points(g.grade))
    return [{"sem": sem, "gpa": gpa_of_points(rows[sem])} for sem in sorted(rows)]


def overall_cgpa(profile):
    """Credit-weighted CGPA across all graded semesters, or None."""
    grades = list(Grade.objects.filter(student=profile).select_related("subject"))
    if not grades:
        return None
    weighted = sum(grade_points(g.grade) * (g.subject.credits or 1) for g in grades)
    credits = sum(g.subject.credits or 1 for g in grades)
    return round(weighted / credits, 2) if credits else None


def attendance_by_subject(profile):
    """Per-subject {subject, code, present, total, percent, at_risk} for a student."""
    totals = {}
    for row in AttendanceSession.objects.values(
        "subject", "subject__name", "subject__code"
    ).annotate(total=Count("id")):
        totals[row["subject"]] = row

    present = {}
    for row in Attendance.objects.filter(student=profile).values(
        "session__subject"
    ).annotate(present=Count("id")):
        present[row["session__subject"]] = row["present"]

    out = []
    for sid, meta in totals.items():
        total = meta["total"]
        p = present.get(sid, 0)
        percent = round(p / total * 100, 1) if total else 0.0
        out.append({
            "subject": meta["subject__name"],
            "code": meta["subject__code"],
            "present": p,
            "total": total,
            "percent": percent,
            "at_risk": percent < AT_RISK_THRESHOLD_PERCENT,
        })
    out.sort(key=lambda r: r["percent"])
    return out


def attendance_overall(profile):
    """Overall attendance percent across all subjects, or None."""
    rows = attendance_by_subject(profile)
    total = sum(r["total"] for r in rows)
    present = sum(r["present"] for r in rows)
    if not total:
        return None
    return round(present / total * 100, 1)


def attendance_trend(teacher, days=14):
    """Daily present-count series for the last `days` days for a teacher."""
    start = timezone.localdate() - timedelta(days=days - 1)
    rows = (
        Attendance.objects
        .filter(session__teacher=teacher, marked_at__date__gte=start)
        .annotate(day=TruncDate("marked_at"))
        .values("day")
        .annotate(present=Count("id"))
        .order_by("day")
    )
    by_day = {r["day"]: r["present"] for r in rows}
    out = []
    for i in range(days):
        d = start + timedelta(days=i)
        out.append({"day": d.isoformat(), "present": by_day.get(d, 0)})
    return out


def at_risk_students(teacher):
    """student_profiles below the attendance threshold in a teacher's sessions."""
    from students.models import student_profile

    ids = set()
    subs = (
        AttendanceSession.objects.filter(teacher=teacher)
        .values("subject_id")
        .annotate(sessions=Count("id"))
    )
    for row in subs:
        subject_id = row["subject_id"]
        total_sessions = row["sessions"]
        presents = (
            Attendance.objects
            .filter(session__teacher=teacher, session__subject_id=subject_id)
            .values("student_id")
            .annotate(present=Count("id"))
        )
        for p in presents:
            if p["present"] * 100 < AT_RISK_THRESHOLD_PERCENT * max(total_sessions, 1):
                ids.add(p["student_id"])
    return list(student_profile.objects.filter(pk__in=ids)[:50])


def grade_distribution(subject, sem):
    """List of {grade, count} for a subject/semester in canonical grade order."""
    counts = {}
    for g in Grade.objects.filter(subject=subject, sem=sem):
        counts[g.grade] = counts.get(g.grade, 0) + 1
    return [
        {"grade": grade, "count": counts[grade]}
        for grade in GRADE_ORDER
        if counts.get(grade)
    ]


def rank_students(sem=None, department=None, limit=None):
    """Students ranked by CGPA (1 = highest). Optionally scoped by sem/department."""
    from students.models import student_profile

    qs = student_profile.objects.all()
    if sem is not None:
        qs = qs.filter(sem=sem)
    if department:
        qs = qs.filter(department__iexact=department)

    rows = []
    for s in qs:
        cgpa = overall_cgpa(s)
        rows.append({"student": s, "cgpa": cgpa})

    ranked = [r for r in rows if r["cgpa"] is not None]
    ranked.sort(key=lambda r: r["cgpa"], reverse=True)
    out = []
    for i, r in enumerate(ranked, start=1):
        out.append({"rank": i, "student": r["student"], "cgpa": r["cgpa"]})
    for r in rows:
        if r["cgpa"] is None:
            out.append({"rank": None, "student": r["student"], "cgpa": None})

    return out[:limit] if limit else out
