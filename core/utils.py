#!/usr/bin/env python

"""Utility module to hold useful methods for the core application."""

import datetime
import re
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from core.models import UserProfile
#from socialregistration.models import FacebookProfile
from django_facebook.models import FacebookProfileModel
from django_facebook.api import *
from knightbookmarket import settings


def load_page(request, template, extra={}):
    """Special page rendering function for bookstore application pages.

    Args::
    request: the original page request passed to the view
    template: the filename of the template to load
    extra: a dictionary holding extra information to inject into the
        template's context in addition to the user's model and
        role (default empty dictionary)

    """
    try:
        facebook = FacebookProfile.objects.get(user=request.user)
    except:
        facebook = None
    return render_to_response(
        '%s' % template,
        dict({
            'facebook': facebook
        }.items() + extra.items()),
        context_instance=RequestContext(request))


def message_page(request, message, back=""):
    """Shortcut function to return a simple message page."""
    extra = {'message': message, 'back': back}
    return load_page(request, 'message.html', extra)


def error_page(request, error):
    """Shortcut function to return a error message page."""
    extra = {'error': error}
    return load_page(request, 'error.html', extra)


def get_remote_ip(request):
    try:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    except:
        ip = request.META['REMOTE_ADDR']
    return ip[ip.find(" ")+1:]


def generate_new_key(user):
    """Generates and returns a new activation key for a user."""

    # Build the activation key for their account
    salt = md5(str(random.random())).hexdigest()[:5]
    activation_key = md5(salt+user.username).hexdigest()
    key_expires = datetime.datetime.today() + datetime.timedelta(2)

    # Create and save their profile
    profile = get_object_or_404(UserProfile, user=user)
    profile.activation_key = activation_key
    profile.key_expires = key_expires
    profile.save()

    return activation_key



def share(request, message, link, name, picture):
    facebook_graph = get_facebook_graph(request)
    if facebook_graph:
        try:
            facebook_graph.set('me/feed', message=message, name=name, 
                               link=link, picture=picture)
        except:
            pass


def share_sale(request, sale):
    title = title_case(sale.title.encode('utf8'))
    condition = sale.condition.lower()
    price = sale.price
    course = title_case(sale.course)
    message = "I'm selling %s %s at the Knight Book Market for $%.2f! It's for %s." % (
        title, condition, price, course
    )
    link = "http://%s/browse/%d/" % (Site.objects.get_current().domain, sale.id)
    picture = "http://%s%s" % (Site.objects.get_current().domain,
                               sale.image.url)
    share(request, message, link, title, picture)


pattern = re.compile(r'[a-zA-Z]')
def title_case(s):
    s = unicode(s).encode('utf8')
    exceptions = ['a', 'an', 'of', 'the', 'is', 'CP', 'AP', '(H)']
    word_list = s.split(' ')
    start = re.search(pattern, s).start()  if re.search(pattern, s) else 0
    title = [word_list[0][0:start] + word_list[0][start:].capitalize()]
    for word in word_list[1:]:
        title.append(word in exceptions and word or word.capitalize())
    return ' '.join(title)


def currency(value):
    # Original filter code found at  http://djangosnippets.org/snippets/2365/
    symbol = '$'
    thousand_sep = ''
    decimal_sep = ''
    # try to use settings if set
    try:
        symbol = settings.CURRENCY_SYMBOL
    except AttributeError:
        pass

    try:
        thousand_sep = settings.THOUSAND_SEPARATOR
        decimal_sep = settings.DECIMAL_SEPARATOR
    except AttributeError:
        thousand_sep = ','
        decimal_sep = '.'

    intstr = str(int(value))
    f = lambda x, n, acc=[]: f(x[:-n], n, [(x[-n:])]+acc) if x else acc
    intpart = thousand_sep.join(f(intstr, 3))
    return "%s%s%s%s" % (symbol, intpart, decimal_sep, ("%0.2f" % value)[-2:])
