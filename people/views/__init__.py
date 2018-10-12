from people.views.handle import (register,login,logout,
                                 user,au_top,user_topics,user_comments,
                                 send_verified_email,email_verified,
                                 first_reset_password,find_password,reset_password,
                                 )
from people.views.setting import (profile,password,upload_headimage,delete_headimage)
from people.views.follow import follow,following,un_follow

class MyMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
    def process_request(self,request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        if request.user.is_authenticated:
            request.user.last_ip = ip
            request.user.save()
        return None
    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response