"""Marks to letter-grade conversion shared by grade entry UIs."""


def grade_for_marks(marks):
    """Return an S..F letter grade for a 0-100 marks value."""
    if marks >= 90:
        return "S"
    if marks >= 80:
        return "A+"
    if marks >= 75:
        return "A"
    if marks >= 70:
        return "B+"
    if marks >= 65:
        return "B"
    if marks >= 60:
        return "C"
    if marks >= 50:
        return "D"
    return "F"