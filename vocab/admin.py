from django.contrib import admin
from .models import WordItem, Quiz, Person, Token, Tag

class WordItemAdmin(admin.ModelAdmin):
    list_display = ('part1', 'part2', 'datetime', 'person', 'answers',
                    'counts_wrong', 'counts_right')
    list_display_links = list_display

class QuizAdmin(admin.ModelAdmin):
    list_display = ('when_started', 'when_ended', 'quiz_hash', 'person')
    list_display_links = list_display

class PersonAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'email', 'is_validated')
    list_display_links = list_display

class TokenAdmin(admin.ModelAdmin):
    list_display = ('person', 'was_used', 'time_used')
    list_display_links = list_display

#class QuizWordItemAdmin(admin.ModelAdmin):
#    list_display = ('person', 'worditem', 'counts_wrong', 'counts_right',
#                    'lastquizzed', 'accuracy')
#    list_display_links = list_display

class TagAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'slug', 'description', )
    list_display_links = list_display

admin.site.register(Tag, TagAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(WordItem, WordItemAdmin)
admin.site.register(Quiz, QuizAdmin)
