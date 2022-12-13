from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'
# Описать класс AboutAuthorView для страницы about/author
 

class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
# Описать класс AboutTechView для страницы about/tech
