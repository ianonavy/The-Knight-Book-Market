#!/usr/bin/env python

"""Django models file to define the models for the bookstore application.

Contains code to encapsulate a mentor, a team and a connection between the two.

"""

import datetime
import random
from hashlib import md5
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db import models


def currency(value):
    # Original filter code found at  http://djangosnippets.org/snippets/2365/
    symbol = '$'
    thousand_sep = ','
    decimal_sep = '.'

    intstr = str(int(value))
    f = lambda x, n, acc=[]: f(x[:-n], n, [(x[-n:])]+acc) if x else acc
    intpart = thousand_sep.join(f(intstr, 3))
    return "%s%s%s%s" % (symbol, intpart, decimal_sep, ("%0.2f" % value)[-2:])


class Course(models.Model):
    """Model that encapsulates a course."""

    number = models.CharField(max_length=4)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        """Returns a unique string identifier for this course."""
        return "%s %s" % (self.number, self.name)


class Sale(models.Model):
    """Model that encapsulates a sale."""

    PENDING = 0
    SOLD = 1
    EXPIRED = 2
    CANCELLED = 3
    SOLD_AND_REMOVED = 4
    STATUS_CHOICES = (
        (PENDING, u'PENDING'),
        (SOLD, u'SOLD'),
        (EXPIRED, u'EXPIRED'),
        (CANCELLED, u'CANCELLED'),
        (SOLD_AND_REMOVED, u'SOLD AND REMOVED')
    )

    CONDITION_CHOICES = (
        (u'Brand New', u'Brand New'),
        (u'Slightly Used', u'Slightly Used'),
        (u'Used', u'Used'),
        (u'Poor', u'Poor')
    )
    
    status  = models.IntegerField(max_length=1, choices=STATUS_CHOICES)
    merchant = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    matches_official = models.BooleanField()
    condition = models.CharField(max_length=13, choices=CONDITION_CHOICES)
    title = models.CharField(max_length=50)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    image = models.ImageField(upload_to="images/books/", max_length=1000)
    price = models.FloatField()
    expires = models.DateField(blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)

    
    def new(self, merchant, course, matches_official, condition, title, isbn,
            image, price, expires, notes):
        self.merchant = merchant
        self.course = course
        self.matches_official = matches_official
        self.condition = condition
        self.title = title
        self.isbn = isbn
        self.image = image
        self.price = price
        self.expires = expires
        self.notes = notes
    
    def accept_offer(self, chosen_offer):
        self.sale.status = Sale.SOLD
        self.save()
        
        offer.accept()
        offers = Offer.objects.filter(sale=self.sale) \
                              .exclude(id=chosen_offer.id)
        for offer in offers:
            offer.decline()
    
    def cancel(self):
        offers = Offer.objects.filter(sale=self)
        for offer in offers:
            offer.cancel_by_sale()
        
        self.status = Sale.CANCELLED
        self.save()
        
    def remove(self):
        if self.status == SOLD:
            self.status = Sale.SOLD_AND_REMOVED
            self.save()
        
    def check_expired(self):
        if len(offers) == 0:
            self.postpone_expiration()
        else:
            self.sale.expire()
    
    def postpone_expiration(self):
        # Send e-mail about expiration being postponed.
        self.expires = self.expires + timedelta(days=3)
        self.save()
    
    def expire(self):
        self.status = Sale.EXPIRED
        self.save()
        # Send email about offer expiration.

    def __unicode__(self):
        """Returns a unique string identifier for this sale."""
        return u"%s for %s by %s" % (self.title, currency(self.price),
                                     self.merchant.get_full_name())


class Offer(models.Model):
    """Model that encapsulates a book."""

    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    CANCELLED = 3
    STATUS_CHOICES = (
        (PENDING, u'PENDING'),
        (ACCEPTED, u'ACCEPTED'),
        (DECLINED, u'DECLINED'),
        (CANCELLED, u'CANCELLED')
    )

    status = models.IntegerField(max_length=1, choices=STATUS_CHOICES)
    sale = models.ForeignKey(Sale)
    buyer = models.ForeignKey(User)
    price = models.FloatField()
    
    def new(self, sale, buyer, price):
        self.status = Offer.PENDING
        self.sale = sale
        self.buyer = buyer
        self.price = price
        self.save()
    
    def available(self):
        sale = self.sale
        return sale.status == Sale.PENDING and self.status == Offer.PENDING
    
    def accept(self):
        self.status = Offer.ACCEPTED
        self.save()
        # Send e-mail that the offer was accepted.
        
    def decline(self):
        self.status = Offer.DECLINED
        self.save()
        # Send e-mail that the offer was declined.
    
    def cancel_by_sale(self):
        self.cancel()
        # Send e-mail about cancelled sale.
    
    def cancel(self):
        self.status = Offer.CANCELLED
        self.save()

    def __unicode__(self):
        """Returns a unique string identifier for this offer."""
        return u"%s for %s by %s" % (self.sale.title, currency(self.price),
                                     self.buyer.get_full_name())


class UserProfile(models.Model):
    """Class to extend the user model for verification purposes."""

    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40, unique=True)
    phone = PhoneNumberField(blank=True, null=True)
    show_phone = models.BooleanField()
    key_expires = models.DateTimeField()
    is_verified = models.BooleanField()
    is_disabled = models.BooleanField()
    last_login_date = models.DateTimeField()
    reg_ip = models.IPAddressField()
    last_login_ip = models.IPAddressField()
    first_login = models.BooleanField()
    
    def new(self, user, phone="", ip_address=""):
        salt = md5(str(random.random())).hexdigest()[:5]
    
        self.user = user
        self.activation_key = md5(salt + user.username).hexdigest()
        self.phone = phone
        self.show_phone = True
        self.key_expires = datetime.datetime.today() + datetime.timedelta(2)
        self.is_verified = False
        self.is_disabled = False
        self.last_login_date = datetime.datetime.today()
        self.reg_ip = ip_address
        self.last_login_ip = ip_address
        self.first_login = True
        
        self.save()

    def __unicode__(self):
        """Returns a unique string identifier for this offer."""
        return self.user.get_full_name()