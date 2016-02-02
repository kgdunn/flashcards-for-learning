# Creates links for the OOI materials: MP4, Script, Captions
import os
import django
import urllib2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import flashcards.settings
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "flashcards.settings"
)
django.setup()

from vocab.models import WordItem, Person, Tag

# Exported from Google Docs:
# https://docs.google.com/spreadsheets/d/1BEpbL92B0TOE6IfIj5U3nPkeUzEZ5g8aHBEBbBs1dnY/edit#gid=1765480361

person = Person.objects.filter(email='kgdunn@gmail.com')[0]
tag = Tag(short_name='Thema 5(DF)', description='Thema 5 van "De Finale"')
tag.save()

fobj = file('Woordenschat-DF-Thema5.csv', 'rt')
for idx, line in enumerate(fobj.readlines()):

    line = line.strip().split(',')

    worditem = WordItem(part1=line[0], part2=line[1], person=person)
    worditem.save()
    worditem.tags.add(tag)
    worditem.save()




fobj.close()