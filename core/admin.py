#!/usr/bin/env python

"""Django admin configuration form.

Contains classes to configure how the models are displayed and edited in the
Django administration side.

"""

from django.contrib import admin
from core.models import UserProfile, Course, Sale, Offer


__author__ = "Ian Adam Naval"
__copyright__ = "Copyright 2011 Ian Adam Naval"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ian Adam Naval"
__email__ = "ianonavy@gmail.com"
__status__ = "Development"
__date__ = "13 August 2011"


class CourseAdmin(admin.ModelAdmin):
    """Admin form configuration for the Course model."""

    fieldsets = [
        ('Course', {'fields': [
            'number',
            'name',
        ]})
    ]
    list_display = ('number', 'name')


class SaleAdmin(admin.ModelAdmin):
    """Admin form configuration for the Sale model."""

    fieldsets = [
        ('Sale', {'fields': [
            'status',
            'merchant',
            'course',
            'matches_official',
            'condition',
            'title',
            'image',
            'price',
            'expires',
            'notes',
            'isbn'
        ]})
    ]
    list_display = ('id', 'title', 'course', 'merchant', 'status', 'price', 'expires')


class OfferAdmin(admin.ModelAdmin):
    """Admin form configuration for the Offer model."""

    fieldsets = [
        ('Book', {'fields': [
            'status',
            'sale',
            'buyer',
            'price'
        ]})
    ]
    list_display = ('sale', 'buyer', 'price', 'status')


class UserProfileAdmin(admin.ModelAdmin):
    """Admin form configurationfor the UserProfile model."""
    fieldsets = [
        (None, {'fields': [
            'user',
            'activation_key',
            'key_expires',
            'is_verified',
            'is_disabled',
            'phone',
            'show_phone',
            'last_login_date',
            'reg_ip',
            'last_login_ip',
            'first_login'
        ]}),
    ]
    list_display = ('user', 'last_login_date', 'key_expires')


# Register the admin forms.
admin.site.register(Course, CourseAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
