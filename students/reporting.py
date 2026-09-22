"""Student-side reporting helpers: GPA/CGPA, attendance, earned badges."""
from django.db.models import Count

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


def _points(grade):
    return GRADE_POINTS.get(grade, 0.0)


def gpa_by_sem(profile):
    """List of {sem, gpa} ordered by semester."""
    rows = {}
    for g in Grade.objects.filter(student=profile).select_related("subject"):
        rows.setdefault(g.sem, []).append(_points(g.grade))

    out = []
    for sem in sorted(rows):
        pts = rows[sem]
        out.append({"sem": sem, "gpa": round(sum(pts) / len(pts), 2)})
    return out


def overall_cgpa(profile):
    """Credit-weighted CGPA across all graded semesters."""
    grades = list(Grade.objects.filter(student=profile).select_related("subject"))
    if not grades:
        return None
    weighted = 0.0
    credits = 0
    for g in grades:
        c = g.subject.credits or 1
        weighted += _points(g.grade) * c
        credits += c
    return round(weighted / credits, 2)


def attendance_by_subject(profile):
    """List of {subject, code, present, total, percent, at_risk} per subject."""
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
            "at_risk": percent < 75,
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


def earned_badges(profile):
    """Badges earned so far, with tier used for styling."""
    badges = []
    cgpa = overall_cgpa(profile)
    if cgpa is not None:
        if cgpa >= 9.0:
            badges.append({"id": "deans", "name": "Dean's List", "desc": "CGPA 9.0 and above", "tier": "gold"})
        if cgpa >= 8.0:
            badges.append({"id": "distinction", "name": "Distinction", "desc": "CGPA 8.0 and above", "tier": "silver"})
        if cgpa >= 7.0:
            badges.append({"id": "merit", "name": "Academic Merit", "desc": "CGPA 7.0 and above", "tier": "bronze"})

    att = attendance_overall(profile)
    if att is not None:
        if att >= 90:
            badges.append({"id": "attend-pro", "name": "Attendance Pro", "desc": "90%+ overall attendance", "tier": "green"})
        if att >= 75:
            badges.append({"id": "punctual", "name": "Punctual Scholar", "desc": "75%+ overall attendance", "tier": "blue"})
    return badges