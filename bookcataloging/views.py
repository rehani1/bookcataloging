from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponse
from .models import UserProfile, Book, BookReview, Collections
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from django.db import models


def get_role(request):
    user_role = ''
    if request.user.is_authenticated: 
        if request.user.groups.filter(name='Librarian').exists():
            user_role = 'Librarian'
        elif request.user.groups.filter(name='Patron').exists():
            user_role = 'Patron'

    return user_role


def edit_collection(request, collection_id):
    collection = get_object_or_404(Collections, id=collection_id)
    user_role = get_role(request)
    
    if request.user != collection.owner and user_role != "Librarian":
        return redirect('bookcataloging:collections')
    
    if request.method == 'POST': # edits the collection
        if 'save_collection' in request.POST:
            collection.name = request.POST.get('name')
            collection.description = request.POST.get('description', '')
            if user_role == "Librarian":
                collection.is_public = request.POST.get('is_public') != 'on'
            collection.save()
            return redirect('bookcataloging:collections')
    
    context = {
        'collection': collection,
        'user_role': user_role,
    }
    return render(request, 'bookcataloging/edit_collection.html', context)


def delete_collection(request, collection_id):
    collection = get_object_or_404(Collections, id=collection_id)
    user_role = get_role(request)
    
    if request.user != collection.owner and user_role != "Librarian":
        return redirect('bookcataloging:collections')
    
    if request.method == 'POST': # deletes the collection
        collection.delete()
        return redirect('bookcataloging:collections')
    
    return redirect('bookcataloging:collections')


def add_collection(request):
    user_role = get_role(request)
    if not request.user.is_authenticated:
        return redirect('bookcataloging:collections')
    
    if request.method == 'POST': # adds the collection
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'off'
        
        if name:
            try:
                Collections.objects.create(
                    name=name,
                    owner=request.user,
                    is_public=is_public,
                    description=description
                )
                return redirect('bookcataloging:collections')
            except Exception as e:
                print('error')
    context = {
        'user_role': user_role,
    }
    return render(request, 'bookcataloging/add_collection.html', context)


def collections_view(request):
    user_role = get_role(request)
    
    if request.method == 'POST' and 'create_collection' in request.POST:
        name = request.POST.get('collection_name')
        description = request.POST.get('collection_description', '')
        is_public = request.POST.get('is_public') == 'on'
        
        if name and request.user.is_authenticated:
            Collections.create_collection(
                name=name,
                owner=request.user,
                is_public=is_public,
                description=description
            )
            return redirect('bookcataloging:collections')
    
    if request.user.is_authenticated:
        collections = Collections.objects.filter(
            models.Q(is_public=True) | models.Q(owner=request.user)
        ).distinct()
    else:
        collections = Collections.objects.filter(is_public=True)
    
    context = {
        'user_role': user_role,
        'collections': collections,
    }
    return render(request, 'bookcataloging/collections.html', context)


def index_view(request):
    user_role = get_role(request)
    return render(request, 'bookcataloging/index.html', {'user_role': user_role})


def search_view(request):
    user_role = get_role(request)
    query = request.GET.get('query', '').strip()
    results = []

    if query:
        results = Book.objects.filter(title__icontains=query) # gets the search results from the query (book title)

    if request.method == 'POST': # when submitting the image change
        book_id = request.POST.get('book_id') # get by book id
        if book_id:
            book = Book.objects.get(id=book_id)
            if 'book_picture' in request.FILES:
                book.book_image = request.FILES['book_picture']
                book.save()
            else:
                print("No image file provided.")
        else:
            print("No book ID provided in the form.")

        return redirect(f"{request.path}?query={query}")

    context = {
        'query': query,
        'results': results,
        'user_role': user_role,
    }
    return render(request, 'bookcataloging/search.html', context)


def book_recs(request):
    popular_books = BookReview.get_popular_books()
    recommendations = BookReview.get_book_recommendations(request.user) if request.user.is_authenticated else []
    my_collections = Collections.get_my_collections(request.user) if request.user.is_authenticated else []

    return render(request, 'bookcataloging/home.html', {
        'popular_books': popular_books,
        'recommendations': recommendations,
        'my_collections': my_collections
    })


def profile_view(request):
    if not request.user.is_authenticated:
        return render(request, "bookcataloging/guest_profile.html")
    profile, created = UserProfile.objects.get_or_create(user=request.user,
    defaults=
    {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }
    )
    user_role = get_role(request)

    
    if request.method == 'POST':
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        return redirect('bookcataloging:profile')
    context = {'profile': profile,
    'user_role': user_role}
    

    return render(request, 'bookcataloging/profile.html', context)


def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        read_status = request.POST.get('read_status', 'false').lower() == 'true'
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        genre = request.POST.get('genre')

        try:
            Book.create_book(
                title=title,
                author=author,
                isbn=isbn,
                read_status=read_status,
                rating=rating if rating else None,
                review=review if review else None,
                genre=genre
            )
            return HttpResponse("Book added successfully.")
        except ValueError as e:
            return HttpResponse(str(e))

    return render(request, 'add_book.html')


@login_required
def add_or_update_review(request, book_id):
    book = Book.objects.get(id=book_id)
    review = BookReview.objects.filter(user=request.user, book=book).first()

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')
        read_status = request.POST.get('read_status', 'false').lower() == 'true'

        if review:
            review.rating = rating if rating else None
            review.review = review_text
            review.read_status = read_status
            review.save()
        else:
            BookReview.objects.create(
                user=request.user,
                book=book,
                rating=rating if rating else None,
                review=review_text,
                read_status=read_status
            )

        return redirect('book_detail', book_id=book.id)

    return render(request, 'add_or_update_review.html', {'book': book, 'review': review})

@login_required
def edit_profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('bookcataloging:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'bookcataloging/edit_profile.html', {'form': form})

def home_view(request):
    popular_books = []        
    collections = []          
    recommendations = []     
    context = {
        'popular_books': popular_books,
        'collections': collections,
        'recommendations': recommendations,
    }
    return render(request, 'bookcataloging/home.html', context)

def book_recommendations(request):
    user = request.user
    recommendations = BookReview.get_book_recommendations(user)

    author_recommendations = recommendations['author_recs']
    genre_recommendations = recommendations['genre_recs']
    general_recommendations = recommendations['general_recs']

    return render(request, 'bookcataloging/book_recs.html', {
        'author_recommendations': author_recommendations,
        'genre_recommendations': genre_recommendations,
        'general_recommendations': general_recommendations
    })


