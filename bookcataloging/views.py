from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse

def index_view(request):
    user_role = ''
    if request.user.is_authenticated: 
        if request.user.groups.filter(name='Librarian').exists():
            user_role = 'Librarian'
        elif request.user.groups.filter(name='Patron').exists():
            user_role = 'Patron'
            
    context = {
        'user_role': user_role,
    }

    return render(request, 'bookcataloging/index.html', context)

def book_recs(request):
    return render(request, 'bookcataloging/book_recs.html')

def profile_view(request):
    return render(request, 'bookcataloging/profile.html')

