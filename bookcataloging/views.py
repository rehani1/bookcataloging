from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpResponse
from .models import UserProfile

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
    profile, created = UserProfile.objects.get_or_create(user=request.user,
    defaults=
    {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }
    )
    user_role = get_role(request)

    context = {'profile': profile,
    'user_role': user_role}
    
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        print(profile.profile_picture)
        return redirect('bookcataloging:profile')

    return render(request, 'bookcataloging/profile.html', context)

