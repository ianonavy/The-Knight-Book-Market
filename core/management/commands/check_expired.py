#!/usr/bin/env python

from datetime import date, timedelta, datetime
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from bookmarket.models import Sale, Offer, UserProfile
from bookmarket.utils import currency
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
            offers = Offer.objects.filter(sale=sale)

            if len(offers) == 0:
                sale.expires = sale.expires + timedelta(7)

                subject = "%s Sale Reminder" % site.name
                body = ("Hi, %s!\n\nYour sale for %s has reached its "
                    "expiration date, but no one offered to buy it. The "
                    "deadline has been extended to %s. If this is not the "
                    "first time you've seen a message like this, you may want "
                    "to consider cancelling the sale.\n\nSincerely,\n%s" %
                    (sale.merchant.first_name, sale.title,
                     sale.expires.strftime('%B %d, %Y'), main_admin_name))
                send_mail(subject, body, from_, [sale.merchant.email])
                self.stdout.write('%s\'s deadline was extended.\n' % str(sale))
            else:
                sale.status = Sale.SOLD

                highest = offers.order_by('-price')[0]
                highest.status = Offer.ACCEPTED
                highest.save()

                subject = "%s Sold at %s" % (sale.title, site.name)
                buyer_name = highest.buyer.get_full_name()
                body = ("Congratulations, %s!\n\nYour sale for %s has reached "
                    "its expiration date, and %s has been automatically "
                    "chosen as the highest bidder at %s. You may contact %s at"
                    " %s" % (sale.merchant.get_full_name(), sale.title,
                        buyer_name, currency(highest.price), buyer_name,
                        highest.buyer.email))
                try:
                    phone = UserProfile.objects.get(user=highest.buyer).phone
                    if phone:
                        body += " or at %s" % phone
                except:
                    self.stdout.write('Error loading %s\'s profile.\n' %
                                      highest.buyer)
                body += ".\n\nSincerely,\n%s" % main_admin_name
                send_mail(subject, body, from_, [sale.merchant.email])

                subject = "%s Sale Chosen!" % site.name
                body = ("Congratulations, %s!\n\nYour offer to purchase %s for"
                        " %s has been accepted. You may contact %s at %s" %
                        (highest.buyer.get_full_name(), sale.title,
                         currency(highest.price),
                         sale.merchant.get_full_name(), sale.merchant.email))
                try:
                    phone = UserProfile.objects.get(user=sale.merchant).phone
                    if phone:
                        body += " or at %s" % phone
                except:
                    self.stdout.write('Error loading %s\'s profile.\n' %
                                      sale.merchant)
                body += ".\n\nSincerely,\n%s" % main_admin_name
                send_mail(subject, body, from_, [highest.buyer.email])
                self.stdout.write('%s expired.\n' % str(sale))

            for offer in offers:
                if offer.id != highest.id:
                    offer.status = Offer.DECLINED
                    offer.save()

                    subject = "%s Offer Declined" % site.name
                    body = ("Dear %s,\n\nUnfortunately, your offer to "
                            "purchase %s from %s has been declined. Please "
                            "continue to browse the site as someone else may "
                            "create a new listing for the book you need. "
                            "Thanks for using our site!\n\nSincerely,\n%s" %
                            (offer.buyer.get_full_name(), offer.sale.title,
                             offer.sale.merchant.get_full_name(),
                             main_admin_name))
                    send_mail(subject, body, from_, [offer.buyer.email])
            sale.save()
