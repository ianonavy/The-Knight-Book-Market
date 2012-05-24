#!/usr/bin/env python

"""Django URLs configuration module for the bookstore application."""

from django.conf.urls.defaults import patterns
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import password_reset, password_reset_done, \
    password_reset_confirm, password_reset_complete, password_change, \
    password_change_done
from django.views.generic.simple import direct_to_template
from bookmarket.forms import CustomSetPasswordForm

__author__ = "Ian Adam Naval"
__copyright__ = "Copyright 2011 Ian Adam Naval"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ian Adam Naval"
__email__ = "ianonavy@gmail.com"
__status__ = "Development"
__date__ = "13 August 2011"


urlpatterns = patterns('bookmarket.views',
    (r'^$', 'index'),

    (r'^login/(?P<activation_key>.*)$', 'login_view'),
    (r'^logout/$', 'logout_view'),

    (r'^account/reset/$', password_reset),
    (r'^account/reset/done/$', password_reset_done),
    (r'^account/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm, {'set_password_form': CustomSetPasswordForm}),
    (r'^account/reset/complete/$', password_reset_complete),

    (r'^account/$', 'account'),
    (r'^account/disable/', 'account_disable'),
    (r'^account/change_password/$', password_change),
    (r'^account/change_password/done/$', password_change_done),

    (r'^signup/$', 'signup'),
    (r'^signup/facebook/$', direct_to_template, {'template':
        'bookmarket/signup_facebook.html'}),
    (r'^terms/$', direct_to_template, {'template': 'bookmarket/terms.html'}),
    (r'^signup/resend_key/(?P<username>.*)$', 'resend_key'),
    (r'^signup/confirmed/$', 'signup_confirmed'),

    (r'^about/$', direct_to_template, {'template': 'bookmarket/about.html'}),
    (r'^donate/$', direct_to_template, {'template': 'bookmarket/donate.html'}),
    (r'^contact/$', 'contact'),
    (r'^report/$', 'report'),
    (r'^report/(?P<id>\d+)/$', 'report'),

    (r'^browse/$', 'browse'),
    (r'^browse/(?P<id>\d+)/$', 'browse'),
    (r'^buy/$', direct_to_template, {'template': 'bookmarket/buy.html'}),
    
    (r'^sale/new/$', 'new_sale'),
    (r'^sale/cancel/(?P<id>\d+)/$', 'cancel_sale'),
    (r'^sale/remove/(?P<id>\d+)/$', 'remove_sale'),
    
    (r'^offer/new/(?P<id>\d+)/$', 'new_offer'),
    (r'^offer/accept/(?P<id>\d+)/$', 'accept_offer'),
    (r'^offer/cancel/(?P<id>\d+)/$', 'cancel_offer')
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)