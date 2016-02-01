from django.template.defaulttags import register

@register.filter
def index(List, i):
    return List[int(i)]