#!/usr/bin/python

# Creates links for the OOI materials: MP4, Script, Captions
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

from vocab.models import WordItem, Person, Tag
from vocab.views import add_new_word

# Exported from Google Docs:
# https://docs.google.com/spreadsheets/d/1BEpbL92B0TOE6IfIj5U3nPkeUzEZ5g8aHBEBbBs1dnY/edit#gid=1765480361

person = Person.objects.filter(email='kgdunn@gmail.com')[0]
person = Person.objects.filter(email='kim.faber@oberlin.edu')[0]
person = Person.objects.filter(email='maudkieft@gmail.com')[0]
person = Person.objects.filter(email='ingeborgvandijck@gmail.com')[0]
person = Person.objects.filter(email='ingrid.mersel@gmail.com')[0]
person = Person.objects.filter(email='andrews.suzy@gmail.com')[0]
person = Person.objects.filter(email='mohamad.aladeeb@gmail.com')[0]
tag, created = Tag.objects.get_or_create(short_name='Thema 5(DF)',
                                         description='Thema 5 van "De Finale"')
tag.save()

with open('Woordenschat-DF-Thema5.tsv', 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    for row in reader:

        worditem = add_new_word(part1=row[0],
                                part2=row[1],
                                person=person)
        worditem.tags.add(tag)
        worditem.save()

