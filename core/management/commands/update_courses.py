#!/usr/bin/env python

from django.core.management.base import BaseCommand, CommandError
from core.models import Course

class Command(BaseCommand):
    args = ''
    help = 'Updates courses in the database.'

    def handle(self, *args, **options):
        courses = "1000 JOURNALISM, 5200 GEOMETRY CP, 1030 JOURNALISM II, 5250 GEOMETRY H, 1060 ADVANCED JOURNALISM, 5300 ALGEBRA II CP, 1200 TV PRODUCTION I, 5350 ALGEBRA II/TRIG H, 1230 TV PRODUCTION II, 5400 PRECALCULUS CP, 1260 TV PRODUCTION III, 5450 (H) PRECALCULUS, 1350 BROADCAST & MEDIA STUDIES, 5500 STATISTICS, 1510 COMPUTER APPLICATIONS, 5550 TRIGONOMETRY, 1600 WEB DESIGN & DEV, 5600 CALCULUS, 1660 GRAPHIC DESIG & MOTION, 5650 AP CALCULUS AB, 2100 ENGLISH I CP, 5700 AP CALCULUS BC, 2150 ENGLISH I H, 5800 AP STATISTICS, 2200 ENGLISH II CP, 7110 REV OF JESUS, 2250 ENGLISH II H, 7160 WHO IS JESUS, 2300 ENGLISH III, 7200 HEBREW SCRIPTURES, 2350 AP LANGUAGE, 7250 NEW TESTAMENT, 2400 ENGLISH IV, 7300 CHRISTIAN MORAL PRINCIPLE, 2450 AP LITERATURE, 7350 JUSTICE & PEACE, 3555 FRESHMAN ACTING, 7450 CHRISTIAN LIFESTYLES, 3600 ACTING I, 7475 CHRISTIAN LEADERSHIP, 3650 ACTING II, 7500 WORLD RELIGIONS - WESTERN, 3700 ACTING III, 7525 WORLD RELIGIONS - EASTERN, 3775 FILM ACTING, 8200 BIOLOGY CP, 3820/3840 PLAY PROD/ PLAY WRI, 8250 BIOLOGY H, 3975 PHOTOGRAPHY I, 8280 HUMAN ANATOMY & PHYSIOLOG, 3980 PHOTOGRAPHY II, 8290 AP BIOLOGY, 4000 SPANISH I, 8300 CHEMISTRY CP, 4025 SPANISH I FOR NS, 8325 CHEMISTRY H, 4100 SPANISH II, 8350 AP CHEMISTRY, 4150 SPANISH II HONORS, 8400 PHYSICS CP, 4200 SPANISH III, 8450 AP PHYSICS C: MECHANICS, 4250 SPANISH III HONORS, 8600 SPORTS MEDICINE, 4300 SPANISH IV, 8650 ADV SPORTS MEDICINE, 4350 AP SPANISH LANGUAGE, 9100 WORLD GEOGRAPHY, 4500 FRENCH I, 9210 WORLD HISTORY, 4525 FRENCH II, 9250 AP EUROPEAN HISTORY, 4550 FRENCH III, 9300 U.S. HISTORY CP, 4575 AP FRENCH LANGUAGE, 9350 AP U.S. HISTORY, 4700 LATIN I, 9400 GOVERNMENT CP, 4725 LATIN II, 9450 ECONOMICS CP, 4750 LATIN III, 9550 AP SENIOR SOCIAL STUDIES, 4800 JAPANESE I, 9560 AP GOVT / H ECON, 4825 JAPANESE II, 9625 LAW & SOCIETY, 4850 JAPANESE III, 9650 PSYCHOLOGY OF PREJUDICE, 4875 AP JAPANESE IV, 9675 SOCIOLOGY, 5100 ALGEBRA I CP, 9700 PSYCHOLOGY, 5150 ALGEBRA I H".split(", ")

        Course.objects.all().delete()
        self.stdout.write('Cleared the database.\n')

        for course in courses:
            number, name = course[:4], course[5:]
            new_course = Course()
            new_course.number = int(number)
            new_course.name = name
            new_course.save()

            self.stdout.write('Successfully added %s %s.\n' % (number, name))