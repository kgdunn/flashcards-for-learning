from __future__ import unicode_literals
import json

from django.db import models
from django.template.defaultfilters import slugify

TOKEN_LENGTH = 8

class Tag(models.Model):
    """ Tags for ``WordItems``. """
    short_name = models.CharField(max_length=50)
    slug = models.SlugField(editable=False, unique=True)
    description = models.CharField(max_length=150)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.short_name)
        super(Tag, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.short_name)

class Person(models.Model):
    """ Defines a person / course participant """
    display_name = models.CharField(max_length=200,
                                    verbose_name="Display name")
    slug = models.SlugField()
    email = models.EmailField(unique=True)
    is_validated = models.BooleanField(default=False, help_text=('Will be auto-'
                        'validated once user has clicked on their email link.'))

    def __unicode__(self):
        return unicode('{0} [{1}]'.format(self.display_name, self.email))

    def save(self, *args, **kwargs):
        self.display_name  = self.display_name.strip()
        super(Person, self).save(*args, **kwargs) # Call the "real" save()


class WordItem(models.Model):
    part1 = models.TextField(max_length=500)
    part2 = models.TextField(max_length=500)
    datetime = models.DateTimeField(auto_now_add=True)
    person = models.ForeignKey('Person')
    tags = models.ManyToManyField(to='Tag', blank=True)

    counts_wrong = models.PositiveIntegerField(default=0)

    # can be negative when checking the answer repeatedly
    counts_right = models.IntegerField(default=0)

    # sequence of right (1) and wrong (0) answers provided for this word
    answers = models.TextField(default='', blank=True)

    lastquizzed = models.DateTimeField(auto_now=True)

    # A number between -1 and 1 that indicates how accurate the user is
    accuracy = models.FloatField(default=0.0)

    def get_answers(self):
        """ Returns a list (instead of the JSON string) of the quiz
        items that have been asked.
        """
        try:
            return json.loads(self.answers)
        except ValueError:
            return list()

    answer_seq = property(get_answers)


    def save(self, *args, **kwargs):
        den = (abs(self.counts_right) + self.counts_wrong + 0.0)
        if den == 0.0:
            self.accuracy = 0.0
        else:
            self.accuracy = self.counts_right/den
        super(WordItem, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{0} :: {1}'.format(unicode(self.part1[0:10]),
                                           unicode(self.part2[0:10]))

class Quiz(models.Model):
    # 3 datetime fields to track for the quiz.
    when_started = models.DateTimeField(auto_now_add=True)
    when_last_used = models.DateTimeField(auto_now=True)
    when_ended = models.DateTimeField(blank=True, null=True)
    person = models.ForeignKey('Person')

    # Unique hash for this quiz
    quiz_hash = models.CharField(max_length=TOKEN_LENGTH, unique=True)

    # Which words have been asked so far in the quiz. String. Represents a list
    # of the primary ID's to WordItem
    words_asked = models.TextField(default='')
    words_correct_first_time = models.TextField(default='')

    # The 0-based index into ``words_asked`` list that tells which is the
    # ID of the current word being asked
    currentitem = models.PositiveIntegerField(default=0)

    def get_n_words_asked(self):
        if self.words_asked:
            return len(json.loads(self.words_asked))
        else:
            return 0
    n_words_asked = property(get_n_words_asked)

    def get_the_score(self):
        a = self.correct
        return '{0}/{1}'.format(sum(self.correct), self.n_words_asked)
    the_score = property(get_the_score)

    def get_quiz_seq(self):
        """ Returns a list (instead of the JSON string) of the quiz
        items that have been asked.
        """
        try:
            return json.loads(self.words_asked)
        except ValueError:
            return list()

    quiz_seq = property(get_quiz_seq)

    def get_quiz_correct(self):
        """ Returns a list (instead of the JSON string) of the quiz
        items that were correct on first attempt.
        """
        try:
            return json.loads(self.words_correct_first_time)
        except ValueError:
            return list()

    correct = property(get_quiz_correct)

class Token(models.Model):
    """ Tokens capture time/date and permissions of a user to access the
    ``System`` models.
    """
    person = models.ForeignKey('Person', null=True, blank=True)
    hash_value = models.CharField(max_length=32, editable=False, default='-'*32)
    was_used = models.BooleanField(default=False)
    time_used = models.DateTimeField(auto_now=True, auto_now_add=False)


