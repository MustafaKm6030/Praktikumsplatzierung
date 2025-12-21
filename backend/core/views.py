from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import ensure_csrf_cookie


@require_GET
@ensure_csrf_cookie
def csrf_token_view(request):
    """Endpoint to provide a CSRF cookie and token for SPA clients."""
    return JsonResponse({"csrfToken": get_token(request)})

