#!/usr/bin/env python

"""Django from configuration file.

This module holds all of the information for forms that need to be injected
into the templates.

"""

import re
from datetime import datetime, timedelta
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.contrib.auth.models import User
from bookmarket.models import Sale, Course, UserProfile

__author__ = "Ian Adam Naval"
__copyright__ = "Copyright 2011 Ian Adam Naval"
__credits__ = []

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ian Adam Naval"
__email__ = "ianonavy@gmail.com"
__status__ = "Development"
__date__ = "15 August 2011"


class SignupForm(forms.Form):
    """
    Class to encapsulate a signup form. Modified to validate and
    sanitize usernames and other data as well as confirm a match
    between two similar form fields.

    """

    first_name = forms.CharField(max_length=50,
        widget=forms.TextInput(
            attrs={'placeholder': 'first name'}
        ),
        error_messages={'required': 'First name is required.'})
    last_name = forms.CharField(max_length=50,
        widget=forms.TextInput(
            attrs={'placeholder': 'last name'}
        ),
        error_messages={'required': 'Last name is required.'})
    username = forms.CharField(max_length=50,
        widget=forms.TextInput(
            attrs={'placeholder': 'username'}
        ),
        error_messages={'required': 'Username is required.'})
    password = forms.CharField(max_length=50,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'password'}
        ),
        error_messages={'required': 'Password is required.'})
    confirm_password = forms.CharField(max_length=50,
        widget=forms.PasswordInput(
            attrs={'placeholder': 'confirm password'}
        ))
    email = forms.EmailField(max_length=50,
        widget=forms.TextInput(
            attrs={'placeholder': 'email address'}
        ),
        error_messages={'required': 'Email is required.'})
    confirm_email = forms.EmailField(max_length=50,
        widget=forms.TextInput(
            attrs={'placeholder': 'confirm email address'}
        ))
    phone = USPhoneNumberField(required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'phone (optional)'}
        ))

    def raise_error_at(self, msg, field):
        """Raises an error but does not return anything.

        Simplified method to catch any custom errors and inject them
        into a certain field. Warning: does not remove the data from
        cleaned_data and only works with one error message at a time.

        """
        self._errors[field] = self.error_class([msg])
        #del self.cleaned_data[field]

    def check_confirm(self, field, name):
        """ Checks and returns whether the confirmation field matches

        Args:
        field: the field to check. The confirmation field must follow
            the naming convention confirm_<field>
        name: the human-readable name that is displayed in the error.

        """
        data = self.cleaned_data
        if data.has_key(field):
            if data.has_key('confirm_%s' % field):
                if data.get(field) != data.get('confirm_%s' % field):
                    self.raise_error_at((u"The %s you have entered do not "
                                         u"match." % name), field)
            else:
                self.raise_error_at((u"You must confirm your %s." % field),
                                    field)

    def clean_first_name(self):
        """Validates first name as alphabetical only."""
        data = self.cleaned_data['first_name'].capitalize()

        if re.match(r"^[a-zA-Z]*$", data) is None:
            raise forms.ValidationError("First name must contain letters "
                                        "only.")

        return data

    def clean_last_name(self):
        """Validates last name as alphabetical only."""
        data = self.cleaned_data['last_name'].capitalize()

        if re.match(r"^[a-zA-Z]*$", data) is None:
            raise forms.ValidationError("Last name must contain letters only.")

        return data

    def clean_username(self):
        """Validates username as alphanumeric, _ and - and [3..50] in length"""
        data = self.cleaned_data['username']

        if data and User.objects.filter(username=data):
            raise forms.ValidationError("Username %s is already taken." % data)
        if re.match(r"^[a-zA-Z0-9_-]*$", data) is None:
            raise forms.ValidationError("Username must be alphanumeric, _ "
                                        "and - only.")
        if len(data) < 3:
            raise forms.ValidationError("Username too short. Must be at least "
                                        "3 characters long.")
        if len(data) > 50:
            raise forms.ValidationError("Username too long. Must be no more "
                                        "than 50 characters long.")

        return data

    def clean_password(self):
        """Validates the password."""
        data = self.cleaned_data['password']

        if len(data) < 6:
            raise forms.ValidationError("Password too short. Must be at least "
                                        "6 characters long.")
        if len(data) > 50:
            raise forms.ValidationError("Password too long. Must be no more "
                                        "than 50 characters long.")

        return data

    def clean_email(self):
        """Check that the email address is unique."""
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if (email and User.objects.filter(email=email)
                          .exclude(username=username).count()):
            raise forms.ValidationError(u'An account with email address %s '
                                        u'already exists.' % email)
        return email

    def clean(self):
        """Customized form validation.

        This method is called after the individual field clean methods
         have been called and cleaned_data has been updated. Returns
        the finalized cleaned_data.

        """

        data = self.cleaned_data

        # Check that the confirmation fields match
        self.check_confirm('password', 'passwords')
        self.check_confirm('email', 'email addresses')

        return data


class CustomSetPasswordForm(SetPasswordForm):
    """Custom form for set password to verify the password."""

    def clean_new_password1(self):
        """Validates the password."""
        password1 = self.cleaned_data.get('new_password1')

        if len(password1) < 6:
            raise forms.ValidationError("Password too short. Must be at least "
                                        "6 characters long.")
        if len(password1) > 50:
            raise forms.ValidationError("Password too long. Must be no more "
                                        "than 50 characters long.")

        return password1

    def clean_new_password2(self):
        """Check that the passwords match."""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Sorry, the password fields did "
                                            "not match.")
        return password2


class ContactForm(forms.Form):
    """Contact form for the Contact Us page."""

    name = forms.CharField(error_messages={'required': 'Name is required.'})
    email = forms.EmailField(
        error_messages={'required': 'Email is required.'}
    )
    reason = forms.ChoiceField(choices=(
        (u'General Question', u'General Question'),
        (u'Feature Request', u'Feature Request'),
        (u'Bug Report', u'Bug Report'),
        (u'Other', u'Other (please explain)')
    ))
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': 'Message'}
        ),
        error_messages={'required': 'Message is required.'}
    )


class ReportForm(forms.Form):
    """Report form for the Report page."""

    name = forms.CharField()
    email = forms.CharField(
    )
    reason = forms.ChoiceField(choices=(
        (u'Inaccurate Information', u'Inaccurate Information'),
        (u'Language', u'Vulgar Language'),
        (u'Hate Speech', u'Hate Speech'),
        (u'Adult Conent/Nudity', u'Adult Content/Nudity'),
        (u'Offensive Material', u'Offensive Material'),
        (u'Other', u'Other (please explain)')
    ))
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': 'Message'}
        )
    )


class SaleForm(forms.ModelForm):
    """Form for creating a new sale."""

    course = forms.ModelChoiceField(Course.objects.all().order_by('number'),
        error_messages={'required': 'Course is required.'})

    title = forms.CharField(required=True,
        error_messages={'required': 'Title is required.'})

    isbn = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '(Optional)'}),
        required=False)

    condition = forms.ChoiceField(choices=Sale.CONDITION_CHOICES,
        error_messages={'required': 'Course is required.'}, initial='Used')

    price = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '42.00'}),
        error_messages={'required': 'Price is required.'}, max_length=6)

    image = forms.URLField(required=False,
        widget=forms.TextInput(attrs={'placeholder': 'http://www.example.com/'
                                                     'image.png'}),
        error_messages={'required': 'Image is required.'})

    expires = forms.CharField(max_length=3,
        error_messages={'required': 'Expiration time is required.'})

    notes = forms.CharField(required=False,
        widget=forms.Textarea(
            attrs={'placeholder': 'Some highlighting, annotated, dog-eared.',
                   'cols': '50', 'rows': '5'}))

    def clean_expires(self):
        """"""
        expires = self.cleaned_data.get('expires')
        try:
            expires = int(expires)
        except:
            raise forms.ValidationError('Invalid number of days until offer '
                                        'expires.')

        if expires <= 0:
            expires = 1

        expires = datetime.now() + timedelta(days=expires)
        return expires

    def clean_isbn(self):
        """Validates ISBN-13 with the checkdigit."""
        isbn = self.cleaned_data.get('isbn')
        if not isbn: return isbn

        isbn = isbn.replace("-", "").replace(" ", "").upper();
        match = re.search(r'^(\d{12})(\d{1})$', isbn)
        if not match:
            raise forms.ValidationError('Must be ISBN-13.')

        digits = match.group(1)
        check_digit = match.group(2)

        result = 10 - (sum((3 if i % 2 else 1) * int(digit) for i, digit in \
            enumerate(digits)) % 10)
        if int(result % 10) != int(check_digit):
            raise forms.ValidationError('Invalid ISBN.')

        return isbn

    class Meta:
        model = Sale


class SearchForm(forms.Form):
    """Form for searching for a particular book"""

    course = forms.ModelChoiceField(Course.objects.all().order_by('number'),
                                    required=False)

    title = forms.CharField(required=False)

    isbn = forms.CharField(required=False)

    def clean_isbn(self):
        """Validates ISBN-13 with the checkdigit."""
        isbn = self.cleaned_data.get('isbn')
        if not isbn: return isbn

        isbn = isbn.replace("-", "").replace(" ", "").upper();
        match = re.search(r'^(\d{12})(\d{1})$', isbn)
        if not match:
            raise forms.ValidationError('Must be ISBN-13.')

        digits = match.group(1)
        check_digit = match.group(2)

        result = 10 - (sum((3 if i % 2 else 1) * int(digit) for i, digit in
            enumerate(digits)) % 10)
        if int(result % 10) != int(check_digit):
            raise forms.ValidationError('Invalid ISBN.')

        return isbn


class AccountForm(forms.Form):
    phone = USPhoneNumberField(required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'optional'}
        ))