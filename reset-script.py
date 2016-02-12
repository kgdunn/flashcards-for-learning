#!/usr/bin/python

# Resets the counts and accuracy for a particular user
import os
import django
import urllib2
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import flashcards.settings
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "flashcards.settings"
)
django.setup()

from vocab.models import WordItem, Person
from vocab.views import logger

person = Person.objects.filter(email='kgdunn@gmail.com')[0]
pairs = WordItem.objects.filter(person=person)
for item in pairs:
    item.counts_wrong = 0
    item.counts_right = 0
    item.answers = ''
    item.save()
    logger.debug(u'Resetted the stats for word: {0}'.format(item.part1))