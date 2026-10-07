from django.shortcuts import render


def dashboard(request):
    """Public Udaan dashboard.

    Authentication is handled inside modules that require it,
    such as Education.
    """
    return render(
        request,
        "dashboard/dashboard.html"
    )
