# You don't get great landscape layout with large font objects
# Prevent exactly the prior word from being picked again.

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect

from django.conf import settings as DJANGO_SETTINGS
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils.timezone import utc

import random
import hashlib
import datetime
import logging
import json
import logging
from smtplib import SMTPException

from . import models
from models import TOKEN_LENGTH

logger = logging.getLogger(__name__)
logger.debug('A new call to the views.py file')

def sign_in_user(request, hashvalue):
    """ User is sign-in with the unique hashcode sent to them,
        These steps are used once the user has successfully been validated,
        or if sign-in is successful.

        A user is considered signed-in if "request.session['person_id']" returns
        a valid ``person.id`` (used to look up their object in the DB)
        """
    logger.debug('Attempting sign-in with token {0}'.format(hashvalue))
    token = get_object_or_404(models.Token, hash_value=hashvalue)
    token.was_used = True
    token.save()
    request.session['person_id'] = token.person.id
    logger.info('RETURNING USER: {0}'.format(token.person.id))

    return HttpResponseRedirect(reverse('add_word_HTML'))

def validate_user(request, hashvalue):
    """ The new/returning user has been sent an email to sign in.
    Recall their token, mark them as validated, sign them in, run the experiment
    they had intended, and redirect them to the next URL associated with their
    token.

    If it is a new user, make them select a Leaderboard name first.
    """
    logger.info('Locating validation token {0}'.format(hashvalue))
    token = get_object_or_404(models.Token, hash_value=hashvalue)
    token.person.is_validated = True
    token.person.save()
    return sign_in_user(request, hashvalue)

def send_logged_email(subject, message, to_address_list):
    """ Sends an email to a user and it is assumed it is an HTML message.

    Returns a string error message if it failed. Returns None if sending
    succeeded.
    """
    from django.core.mail import send_mail
    logger.debug('Email [{0}]: {1}'.format(str(to_address_list), message))
    try:
        out = send_mail(subject=subject,
                  message=message,
                  from_email=None,
                  recipient_list=list(to_address_list),
                  fail_silently=False,
                  html_message=message)
        out = None
    except SMTPException as err:
        logger.error('EMAIL NOT SENT: {0}'.format(str(err)))
        out = str(err)
    return out

def send_suitable_email(person, hash_val):
    """ Sends a validation email, and logs the email message. """

    if person.is_validated:
        sign_in_URI = '{0}/sign-in/{1}'.format(DJANGO_SETTINGS.WEBSITE_BASE_URI,
                                        hash_val)
        ctx_dict = {'sign_in_URI': sign_in_URI,
                    'username': person.display_name}
        message = render_to_string('vocab/email_sign_in_code.txt',
                                   ctx_dict)
        subject = ("Unique code to sign-into the Woorden Words Website")
        to_address_list = [person.email.strip('\n'), ]

    else:
        # New users / unvalidated user
        check_URI = '{0}/validate/{1}'.format(DJANGO_SETTINGS.WEBSITE_BASE_URI,
                                             hash_val)
        ctx_dict = {'validation_URI': check_URI}
        message = render_to_string('vocab/email_new_user_to_validate.txt',
                                   ctx_dict)

        subject = ("Confirm your email address to use the Woorden Words "
                   "Website!")
        to_address_list = [person.email.strip('\n'), ]


    # Use regular Python code to send the email in HTML format.
    message = message.replace('\n','\n<br>')
    return send_logged_email(subject, message, to_address_list)

def create_token_send_email_check_success(person):
    """ Used during signing in a new user, or an existing user. A token to
    is created, and an email is sent.
    If the email succeeds, then we return with success, else, we indicate
    failure to the calling function.
    """
    # Create a token for the new user
    hash_value = get_quiz_hash(token_length=TOKEN_LENGTH, check_unused=False)

    # Send them an email
    failed = send_suitable_email(person, hash_value)

    if failed: # SMTPlib cannot send an email
        return False
    else:
        token = models.Token(person=person,
                             hash_value=hash_value,)
        return token

def popup_sign_in(request):
    """POST-only sign-in via the website. """

    if 'emailaddress' not in request.POST:
        return HttpResponse("Unauthorized access", status=401)

    # Process the sign-in
    # 1. Check if email address is valid based on a regular expression check.
    try:
        email = request.POST.get('emailaddress', '').strip()
        validate_email(email)
    except ValidationError:
        return HttpResponse("Invalid email address. Try again please.",
                            status=406)

    # 2. Is the user signed in already? Return back (essentially do nothing).
    # TODO: handle this case still. For now, just go through with the email
    #       again (but this is prone to abuse). Why go through? For the case
    #       when a user signs in, now the token is used. But if they reuse that
    #       token to sign in, but the session here is still active, they can
    #       potentially not sign in, until they clear their cookies.
    #if request.session.get('person_id', False):
    #    return HttpResponse("You are already signed in.", status=200)

    # 3A: a brand new user, or
    # 3B: a returning user that has cleared cookies/not been present for a while
    try:
        # Testing for 3A or 3B
        person = models.Person.objects.get(email=email)

        # Must be case 3B. If prior failure, then it is case 3A (see below).
        token = create_token_send_email_check_success(person)
        if token:
            token.save()
            return HttpResponse(("<i>Welcome back!</i> Please check your email,"
                     " and click on the link that we emailed you."), status=200)
        else:
            return HttpResponse(("An email could not be sent to you. Please "
                                 "ensure your email address is correct."),
                                status=404)

    except models.Person.DoesNotExist:
        # Case 3A: Create totally new user. At this point we are sure the user
        #          has never been validated on our site before.
        #          But the email address they provided might still be faulty.
        person = models.Person(is_validated=False,
                               display_name='Anonymous',
                               email=email)
        person.save()
        person.display_name = person.display_name + str(person.id)

        token = create_token_send_email_check_success(person)
        if token:
            person.save()
            token.person = person  # must overwrite the prior "unsaved" person
            token.save()
            return HttpResponse(("An account has been created for you, but must"
                                 " be actived. Please check your email and "
                                 "click on the link that we emailed you."),
                                status=200)
        else:
            # ``token`` will automatically be forgotten when this function
            # returns here. Perfect!
            person.delete()
            return HttpResponse(("An email could NOT be sent to you. Please "
                "ensure your email address is valid."), status=404)


def add_new_word(part1, part2, person):
    """
    Does the work of adding a new quiz to the database.
    """
    part1 = part1.strip()
    part2 = part2.strip()

    # Avoid a silly corner case
    if part1 == '' and part2 == '':
        part1 = 'pech'
        part2 = 'bad luck'


    pair, created = models.WordItem.objects.get_or_create(part1=part1,
                                                          part2=part2,
                                                          person=person)

    worditem = models.QuizWordItem(worditem=pair,
                                   person=person,
                                   counts_wrong=0,
                                   counts_right=0)

    return created

def get_next_quiz_pair(quiz, person):
    """
    Returns the next word to quiz.
    Uses a sliding scale to determine which words to return. Weakest words are
    always preferencially returned
    """
    words = []#models.WordItem.objects.all()
    lowest = models.QuizWordItem.objects.filter(person=person,
                                                accuracy__lt=0.01)
    words.extend(lowest)
    if len(words) < 5:
        middle = models.QuizWordItem.objects.filter(person=person,
                                                    accuracy__lt=0.51)
        words.extend(middle)

    if len(words) < 5:
        upper = models.QuizWordItem.objects.filter(person=person,
                                                   accuracy__lt=0.81)
        words.extend(upper)

    if len(words) < 5:
        top = models.QuizWordItem.objects.filter(person=person,
                                                 accuracy__lt=0.91)
        words.extend(top)

    if len(words) < 5:
        highest = models.QuizWordItem.objects.filter(person=person,
                                                     accuracy__lt=1.01)
        words.extend(highest)

    # Give the lower accuracy words a higher probability of being picked
    words.extend(lowest)
    words.extend(lowest)
    words.extend(lowest)
    words.extend(middle)
    worditems = [item.worditem for item in words]

    if words:
        return worditems[random.randint(0, len(words)-1)]
    else:
        return None

def add_word_HTML(request):
    """
    Adds a new word via the website
    """
    person = models.Person.objects.filter(id=request.session.get('person_id',
                                                                 None))
    words = models.WordItem.objects.all()
    extra_info = ''
    if request.POST and len(person)==1:
        part1 = request.POST.get('part1', None)
        part2 = request.POST.get('part2', None)
        add_new_word(part1, part2, person[0])
        extra_info = 'That new pair of words/phrases was successfully added.'
        # continue on as if a GET request

    # This is a GET request
    enabled = hide_sign_in = False
    if len(person)>0:
        enabled = person[0].is_validated
        hide_sign_in = True

    context = {'extra_info': extra_info,
               'enabled': enabled,
               'words': words,
               'hide_sign_in': hide_sign_in}
    return render(request, 'vocab/add-new-word.html', context)

def quiz_HTML(request, hashvalue=None, action=None):
    """
    When the quiz is started, the user is directed to a hash.

    That page is rendered with the first quiz question, which also has links
    to action =
    "1" to the left swipe   (go back to prior question)
    "2" to the right swipe  (go to the next question)
    "3" up swipe            (show me the answer)
    "4" down swipe          (I'm done: show me my score)
    "5"                     (resume with the question whose answer was revealed)

    Depending on the action that the user takes (1, 2, 3), the user's
    scores are tracked and then the next WordItem is shown to the user to
    continue the quz.

    If action 4 is taken the quiz is terminated.
    """
    person = models.Person.objects.filter(id=request.session.get('person_id',
                                                                     None))
    if len(person) == 0:
        return HttpResponseRedirect(reverse('add_word_HTML'))
    else:
        person = person[0]

    if hashvalue is None:
        hashvalue = ''
    else:
        hashvalue = hashvalue.strip()
    quiz = models.Quiz.objects.filter(quiz_hash=hashvalue)


    # Is this an existing quiz?
    if quiz:
        quiz = quiz[0]

    else:
        # Start a new quiz, and return the user back here
        action = ''
        quiz = models.Quiz(quiz_hash=get_quiz_hash(), person=person)
        quiz.save()
        return HttpResponseRedirect(reverse('quiz_HTML',
                                            kwargs={'hashvalue': quiz.quiz_hash,
                                                    'action': '2'}))

    try:
        pair_id = quiz.quiz_seq[quiz.currentitem]
        pair = models.WordItem.objects.filter(id=pair_id)[0]
        show_answer = False
    except IndexError:
        # This intentionally occurs when a new quiz is started that is empty.
        # Set action = '2' (it will liklely be that already), and continue on.
        # IF the assertion occurs, it is in the corner case when a word was
        # tested and has been deleted from the database. At least that is how
        # I have come to a failed assertion once in the past.
        assert(action == '2')

    # Does the user want to take one of the 4 actions mentioned above?
    if action == '1':
        # Get the prior item in the sequence; clamping at zero.
        # Going backwards does not alter the wrong/right count on the word.
        quiz.currentitem = max(0, quiz.currentitem-1)
        pair_id = quiz.quiz_seq[quiz.currentitem]
        pair = models.WordItem.objects.filter(id=pair_id)[0]
        quiz.save()
        return HttpResponseRedirect(reverse('quiz_HTML',
                                            kwargs={'hashvalue': hashvalue,
                                                    'action': ''}))

    elif action == '2':

        if quiz.currentitem - (quiz.n_words_asked-1) < 0:
            # If we are in the middle of a quiz; so return the next word from
            # the sequence.
            pair_id = quiz.quiz_seq[quiz.currentitem+1]
            pair = models.WordItem.objects.filter(id=pair_id)[0]
            quiz.currentitem += 1
        else:
            # or, as long as the user wants to keep going, add a new word
            # onto the quiz. Show this WordItem ``pair`` as the next quiz.
            pair = get_next_quiz_pair(quiz, person)

            quiz_seq = quiz.quiz_seq
            quiz_seq.append(pair.id)
            quiz.words_asked = json.dumps(quiz_seq)
            # Also, the assumption is the person got the prior answer correct if
            # they are clicking to move onto the "Next" quiz item.
            correct = quiz.correct
            correct.append(1)
            quiz.words_correct_first_time = json.dumps(correct)
            quiz.currentitem = len(quiz_seq) - 1

            worditem = models.QuizWordItem.objects.filter(worditem=pair,
                                                          person=person)[0]
            worditem.counts_right += 1
            worditem.save()

        # Parts common to both branches above:
        quiz.save()

        return HttpResponseRedirect(reverse('quiz_HTML',
                                                kwargs={'hashvalue': hashvalue,
                                                        'action': ''}))

    elif action == '3':
        # The user wants to see the answer. This counts against them.
        correct = quiz.correct
        correct[quiz.currentitem] = 0
        quiz.words_correct_first_time = json.dumps(correct)
        quiz.save()

        worditem = models.QuizWordItem.objects.filter(worditem=pair,
                                                      person=person)[0]


        worditem.counts_wrong += 1
        worditem.counts_right -= 1
        worditem.save()

        show_answer = True

    elif action == '4':
        # Stop the quiz. Show the user their results.
        words = models.WordItem.objects.filter(pk__in=quiz.quiz_seq)
        worddict = {}
        for item in words:
            worddict[item.pk]=item
        answers = []
        for item in quiz.quiz_seq:
            answers.append(worddict[item])

        pair = None
        context = {'answers': answers,
                   'quiz': quiz,
                   'correct': quiz.correct}
        return render(request, 'vocab/answers.html', context)

    elif action == '5':
        pass

    context = {'extra_info': hashvalue,
               'word_item': pair,
               'show_answer': show_answer,
               'quiz': quiz}
    return render(request, 'vocab/quiz.html', context)

def get_quiz_hash(token_length=TOKEN_LENGTH, no_lowercase=True,
                  check_unused=True):
    """Creates random length tokens from unmistakable characters."""
    choices = 'ABCEFGHJKLMNPQRSTUVWXYZ'
    if not(no_lowercase):
        choices += 'abcdefghjkmnpqrstuvwxyz'

    hashval = ''.join([random.choice(choices) for i in range(token_length)])
    if check_unused:
        try:
            models.Quiz.objects.get(quiz_hash=hashval)
        except models.Quiz.DoesNotExist:
            return hashval
        # It will repeat at this point
    else:
        return hashval