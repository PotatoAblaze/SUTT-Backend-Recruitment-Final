from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = settings.LOGIN_URL
        self.open_urls = [self.login_url] + \
                         getattr(settings, 'OPEN_URLS', [])

    def __call__(self, request):
        print(request.path_info)
        if not request.user.is_authenticated \
        and not request.path_info in self.open_urls \
        and not request.path.startswith('/admin') \
        and not request.path.startswith('/accounts'):
            return redirect(self.login_url+'?next='+request.path)
        
        if(request.user.is_authenticated and request.user.socialaccount_set.exists()):
            if(request.path.startswith('/staff')):
                return redirect(reverse('student_dashboard'))
        if(request.user.is_authenticated and not request.user.socialaccount_set.exists()):
            if(request.path.startswith('/student')):
                return redirect(reverse('staff_dashboard'))
        
        return self.get_response(request)