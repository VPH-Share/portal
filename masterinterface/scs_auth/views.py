"""
Scs_auth views contain all frontend views about authentication process.
"""
import urllib2
import os
from M2Crypto import DSA

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.utils.datastructures import SortedDict
from django.core.validators import URLValidator
from django.core.exceptions import ObjectDoesNotExist
from masterinterface.scs_auth import __version__ as version
from piston.handler import BaseHandler
from permissions.utils import add_role, remove_role

from auth import authenticate
from masterinterface.scs.utils import is_staff
from masterinterface.scs_auth.auth import calculate_sign
from masterinterface.cyfronet import easywebdav
from models import *


@csrf_exempt
def done(request):
    """ login complete view """
    ctx = {
        'version': version,
        'last_login': request.session.get('social_auth_last_login_backend')
    }

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    agreement, created = UserAgreement.objects.get_or_create(user=request.user, cookies=True, privacy=True)
    if created:
        agreement.ip = ip
    agreement.save()
    if request.user.first_name:
        request.session['welcome'] = "Dear %s, your login attempt has been successful! Welcome to the Master Interface!" % request.user.first_name
    else:
        request.session['welcome'] = "Dear friend, your login attempt has been successful! Welcome to the Master Interface!"

    #Create home folder for the user
    webdav = easywebdav.connect(settings.LOBCDER_HOST, username='user',
                                password=request.ticket, protocol='https'
                                )
    foldertocreate = settings.LOBCDER_ROOT + "/home/%s" % request.user.username
    try:
        #if the fodler doesn't exisit , it is created.
        if not webdav.exists(foldertocreate):
            webdav.mkdir(foldertocreate)
    except Exception as e:
            # This is done to skip an erratic behaviour of the webdav, that is triggering an exception
            # even after the directory is successfully created
            try:
                if webdav.exists(foldertocreate) == False:
                    pass
            except Exception as e:
                pass
    response = render_to_response(
        'scs_auth/done.html',
        ctx,
        RequestContext(request)
    )

    return response

@login_required
def set_privacy(request):

    if request.user.userprofile.privacy:
        request.user.userprofile.privacy = False
    else:
        request.user.userprofile.privacy = True
    request.user.userprofile.save()

    response = HttpResponse(status=200)
    response._is_string = True
    return response

@csrf_exempt
@login_required
def refreshtkt(request):

    if request.method == 'POST' and request.user.is_authenticated():
        try:
            newtkt = request.user.userprofile.get_ticket(int(request.POST.get('expire')))
            response = HttpResponse(status=200, content=newtkt)
        except Exception, e:
            response = HttpResponse(status=400)
    else:
        response = HttpResponse(status=403)
    response._is_string = True
    return response

@csrf_exempt
@login_required
def changeuser(request):
    """
    tool avalable only for admin
    """
    if request.method == 'POST' and request.user.is_superuser:
        try:
            newtkt = User.objects.get(username=request.POST.get('username')).userprofile.get_ticket()
            response = HttpResponse(status=200, content=newtkt)
        except Exception, e:
            response = HttpResponse(status=400)
    else:
        response = HttpResponse(status=403)
    response._is_string = True
    return response


@csrf_exempt
def bt_agreement_check(request):

    if request.method == 'POST' and request.POST.get('username'):
        try:
            user = User.objects.get(username=request.POST.get('username'))
            agreement = UserAgreement.objects.get(user=user)
            if not agreement.privacy:
                raise ObjectDoesNotExist
            response = HttpResponse('TRUE')
        except ObjectDoesNotExist:
            response = HttpResponse('FALSE')
    else:
        response = HttpResponse(status=403)

    response._is_string = True
    return response


def bt_loginform(request):
    """ return the biomedtown login form """
    if request.method == 'POST' and request.POST.get('username'):
        name = settings('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')
        request.session['saved_username'] = request.POST['username']
        backend = request.session[name]['backend']

        return redirect('socialauth_complete', backend=backend)
    context = {'version': version}

    if request.GET.get('error'):
        context['info'] = 'Login Error'
    return render_to_response(
        'scs_auth/bt_loginform.html',
        context,
        RequestContext(request)
    )


def bt_login(request):
    """ return the biomedtown login page with and embedded login iframe"""

    return render_to_response(
        'scs_auth/bt_login.html',
        {'version': version},
        RequestContext(request)
    )


def auth_loginform(request):
    """
    Process login request.
    Create session and user into database if not exist.
    """

    response = {'version': version}

    try:
        if request.method == 'POST' and request.POST.get('biomedtown_username') and request.POST.get('biomedtown_password'):
            username = request.POST['biomedtown_username']
            password = request.POST['biomedtown_password']

            user, tkt64 = authenticate(username=username, password=password)

            if user is not None:

                response['ticket'] = tkt64
                response['last_login'] = 'biomedtown'

                login(request, user)

                webdav = easywebdav.connect(settings.LOBCDER_HOST, username='user', password=response['ticket'], protocol='https')
                foldertocreate = settings.LOBCDER_ROOT + "/home/%s" % request.user.username
                try:
                    if not webdav.exists(foldertocreate):
                       webdav.mkdir(foldertocreate)
                except Exception as e:
                    try:
                        if webdav.exists(foldertocreate) == False:
                            pass
                    except Exception as e:
                        pass

                response = render_to_response(
                    'scs_auth/done.html',
                    response,
                    RequestContext(request))

                response.set_cookie('vph-tkt', tkt64, domain='.vph-share.eu')

                return response

            else:
                response['info'] = "Username or password not valid."

        elif request.method == 'POST':
            response['info'] = "Login error"
        elif request.method == 'GET':
            if request.user.is_authenticated():
                response['info'] = "username %s is authenticated" % (request.user.username,)
            else:
                response['info'] = "username is not authenticated"
    except Exception, e:
        response['info'] = "Login error with exceptioni %s" % (str(e),)

    return render_to_response(
        'scs_auth/auth_loginform.html',
        response,
        RequestContext(request)
    )


def auth_done(request, token):
    """ login complete view """
    ctx = {
        'version': version,
        'last_login': "biomedtown"
    }

    response = render_to_response(
        'scs_auth/done.html',
        ctx,
        RequestContext(request)
    )

    return response


def auth_login(request):
    """ return the biomedtown mod_auth tkt login page"""

    return render_to_response('scs_auth/auth_login.html',
                              {'version': version},
                              RequestContext(request)
    )


def logout(request):
    """Logs out user"""
    if request.META.get('HTTP_REFERER'):
        if request.META['HTTP_REFERER'].count('logout') and request.user.is_authenticated():
            return HttpResponseRedirect('http://' + request.META['HTTP_HOST'] + '/')

    auth_logout(request)
    #response = HttpResponseRedirect('http://'+request.META['HTTP_HOST']+'/?loggedout')
    response = render_to_response(
        'scs_auth/logout.html',
        None,
        RequestContext(request)
    )
    response.delete_cookie('vph_cookie')
    return response


class validate_tkt(BaseHandler):
    """
        REST service based on Django-Piston Library.\n
        Now Service support:\n
        # application/json -> http://HOSTvalidatetkt.json?ticket=<ticket>\n
        # text/xml -> http://HOST/validatetkt.xml?ticket=<ticket>\n
        # application/x-yaml -> http://HOST/validatetkt.yaml?ticket=<ticket>\n

        Method validate given ticket, if it valid return User info else 403 error return
    """

    def read(self, request, ticket=''):

        """
            Process a Validate ticket request.
            Arguments:

            request (HTTP request istance): HTTP request send from client.
            ticket (string) : base 64 ticket.

            Return:

            Successes - Json/xml/yaml format response (response format depend on request content/type)
            Failure - 403 error

        """
        try:
            if request.GET.get('ticket'):
                client_address = request.META['REMOTE_ADDR']
                user, tkt64 = authenticate(ticket=request.GET['ticket'], cip=client_address)

                if user is not None:
                    theurl = settings.ATOS_SERVICE_URL
                    username = user.username
                    password = request.GET['ticket']

                    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                    passman.add_password(None, theurl, username, password)
                    authhandler = urllib2.HTTPBasicAuthHandler(passman)

                    opener = urllib2.build_opener(authhandler)

                    urllib2.install_opener(opener)
                    #pagehandle = urllib2.urlopen(theurl)

                    #if pagehandle.code == 200 :
                    return user.userprofile.to_dict()

            response = HttpResponse(status=403)
            response._is_string = True
            return response
        except Exception, e:
            response = HttpResponse(status=403)
            response._is_string = True
            return response


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


@is_staff()
def users_access_search(request):
    Response = {}

    try:
        if request.method == "POST":

            import urllib2

            if not validateEmail(str(request.POST['email'])):
                return HttpResponse('FALSE')

            usermail = str(request.POST['email'])
            f = urllib2.urlopen('https://biomedtown.vph-share.eu/getMemberByEmail?email=' + usermail)
            username = f.read()

            if username != '':
                Roles = Role.objects.all()
                try:
                    usersRole, created = User.objects.get_or_create(username=username, email=usermail)
                except:
                    usersRole = {}
                    pass

                resultUsers = {}

                if not isinstance(usersRole, dict):
                    if getattr(resultUsers, usersRole.username, None) is None:
                        resultUsers[usersRole.username] = {}
                        resultUsers[usersRole.username]['email'] = usersRole.email
                    resultUsers[usersRole.username]['roles'] = []
                    for role in get_roles(usersRole):
                        resultUsers[usersRole.username]['roles'].append(role.name)

                #If user is not present into local db
                if username not in resultUsers:
                    resultUsers[username] = {}
                    resultUsers[username]['email'] = usermail
                    resultUsers[username]['roles'] = []
                Response = {'Roles': Roles.values(), 'resultUsers': resultUsers}

                return render_to_response("scs_auth/user_role_search.html",
                                          Response,
                                          RequestContext(request))

            return HttpResponse('FALSE')

    except Exception, e:
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        return HttpResponse('FALSE')


@is_staff()
def users_create_role(request):
    try:
        if request.method == "POST":
            if request.POST['role_name'].lower() == "":
                return HttpResponse("FALSE")
            newRole, created = Role.objects.get_or_create(name=request.POST['role_name'])
            if created:
                newRole.save()
            else:
                return HttpResponse("FALSE")
            return HttpResponse('<li id="' + request.POST['role_name'].lower() + '">' + request.POST[
                'role_name'].lower() + ' <input  name="' + request.POST[
                                    'role_name'] + '" type="checkbox" ></li>')

    except  Exception, e:
        return HttpResponse("FALSE")
    return HttpResponse("FALSE")


@is_staff()
def users_remove_role(request):
    try:
        if request.method == "POST" and request.user.is_superuser:
            newRole = Role.objects.get(name=request.POST['role_name'].lower())
            newRole.delete()
            return HttpResponse(request.POST['role_name'].lower())

    except  Exception, e:
        return HttpResponse("FALSE")
    return HttpResponse("FALSE")


@is_staff()
def users_update_role_map(request):
    try:
        if request.method == "POST":
            for key, value in request.POST.iteritems():
                if len(key.split('!')) == 3:
                    userinfo = key.split('!')
                    role = Role.objects.get(name=userinfo[0])
                    if not isinstance(role, Role):
                        return HttpResponse('FALSE')
                    user, created = User.objects.get_or_create(username=userinfo[1], email=userinfo[2])
                    if value == 'on':
                        add_role(user, role)
                    else:
                        remove_role(user, role)

            return HttpResponse('TRUE')
    except Exception, e:
        from raven.contrib.django.raven_compat.models import client
        client.captureException()
        return HttpResponse("FALSE")

    Roles = Role.objects.all()
    usersRole = User.objects.order_by('username').all()

    resultUsers = SortedDict()
    for i in range(0, len(usersRole.values())):

        if getattr(resultUsers, usersRole[i].username, None) is None:
            resultUsers[usersRole[i].username] = {}
            resultUsers[usersRole[i].username]['email'] = usersRole[i].email
        resultUsers[usersRole[i].username]['roles'] = []
        for role in get_roles(usersRole[i]):
            resultUsers[usersRole[i].username]['roles'].append(role.name)

    return render_to_response("scs_auth/users_role_map.html",
                              {
                                  'Roles': Roles.values(),
                                  'resultUsers': resultUsers,
                                  'request': request
                              },
                              RequestContext(request))


@is_staff()
def set_security_agent(request):
    serviceDIGEST = "user_id=%s&granted_roles=%s&timestamp=%s"
    serviceACTION = "%s/setgrantedroles?%s&sign=%s"
    Roles = ()
    serviceURL = ""
    try:
        if request.method == "POST":
            for key, value in request.POST.iteritems():
                if key == "serviceURL":
                    serviceURL = value
                elif key == "csrfmiddlewaretoken":
                    continue
                else:
                    role = Role.objects.get(name=key)
                    if not isinstance(role, roles):
                        return HttpResponse('FALSE')
                    Roles = Roles + ( key, )

            validator = URLValidator()
            try:
                validator(serviceURL)
            except Exception, e:
                return HttpResponse("Service URL is not well formed")
            granted_roles = ""
            for value in Roles:
                granted_roles += str(value) + ","
            granted_roles = granted_roles[:-1]

            serviceDIGEST = serviceDIGEST % (request.user.username, granted_roles, str(int(time.time())))
            key = DSA.load_key(settings.MOD_AUTH_PRIVTICKET)
            serviceSIGN = calculate_sign(key, serviceDIGEST)

            requestURL = serviceACTION % (serviceURL, serviceDIGEST, serviceSIGN)
            username = "test"
            password = "test"

            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, requestURL, username, password)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)

            opener = urllib2.build_opener(authhandler)

            urllib2.install_opener(opener)

            try:
                pagehandle = urllib2.urlopen(requestURL)
            except:
                pagehandle = urllib2.urlopen(requestURL)
            if pagehandle.code != 200:
                return HttpResponse(' Sec/Agent request refused.')

            return HttpResponse('TRUE')
    except Exception, e:
        return HttpResponse("FALSE")
