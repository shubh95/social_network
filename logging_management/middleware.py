# middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import Log
import json

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # return if the request is for logging itself
        if request.path == '/logs/create/' or request.path == '/logs/':
            request.log_obj = None
            return
        
        self.start_time = timezone.now()

        jwt_authentication = JWTAuthentication()
        try:
            auth_result = jwt_authentication.authenticate(request)

            if auth_result is not None:
                user = auth_result[0]
            else:
                user = None
        except AuthenticationFailed as e:
            user = None

        log_obj = Log.objects.create(
            user=user,
            action=request.path,
            method=request.method,
            ip_address=request.META.get('REMOTE_ADDR'),
            action_started_at=self.start_time,
            payload=json.dumps(request.body.decode('utf-8')),
        )

        request.log_obj = log_obj
    
    def process_response(self, request, response):
        log_obj = request.log_obj
        if log_obj:
            log_obj.action_completed_at = timezone.now()
            log_obj.result = response.content
            log_obj.status_code = response.status_code
            log_obj.save()

        return response