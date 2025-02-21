from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView


# Create your views here.
class IndexView(TemplateView):
    template_name = "bookcataloging/index.html"

class AddBookView(TemplateView):
    template_name = "bookcataloging/add_book.html"

def book_recs(request):
    return render(request, 'bookcataloging/book_recs.html')
