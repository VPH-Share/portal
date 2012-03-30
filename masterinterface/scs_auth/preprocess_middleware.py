from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import logout , login
from tktauth import validateTicket, createTicket
from datetime import datetime
import binascii

class MultiHostMiddleware:

    def process_view(self, request, callback, callback_args, callback_kwargs):

        request.META['NEW_VPH_TKT_COOKIE']=False

        try:
            host = request.META["HTTP_HOST"]
            if  request.COOKIES.get('vph-tkt'):

                ticket=binascii.a2b_base64(request.COOKIES['vph-tkt'])

                if validateTicket(settings.SECRET_KEY,ticket) is None:
                    logout(request)
                request.META['VPH_TKT_COOKIE'] = ticket
            else:
                logout(request)

            if request.GET.get('ticket'):
                ticket = binascii.a2b_base64(request.GET['ticket'])
                data = validateTicket(settings.SECRET_KEY,ticket)
                if  data is not None :
                    new_user = RemoteUserBackend()
                    user = new_user.authenticate(data[1])
                    user.backend ='django.contrib.auth.backends.RemoteUserBackend'
#                    user.first_name = service_response['fullname'].split(" ")[0]
#                    user.last_name = service_response['fullname'].split(" ")[1]
#                    user.email = service_response['email']
                    user.last_login = str(datetime.now())
                    user.save()
                    login(request,user)
                    request.META['NEW_VPH_TKT_COOKIE'] = True



        except KeyError:
            pass # use default urlconf (settings.ROOT_URLCONF)

    def process_response(self, request, response):

        if request.META.get('NEW_VPH_TKT_COOKIE'):

            new_tkt = createTicket(
                settings.SECRET_KEY,
                request.user.username
            )

            tkt64 = binascii.b2a_base64(new_tkt).rstrip()

            response.set_cookie( 'vph-tkt', tkt64 )



        if request.META.get("VPH_TKT_COOKIE") is None:
            return response

        ticket=binascii.a2b_base64(request.COOKIES['vph-tkt'])
        data = validateTicket(settings.SECRET_KEY,ticket)
        if data is not None:
            (digest, userid, tokens, user_data, timestamp) = data
            tkt64 =binascii.b2a_base64(createTicket(settings.SECRET_KEY, userid, tokens, user_data))
            response.set_cookie( 'vph-tkt', tkt64 )

            return response

        return response

