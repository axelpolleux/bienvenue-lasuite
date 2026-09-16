from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
def whoami(request):
    return JsonResponse(
        {
            "email": request.user.email,
            "username": request.user.username,
        }
    )
