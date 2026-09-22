"""Student-side reporting helpers, delegating to the shared analytics layer."""
from academics.analytics import (
    grade_points,
    gpa_by_sem,
    overall_cgpa,
    attendance_by_subject,
    attendance_overall,
)

_points = grade_points


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
