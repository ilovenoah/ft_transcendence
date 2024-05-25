from django.utils import timezone
from datetime import timedelta

class UpdateUserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            now = timezone.now()
            if not request.user.last_active or (now - request.user.last_active > timedelta(minutes=1)): #最後にアクセスしてから1分以上経過している
                request.user.last_active = now
                request.user.is_online = True
                request.user.save(update_fields=['last_active', 'is_online'])
        return response
