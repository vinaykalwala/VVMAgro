import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('app_logger')

class ActionLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._log_data = {
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
            'ip': self.get_client_ip(request),
            'method': request.method,
            'path': request.path,
            'get_data': dict(request.GET),
            'post_data': dict(request.POST) if request.method in ['POST', 'PUT'] else None,
        }

    def process_response(self, request, response):
        log_data = getattr(request, '_log_data', {})
        log_data['status_code'] = response.status_code

        logger.info(
            f"User: {log_data.get('user')} | "
            f"IP: {log_data.get('ip')} | "
            f"Method: {log_data.get('method')} | "
            f"Path: {log_data.get('path')} | "
            f"GET: {log_data.get('get_data')} | "
            f"POST: {log_data.get('post_data')} | "
            f"Status: {log_data.get('status_code')}"
        )
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
