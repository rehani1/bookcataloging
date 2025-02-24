from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse

def get_role(request):
    user_role = ''
    if request.user.is_authenticated: 
        if request.user.groups.filter(name='Librarian').exists():
            user_role = 'Librarian'
        elif request.user.groups.filter(name='Patron').exists():
            user_role = 'Patron'

    return user_role

def index_view(request):
    user_role = get_role(request)
    return render(request, 'bookcataloging/index.html', {'user_role': user_role})

def book_recs(request):
    user_role = get_role(request)
    return render(request, 'bookcataloging/book_recs.html', {'user_role': user_role})

def profile_view(request):
    user_role = get_role(request)
    return render(request, 'bookcataloging/profile.html', {'user_role': user_role})

