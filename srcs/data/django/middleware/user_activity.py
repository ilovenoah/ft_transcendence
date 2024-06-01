from django.utils import timezone
from datetime import timedelta

class UpdateUserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            now = timezone.now()
            # ユーザーの最後のアクティビティ時刻をチェック
            if request.user.last_active and (now - request.user.last_active > timedelta(minutes=5)):
                request.user.is_online = False
            else:
                request.user.is_online = True
            
            # 最後のアクティブ時刻を更新
            request.user.last_active = now
            request.user.save(update_fields=['last_active', 'is_online'])

        return response

