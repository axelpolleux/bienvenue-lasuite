from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse


def home(request):
    if request.user.is_authenticated:
        return HttpResponse(f"Logged in as {request.user.email}")
    return HttpResponse("Logged out.")


@login_required
def whoami(request):
    return JsonResponse(
        {
            "email": request.user.email,
            "username": request.user.username,
        }
    )
