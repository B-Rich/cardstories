#
# Copyright (C) 2011 Farsides <contact@farsides.com>
#
# Author: Adolfo R. Brandes <arbrandes@gmail.com>
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#
from urllib import quote, urlencode, urlopen
from urlparse import parse_qs

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse

from forms import RegistrationForm, LoginForm


def get_facebook_redirect_uri(encode=True):
    """
    Returns the urllib.quoted facebook redirection URI.

    """
    domain = Site.objects.get_current().domain
    uri = 'http://%s%s' % (domain, reverse(facebook))
    if encode:
        uri = quote(uri, '')

    return uri

def welcome(request):
    """
    Simply renders the welcome page, which includes both a registration and
    login forms.

    """
    context = {'registration_form': RegistrationForm(),
               'login_form': LoginForm(),
               'fb_redirect_uri': get_facebook_redirect_uri(),
               'fb_app_id': settings.FACEBOOK_APP_ID}
    response = render_to_response('cardstories/welcome.html', context,
                              context_instance=RequestContext(request))

    # Set welcome page URL for redirection.
    welcome_url = quote(reverse(welcome), '')
    response.set_cookie('CARDSTORIES_WELCOME', welcome_url)

    return response

def register(request):
    """
    Registers a user from supplied username and password.  If successful, logs
    the user in and redirects him to the cardstories client, with the proper
    cookie set.

    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # Store username both as username and email, since username = email
            # for now.
            u = User.objects.create_user(username, username, password)
            u.first_name = name
            u.save()
            
            # Always call authenticate() before login().
            auth_user = authenticate(username=username, password=password)
            auth_login(request, auth_user)
            response = HttpResponseRedirect(settings.CARDSTORIES_URL)

            # Note that the username should be "quoted", which is the
            # equivalent of Javascript's, encodeURIcompontent().
            response.set_cookie('CARDSTORIES_ID', quote(username))

            # Set welcome page URL for redirection, which will be needed for
            # logout, for example.
            welcome_url = quote(reverse(welcome), '')
            response.set_cookie('CARDSTORIES_WELCOME', welcome_url)

            return response
    else:
        form = RegistrationForm()

    context = {'registration_form': form,
               'login_form': LoginForm(),
               'fb_redirect_uri': get_facebook_redirect_uri(),
               'fb_app_id': settings.FACEBOOK_APP_ID}
    return render_to_response('cardstories/welcome.html', context,
                              context_instance=RequestContext(request))

def login(request):
    """
    Logs a user in using Django's contrib.auth, and sets the cookie that
    the cardstories client expects.

    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            # At this point, the user has already been authenticated by form
            # validation (which simplifies user feedback on login errors).
            auth_login(request, form.auth_user)
            response = HttpResponseRedirect(settings.CARDSTORIES_URL)

            # Note that the username should be "quoted", which is the
            # equivalent of Javascript's, encodeURIcompontent().
            response.set_cookie('CARDSTORIES_ID', quote(username))

            # Set welcome page URL for redirection, which will be needed for
            # logout, for example.
            welcome_url = quote(reverse(welcome), '')
            response.set_cookie('CARDSTORIES_WELCOME', welcome_url)

            return response
    else:
        form = LoginForm()

    context = {'registration_form': RegistrationForm(),
               'login_form': form,
               'fb_redirect_uri': get_facebook_redirect_uri(),
               'fb_app_id': settings.FACEBOOK_APP_ID}
    return render_to_response('cardstories/welcome.html', context,
                              context_instance=RequestContext(request))

def facebook(request):
    """
    Logs a user in using Facebook.  Registers the user using his/her email, so
    appropriate permissions are necessary.

    """
    if request.method == 'GET':
        if request.GET.get('error', '') == '' \
           and request.GET.get('code', '') != '':
            params = {
                'client_id': settings.FACEBOOK_APP_ID,
                'client_secret': settings.FACEBOOK_API_SECRET,
                'redirect_uri': get_facebook_redirect_uri(encode=False),
                'code': request.GET['code'],
            }

            url = 'https://graph.facebook.com/oauth/access_token?%s' % urlencode(params)
            data = urlopen(url).read()
            if 'error' not in data:
                response = parse_qs(data)
                token = response['access_token'][0]

                user = authenticate(token=token)
                if user and user.is_active:
                    auth_login(request, user)
                    response = HttpResponseRedirect(settings.CARDSTORIES_URL)

                    # Note that the username should be "quoted", which is the
                    # equivalent of Javascript's, encodeURIcompontent().
                    response.set_cookie('CARDSTORIES_ID', quote(user.username))

                    # Set welcome page URL for redirection, which will be needed for
                    # logout, for example.
                    welcome_url = quote(reverse(welcome), '')
                    response.set_cookie('CARDSTORIES_WELCOME', welcome_url)

                    return response

    context = {'registration_form': RegistrationForm(),
               'login_form': LoginForm(),
               'fb_redirect_uri': get_facebook_redirect_uri(),
               'fb_app_id': settings.FACEBOOK_APP_ID}
    return render_to_response('cardstories/welcome.html', context,
                              context_instance=RequestContext(request))

def getuserid(request, username):
    """
    Returns a user's id based on supplied username, optionally creating the
    user, if so requested.  Username will be validated according to
    registration form rules.
    
    If user is not found, a status of 404 will be returned.

    If user is not found, creation is requested, but the supplied username is
    invalid, a status of 400 will be returned.

    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        if request.GET.get('create', '') == 'yes':
            # Validates the username according to the registration form.
            name = "Cardstories Player"
            password = "mockpassword"
            data = {"name": name,
                    "username": username,
                    "password1": password,
                    "password2": password}
            form = RegistrationForm(data)
            if not form.is_valid():
                return HttpResponseBadRequest()

            # Create the user with an unusable password and generic name.  The
            # user will need to click on "forgot password" to obtain a new one.
            user = User.objects.create_user(username, username)
            user.first_name = name
            user.save()
        else:
            return HttpResponseNotFound()

    response = HttpResponse(user.id, mimetype="text/plain")
    return response

def getusername(request, userid):
    """
    Returns a user's username based on supplied id, if found. Returns 404 if
    not.

    """
    try:
        user = User.objects.get(id=userid)
        return HttpResponse(user.username, mimetype="text/plain")
    except User.DoesNotExist:
        return HttpResponseNotFound()

def getloggedinuserid(request, session_key):
    """
    Returns a user's id based on a logged in session id. If user is not found,
    a status of 404 will be returned.

    """
    try:
        session = Session.objects.get(session_key=session_key)
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)
    except (User.DoesNotExist, Session.DoesNotExist):
        return HttpResponseNotFound()

    response = HttpResponse(user.id, mimetype="text/plain")
    return response
