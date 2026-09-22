from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import User


def role_required(*roles):
    """Require login AND one of the given portal roles.

    Roles are members of ``User.Roles`` (e.g. ``User.Roles.STUDENT``).
    Failing the check redirects to the login page.
    """

    def decorator(view_func):
        @login_required(login_url='login_p')
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.role and request.user.role in roles:
                return view_func(request, *args, **kwargs)
            from django.contrib import messages
            messages.error(request, "You do not have access to that portal.")
            return redirect('login_p')
        return _wrapped

    return decorator


def approved_teacher_required(view_func):
    """Role-gated teacher portal that also requires an approved profile."""
    from faculty.models import faculty_profile

    @role_required(User.Roles.TEACHER)
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile = faculty_profile.objects.filter(user=request.user).first()
        if profile is not None and profile.is_approved:
            return view_func(request, *args, **kwargs)
        return redirect('pend_page')
    return _wrapped