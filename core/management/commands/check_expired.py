#!/usr/bin/env python

from datetime import date, timedelta, datetime
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from core.models import Sale, Offer, UserProfile
from core.utils import currency
from knightbookmarket import settings

class Command(BaseCommand):
    args = ''
    help = 'Checks database for expired courses.'

    def handle(self, *args, **options):
        sales = Sale.objects.filter(expires__lte=date.today(),
                                    status=Sale.PENDING)

        self.stdout.write('KNIGHT BOOK MARKET EXPIRATION REPORT\n')
        self.stdout.write('Datetime: %s\n\n' % datetime.now())

        if len(sales) == 0:
            self.stdout.write('No sales expired today.\n')

        site = Site.objects.get(id=settings.SITE_ID)
        from_ = settings.EMAIL_HOST_USER
        main_admin_name = settings.ADMINS[0]

        for sale in sales:
            if sale.check_expired():
                self.stdout.write('%s\'s deadline was extended.\n' % str(sale))