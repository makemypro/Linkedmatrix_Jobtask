from asyncio import proactor_events
from distutils.log import info
from ipaddress import ip_address
from time import asctime
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.models import User, Group
import logging
#logger = logging.getLogger(__name__)
# defined logger
logger = logging.getLogger('file')
# logging.basicConfig(filename = 'iptime.log', level = logging.DEBUG, filemode='w', style='%', format = '%(asctime)s: %(ip)s',)
class IPMiddleware(MiddlewareMixin): 
    def process_request(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            self.ip = x_forwarded_for.split(',')[0]
        else:
            self.ip = request.META.get('REMOTE_ADDR')

        logger.info("User time and IPAddress is "+str(self.ip) + str(time.time))
        


# class IPMiddleware(MiddlewareMixin):
#     def process_request(self,request):
#          x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#          if x_forwarded_for:
#              self.ip = x_forwarded_for.split(',')[0]
#          else:
#              self.ip = request.META.get('REMOTE_ADDR')
#          logger.warning("User time and IPAddress is "+str(self.ip) ,time.time)
      


class UserIPBlocker(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # get the client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        # key for each IP
        ip_cache_key = "blocker:ip" + ip

        query_set = Group.objects.filter(user = request.user)
        for g in query_set:
            group_name = g.name
        ip_hits_timeout = settings.IP_HITS_TIMEOUT if hasattr(settings, 'IP_HITS_TIMEOUT') else 60
        max_allowed_hits = settings.MAX_ALLOWED_HITS_PER_IP if hasattr(settings, 'MAX_ALLOWED_HITS_PER_IP') else 2
        if request.user.is_authenticated:
            if group_name == 'Gold':
                max_allowed_hits = 10
            elif group_name == 'Silver':
                max_allowed_hits = 5
            elif group_name == 'Bronze':
                max_allowed_hits = 2
        else:
            max_allowed_hits = 1
                

        # get the hits by this IP in last IP_TIMEOUT time
        this_ip_hits = cache.get(ip_cache_key)

        if not this_ip_hits:
            this_ip_hits = 1
            cache.set(ip_cache_key, this_ip_hits, ip_hits_timeout)
        else:
            this_ip_hits += 1
            cache.set(ip_cache_key, this_ip_hits)

        # print(this_ip_hits, ip, ip_hits_timeout, max_allowed_hits)
        if this_ip_hits > max_allowed_hits:
            return HttpResponseForbidden()

        else:
            response = self.get_response(request)          
            return response

def ReturnObject():

    return 'OK' 