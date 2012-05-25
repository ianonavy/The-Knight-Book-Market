#!/usr/bin/env python

"""Django views for the core application."""

import knightbookmarket.settings
import urllib
import urllib2
import re
import os
import StringIO
from PIL import Image
from math import ceil
from datetime import datetime, timedelta, date
from django.contrib.auth import logout, authenticate
from django.http import HttpResponseRedirect
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.db.models import Max
from core.forms import SignupForm, ContactForm, ReportForm, SaleForm, \
    SearchForm, AccountForm
from core.models import UserProfile, Course, Sale, Offer
from core.utils import message_page, generate_new_key,\
    error_page, get_remote_ip, load_page, share_sale, \
    title_case, currency
from django_facebook.api import get_facebook_graph
from knightbookmarket.settings import SITE_ROOT, STATIC_ROOT


def index(request, flash=None):
    """View that handles the guest index page and user home."""

    flash = request.GET.get('flash', flash) # Get flash message.

    selling = []
    sold = []
    buying = []
    bought = []
    
    if request.user.is_authenticated():
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.first_login:
                #if facebook_connected(request):
                #    flash = ('Welcome to the Book Market! If you\'d like, you '
                #             'can set your phone number in the Account page. '
                #             'For convenience, it will automatically be sent '
                #             'to users to whom you choose to sell your books.')
                #else:
                flash = 'Welcome to the Book Market!'
                profile.first_login = False
                profile.save()
        except:
            error = "There was an error loading your user profile!"
        
        # Sort sales into "selling" and "sold" accordingly
        for sale in Sale.objects.filter(merchant=request.user):
            offers = Offer.objects.filter(sale=sale)
            highest = offers.aggregate(Max('price'))['price__max']
            this_sale = {
                'id': sale.id,
                'title': sale.title,
                'image': sale.image,
                'offers': len(offers.filter(status=Offer.PENDING)),
                'highest': highest
            }
            if sale.status == Sale.PENDING:
                selling.append(this_sale)
            elif sale.status == Sale.SOLD:
                offer = Offer.objects.get(sale=sale, status=Offer.ACCEPTED)
                buyer = "%s %s" % (offer.buyer.first_name,
                                   offer.buyer.last_name)
                this_sale['price'] = offer.price
                this_sale['buyer'] = buyer
                sold.append(this_sale)
        selling.sort(key=lambda sale: sale['title'].lower())
        sold.sort(key=lambda sale: sale['title'].lower())

        for offer in Offer.objects.filter(buyer=request.user):
            offer.highest = Offer.objects.filter(sale=offer.sale) \
                .aggregate(Max('price'))['price__max']

            if (offer.sale.status == Sale.PENDING and
                    offer.status == Offer.PENDING):
                buying.append(offer)
            elif (offer.sale.status == Sale.SOLD and
                    offer.status == Offer.ACCEPTED):
                bought.append(offer)
        buying.sort(key=lambda offer: offer.sale.title.lower())
        bought.sort(key=lambda offer: offer.sale.title.lower())
        

    return load_page(request, 'index.html',
                     {'flash': flash, 'selling': selling, 'sold': sold,
                      'buying': buying, 'bought': bought})


def signup(request):
    """View that handles user registration."""

    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.method == "GET":
        form = SignupForm() # Create an empty form if the method is GET.
    elif request.method == "POST":
        form = SignupForm(request.POST) # Populate the form with POST data.
        if form.is_valid():
            # Get the form data.
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # Create a new user and profile.
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save() # Save the user.

            new_profile = UserProfile()
            new_profile.new(user, form.cleaned_data['phone'],
                            get_remote_ip(request))

            # Send an email with the confirmation link
            site = Site.objects.get_current()
            subject = "%s User Activation" % site.name
            body = ("Hello, %s, and thanks for signing up for an account at %s!"
                    "\n\nTo activate your account, click this link within 48 hours:"
                    "\n\nhttp://%s/login/%s" % (user.username, site.domain, site.domain,
                    new_profile.activation_key))
            send_mail(subject, body, 'settings.EMAIL_HOST_USER', [user.email])
            
            # Redirect to a confirmation page.
            return HttpResponseRedirect('/signup/confirmed/')

    # Load signup.html on GET request and POST error.
    return load_page(request, 'signup.html', {'form': form})


def signup_confirmed(request):
    """Simple view to show a message after the user successfully signs up."""

    return message_page(request, u'Thank you for signing up! An email was '
        u'dispatched to your address. Please click the link inside to verify '
        u'your email and activate your account, which expires in 48 hours. '
        u'Please check your email\'s spam folder if it does not appear in the '
        u'inbox.')


def resend_key(request, username):
    """View for resending an expired or lost authentication key."""

    # Generate a new activation key for the user.
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    activation_key = generate_new_key(user)

    if profile.is_verified:
        return message_page(request, 'Your user account is already activated!')

    # Send a new email with the confirmation link
    site = Site.objects.get(id=settings.SITE_ID)
    subject = "%s User Activation" % site.name
    body = ("Hello, %s, and thanks for signing up for an account at %s!"
        "\n\nTo activate your account, click this link within 48 hours:"
        "\n\nhttp://%s/login/%s" % (user.username, site.domain, site.domain,
            activation_key))

    send_mail(subject, body, 'settings.EMAIL_HOST_USER', [user.email])

    return message_page(request, 'A new link was sent to %s' % user.email)


def login_view(request, activation_key=""):
    """View that handles logging in. Verifies activation keys too."""

    # Default variable values.
    error = u''
    username = ''
    noverify = False

    # Logging in
    if request.method == 'POST':
        # Get login information from the POST data
        username = request.POST['username']
        password = request.POST['password']

        # Create a new user and authenticate it
        user = authenticate(username=username, password=password)
        if user is not None: # User exists

            try:
                profile = UserProfile.objects.get(user=user)

                if profile.is_verified:
                    if user.is_active:
                        if profile.is_disabled:
                            # Profile deactivated by user.
                            profile.is_disabled = False;
                            profile.last_login_date = datetime.today()
                            profile.last_login_ip = get_remote_ip(request)
                            profile.save()
                            login(request, user)
                            return index(request, 'Welcome back!')

                        # Profile is active and enabled.
                        profile.last_login_date = datetime.today()
                        profile.last_login_ip = get_remote_ip(request)
                        profile.save()
                        login(request, user)
                    else:
                        # Profile disabled.
                        error = (u'Sorry, your user account has been '
                                 u'disabled by an administrator for '
                                 u'misconduct and/or violating the terms of '
                                 u'service agreement.')
                else:
                    # If the user is not verified, try verifying.
                    if not activation_key:
                        error = (u'Your account has not been verified. Please '
                                 u'check your email for a verification link.')
                        noverify = True

                    else:
                        try:
                            profile = get_object_or_404(UserProfile,
                                activation_key=activation_key)
                            user = profile.user
                        except:
                            error = "Invalid verification key."
                            noverify = True

                    # Error if the activation key expired.
                    if profile.key_expires < datetime.today():
                        error = (u'Your activation key has expired. Please '
                                 u'request a new one with the link below.')
                        noverify = True

                    elif not noverify:
                        profile.is_verified = True
                        profile.last_login_date = datetime.today()
                        profile.last_login_ip = get_remote_ip(request)
                        profile.save()
                        login(request, user)
            except:
                if user.is_staff:
                    login(request, user)
                else:
                    error = (u'Error: your user profile could not be loaded. '
                             u'Please contact an administrator or create a '
                             u'new account. We are sorry for any '
                             u'inconvenience.')
                raise
        else:
            error = u'Invalid username and password.'

    # GET and POST with errors

    # Display page
    if request.user.is_active: # User is logged in.
        if request.user.is_staff: # User is an admin.
            return HttpResponseRedirect('/admin') # Redirect to admin page.
        elif request.POST.get('next', None): # User is not an admin
            return HttpResponseRedirect(request.POST['next'])
        else:
            return HttpResponseRedirect('/') # Redirect home.
    else: # User is not logged in.
        next = request.GET.get('next', '')
        return load_page(request, 'login.html', {'error': error,
                                                 'username': username,
                                                 'key': activation_key,
                                                 'noverify': noverify,
                                                 'next': next})


def logout_view(request):
    """Simple view for handling logging out."""
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def new_sale(request):
    """View for handling the creation of new sales."""
    form = SaleForm()
    error = ""
    
    facebook = (get_facebook_graph(request) != None)
    
    if request.method == "POST":
        data = request.POST.copy()
        data['merchant'] = request.user.id
        data['status'] = Sale.PENDING

        form = SaleForm(data)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.expires = form.cleaned_data['expires']

            url = request.POST.get('image', '')
            if url == '' or len(url) > 1000:
                sale.image = File(open(
                    os.path.join(STATIC_ROOT, 'img/book_placeholder.gif'))
                )

            else:
                req = urllib2.Request(url, headers={'User-Agent' :
                                                    "Magic Browser"})
                img_temp = NamedTemporaryFile(delete=True)
                image = urllib2.urlopen(req).read()
                img_temp.write(image)
                img_temp.flush()

                try:
                    im = Image.open(StringIO.StringIO(image))
                    im.verify()
                except Exception, e:
                    error = "Invalid image URL." + str(e)
                    return load_page(request, 'new_sale.html', {'form': form,
                                                                'error': error})

                filename = data['image'] if '.' in data['image'][-5:] else\
                    data['image'] + '.png'
                sale.image.save(filename, File(img_temp))

            sale.save()

            message = 'Thanks, your sale has been listed!'
            try:
                if request.POST['facebook']:
                    share_sale(request, sale)
                    message += ' A post has been added to your timeline.'
            except:
                pass

            return index(request, flash=message)
    return load_page(request, 'new_sale.html', {'form': form, 'error': error, 'facebook': facebook})


@login_required
def cancel_sale(request, id=-1):
    id = int(id)
    try:
        sale = Sale.objects.get(id=id, merchant=request.user)
    except:
        return error_page(request, 'A sale with the ID %d could not be found.'
                                    % id)
    if sale.status != Sale.PENDING:
        return error_page(request, 'That sale has already been cancelled.')

    sale.cancel()
    return HttpResponseRedirect('/')


@login_required
def remove_sale(request, id=-1):
    Sale.objects.get(id=id).remove()
    return HttpResponseRedirect('/')


def browse(request, id=-1):

    if id is not -1: # Browse book interface.
        try:
            sale = Sale.objects.get(id=id, status=Sale.PENDING)
        except:
            return error_page(request, 'A sale with the id %d could not be '
                                       'found.' % int(id))
        viewer = "guest"
        if request.user == sale.merchant:
            viewer = "merchant"
        elif request.user.is_authenticated():
            if len(Offer.objects.filter(sale=sale, status=Sale.PENDING,
                                        buyer=request.user)) > 0:
                viewer = "made_offer"
            else:
                viewer = "no_offer"
        offers = Offer.objects.filter(sale=sale, status=Offer.PENDING).order_by(
            '-price', 'buyer__first_name'
        )
        return load_page(request, 'sale_details.html', {'viewer': viewer,
                                                        'sale': sale,
                                                        'offers': offers})
    else:
        if request.user.is_authenticated():
            sales = Sale.objects.exclude(merchant=request.user) \
                .filter(status=Sale.PENDING)
        else:
            sales = Sale.objects.filter(status=Sale.PENDING)

        sales = sales.order_by('price', 'title', 'merchant__last_name')

        error = ""

        form = SearchForm(request.GET)
        if form.is_valid():
            title = form.cleaned_data['title'] or None
            isbn = form.cleaned_data['isbn'] or None
            course = form.cleaned_data['course'] or None

            if title: sales = sales.filter(title__icontains=title)
            if isbn: sales = sales.filter(isbn__exact=isbn)
            if course: sales = sales.filter(course__exact=course)

        my_sales = []
        for sale in sales:
            offers = Offer.objects.filter(sale=sale)
            this_sale = {
                'id': sale.id,
                'image': sale.image,
                'title': sale.title,
                'course': sale.course,
                'price': sale.price,
                'merchant': sale.merchant,
                'offers': len(offers.filter(status=Offer.PENDING)),
                'expires': sale.expires,
                'expires_soon': (sale.expires - date.today()) <= timedelta(1)
            }
            my_sales.append(this_sale)
        sales = my_sales

        per_page = 5
        pages = int(ceil(len(sales) / float(per_page)))

        page = int(request.GET.get('page', 1))

        if pages <= 0: pages = 1
        if page <= 0: page = 1
        if page > pages: page = pages

        prev = "?title=%s&isbn=%s&course%s=&page=%s" % \
            (title or "", isbn or "", course or "", (page - 1))
        next = "?title=%s&isbn=%s&course=%s&page=%s" % \
            (title or "", isbn or "", course or "", (page + 1))

        # Calculate the page number. Don't forget any leftovers on the last page.
        #page_number = min(page, ceil(len(sales) / float(per_page)))

        # Calculate the display indices from the page number.
        first = int((page - 1) * per_page)
        last = int(page * per_page)
        sales = sales[first:last]

        return load_page(request, 'browse.html',
                         {'sales': sales, 'form': form, 'error': error,
                          'prev': prev, 'next': next, 'page': page,
                          'pages': pages})


@login_required
def new_offer(request, id=-1):
    sale = Sale.objects.get(id=id)
    price = request.POST['price']
    try:
        float(price)
    except ValueError:
        return HttpResponseRedirect('/browse/%s/' % sale.id)

    try:
        offer = Offer.objects.get(sale=sale, buyer=request.user)
    except:
        offer = Offer()

    offer.new(sale, request.user, request.POST['price'])
    return HttpResponseRedirect('/browse/%s/' % sale.id)


@login_required
def accept_offer(request, id=-1):
    try:
        chosen_offer = Offer.objects.get(id=id)
    except:
        return error_page(request, 'Offer does not exist.')
    
    if not chosen_offer.available():
        return error_page(request, 'Offer no longer available!')
    else:
        chosen_offer.sale.accept_offer(chosen_offer)
        message = 'Congratulations on selling your book! You can contact %s at %s'\
                    % (chosen_offer.buyer.get_full_name(),
                       chosen_offer.buyer.email)

    return index(request, flash=message)


@login_required
def cancel_offer(request, id=-1):
    offer = Offer.objects.get(id=id)
    offer.cancel()
    return HttpResponseRedirect('/browse/%s/' % offer.sale.id)


def contact(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            send_mail('Knight Book Market Support',
                "From: %s\nReason: %s\n\n%s" % (request.POST['email'],
                                               request.POST['reason'],
                                               request.POST['message']),
                'settings.EMAIL_HOST_USER',
                ['ianonavy@gmail.com'])
            return message_page(request, u'Thanks for contacting us!')
    else:
        contact_form = ContactForm()
    return load_page(request, "contact-report.html", {'form': contact_form})


def report(request, id=None):
    if request.method == 'POST':
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            try:
                sale = unicode(Sale.objects.get(id=id))
            except:
                sale = "Not found."
            send_mail('Knight Book Market Report',
                "From: %s\n"
                "Reason: %s\n"
                "Reported Sale: %s (ID: %s)\n\n"
                "%s" % (request.POST['email'], request.POST['reason'],
                        sale, id, request.POST['message']),
                'settings.EMAIL_HOST_USER',
                ['ianonavy@gmail.com'])
            return message_page(request, u'Thanks for contacting us!')
    else:
        report_form = ReportForm()
    return load_page(request, "contact-report.html", {'form': report_form,
                                                      'report': True,
                                                      'id': id})


@login_required
def account(request):
    user = request.user
    
    try:
        profile = UserProfile.objects.get(user=request.user)
    except:
        profile = UserProfile()
        profile.new(user, ip_address=get_remote_ip(request))
        profile.save()
    
    form = AccountForm({'phone': profile.phone, 'email': user.email})
    error = ''

    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            #user.email = form.cleaned_data['email']
            user.save()
            profile.phone = form.cleaned_data['phone']
            profile.save()
            return index(request, "Your account has successfully been edited.")
        else:
            error = form.errors
    return load_page(request, 'account.html', {'form': form, 'error': error})


@login_required
def account_disable(request):
    for sale in Sale.objects.filter(merchant=request.user,
                                    status=Sale.PENDING):
        sale.cancel()

    for offer in Offer.objects.filter(buyer=request.user,
                                      status=Offer.PENDING):
        offer.cancel()

    profile = UserProfile.objects.get(user=request.user)
    profile.is_disabled = True
    profile.save()

    logout(request)
    return HttpResponseRedirect('/')