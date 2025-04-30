from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponse
from .models import UserProfile, Book, BookReview, Collections, Request, BookRating
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models import Count 
from random import sample


def get_role(request):
    user_role = ''
    if request.user.is_authenticated: 
        if request.user.groups.filter(name='Librarian').exists():
            user_role = 'Librarian'
        elif request.user.groups.filter(name='Patron').exists():
            user_role = 'Patron'

    return user_role

def view_patrons(request):
    user_role = get_role(request)

    users_group = Group.objects.get(name="Patron")
    users = users_group.user_set.all()
    context = {
        'user_role': user_role,
        'users': users,
    }
    return render(request, 'bookcataloging/view_patrons.html', context)

def upgrade_patrons(request, patron_id):
    user_role = get_role(request)

    user = get_object_or_404(User, id=patron_id)

    patron_group = Group.objects.get(name='Patron')
    if patron_group in user.groups.all():
        user.groups.remove(patron_group)

    librarian_group, created = Group.objects.get_or_create(name='Librarian')
    user.groups.add(librarian_group)
    
    return redirect('bookcataloging:view_patrons')
def edit_book(request, book_id):
    genre_choices = Book.GENRE_CHOICES
    book = get_object_or_404(Book, id=book_id)
    user_role = get_role(request)
    
    if user_role != "Librarian":
        return redirect('bookcataloging:index')
    
    if request.method == 'POST':
        if 'save_book' in request.POST:
            book.title = request.POST.get('title')
            book.author = request.POST.get('Author')
            book.rating = request.POST.get('Rating')
            book.review = request.POST.get('Review')
            book.series = request.POST.get('Series')
            book.genre = request.POST.get('Genre')
            book.location = request.POST.get('Location')
            book.book_image = request.FILES.get('Image')
            book.save()
            return redirect('bookcataloging:index')
    
    context = {
        'book': book,
        'user_role': user_role,
        'genre_choices': genre_choices,
    }
    return render(request, 'bookcataloging/edit_book.html', context)

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user_role = get_role(request)
    
    if user_role != "Librarian":
        return redirect('bookcataloging:index')
    
    if request.method == 'POST': 
        book.delete()
        return redirect('bookcataloging:index')
    
    return redirect('bookcataloging:index')

def add_book(request):
    user_role = get_role(request)
    genre_choices = Book.GENRE_CHOICES
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('Author')
        rating = request.POST.get('Rating')
        review = request.POST.get('Review')
        series = request.POST.get('Series')
        genre = request.POST.get('Genre')
        location = request.POST.get('Location')
        image = request.FILES.get('Image')
        if title:
            try:
                book = Book.objects.create(
                    title=title,
                    author=author,
                    review=review,
                    series=series,
                    genre=genre,
                    location=location,
                    book_image=image,
                    read_status=False,
                    user = request.user,
                )
                if rating:
                    BookRating.objects.create(
                        book=book,
                        user=request.user,
                        rating=rating
                    )
                return redirect('bookcataloging:index')
            except Exception as e:
                print(f'Error creating book: {e}')  # Print the actual error
    context = {
        'user_role': user_role,
        'genre_choices': genre_choices,
    }
    return render(request, 'bookcataloging/add_book.html', context)

def view_collection(request, collection_id):
    collection = get_object_or_404(Collections, id=collection_id)
    user_role = get_role(request)
    query = request.GET.get('query', '').strip()

    search_by = request.GET.get('search_by', 'title')

    context = {
        'collection': collection,
        'user_role': user_role,
        'search_by': search_by,
    }
    return render(request, 'bookcataloging/view_collection.html', context)

def search_collection(request, collection_id):
    collection = get_object_or_404(Collections, id=collection_id)
    user_role = get_role(request)
    query = request.GET.get('query', '').strip()
    search_by = request.GET.get('search_by', 'title')
    results = []

    if not query:
        results = collection.books.all()
    else: 
        if query:
            if search_by == 'title':
                results = collection.books.filter(title__icontains=query)
            elif search_by == 'author':
                results = collection.books.filter(author__icontains=query)
            elif search_by == 'genre':
                results = collection.books.filter(genre__iexact=query)
            else:
                results = collection.books.all()

    context = {
        'query': query,
        'results': results,
        'user_role': user_role,
        'search_by': search_by,
        'collection': collection,
    }
    return render(request, 'bookcataloging/search_collection.html', context)

def view_users(request, collection_id):
    collection = get_object_or_404(Collections, id=collection_id)
    user_role = get_role(request)
    context = {
        'collection': collection,
        'user_role': user_role,
    }
    return render(request, 'bookcataloging/view_users.html', context)
def request_collection(request, collection_id):
    collection = get_object_or_404(Collections, id=collection_id)
    if request.user.is_authenticated:
        Request.objects.get_or_create(user=request.user, collection=collection)
    return redirect('bookcataloging:collections')

def view_requests(request):
    user_role = get_role(request)
    pending_requests = Request.objects.filter(is_approved=False,pending=True).select_related('user', 'collection')
    context = {
        'pending_requests': pending_requests,
        'user_role': user_role,
    }
    return render(request, 'bookcataloging/view_requests.html', context)

def approve_request(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    req.is_approved = True
    req.save()
    req.pending = False
    req.collection.approved_users.add(req.user)
    req.collection.save()

    return redirect('bookcataloging:view_requests')

def delete_request(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    req.pending = False
    return redirect('bookcataloging:view_requests')


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

# class AddBookView(TemplateView):
#     template_name = "bookcataloging/add_book.html"

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
        is_public = request.POST.get('is_public') != 'on'

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
        collections = Collections.objects.all()
    else:
        collections = Collections.objects.filter(is_public=True)
    context = {
        'user_role': user_role,
        'collections': collections,
    }
    return render(request, 'bookcataloging/collections.html', context)

def request_access_to_collection(request, collection_id):
    collection = get_object_or_404(Collections, id=collection_id)
    # test
    return redirect('bookcataloging:collections')

def delete_book_from_collection(request, collection_id, book_id):
    collection = get_object_or_404(Collections, id=collection_id)
    book = get_object_or_404(Book, id=book_id)
    user_role = get_role(request)  
    
    if request.user != collection.owner and user_role != "Librarian":
        return redirect('bookcataloging:view_collection', collection_id=collection.id)

    collection.books.remove(book)
    return redirect('bookcataloging:view_collection', collection_id=collection.id)

def add_book_to_collection(request, collection_id):
    collection = get_object_or_404(Collections, id=collection_id)
    user_role = get_role(request)
    if request.method == 'POST':
        book_ids = request.POST.getlist('books')  
        books = Book.objects.filter(id__in=book_ids)

        private_books = books.filter(collections__is_public=False).distinct()
        if not private_books.exists():
            collection.books.add(*books)
            return redirect('bookcataloging:view_collection', collection_id=collection.id)
    private_book_ids = Book.objects.filter(collections__is_public=False).values_list('id', flat=True)
    available_books = Book.objects.filter(collections=None).distinct()
    
    context = {
        'collection': collection,
        'available_books': available_books,
        'user_role': user_role,
    }
    return render(request, 'bookcataloging/add_book_to_collection.html', context)


def index_view(request):
    user_role = get_role(request)
    search_by = request.GET.get('search_by', 'title')
    return render(request, 'bookcataloging/index.html', 
    {'user_role': user_role,
    'search_by': search_by,
    })


def search_view(request):
    user_role = get_role(request)
    query = request.GET.get('query', '').strip()
    search_by = request.GET.get('search_by', 'title')
    results = []

    if query:
        if search_by == "title":
            results = Book.objects.filter(title__icontains=query) # gets the search results from the query (book title)
        elif search_by == "author":
            results = Book.objects.filter(author__icontains=query)
        elif search_by == "genre":
            results = Book.objects.filter(genre__icontains=query)

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

        return redirect(f"{request.path}?query={query}&search_by={search_by}")

    context = {
        'query': query,
        'results': results,
        'user_role': user_role,
        'search_by': search_by, 
    }
    return render(request, 'bookcataloging/search.html', context)


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

    pending_requests = Request.objects.filter(
    user=request.user
    ).select_related('user', 'collection')
        
    if request.method == 'POST':
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        return redirect('bookcataloging:profile')
    context = {'profile': profile,
    'user_role': user_role,
    'pending_requests': pending_requests,
    }
    

    return render(request, 'bookcataloging/profile.html', context)


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
def add_book_rating(request, book_id):
    user_role = get_role(request)
    book = get_object_or_404(Book, id=book_id)
    existing_rating = BookRating.objects.filter(book=book, user=request.user).first()

    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        if rating_value and rating_value.isdigit() and 1 <= int(rating_value) <= 5:
            if existing_rating:
                existing_rating.delete()
            BookRating.objects.create(
                book=book,
                user=request.user,
                rating=int(rating_value)
            )
            return redirect('bookcataloging:index')
        
    context = {
    'book': book,
    'user_role': user_role,
    }

    return render(request, 'bookcataloging/add_book_rating.html', context)


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
    user_role = get_role(request)
    popular_books = BookRating.get_popular_books()
    if request.user.is_authenticated:
        recommendations = BookRating.get_book_recommendations(request.user)
        my_collections = Collections.get_my_collections(request.user)
    else:
        return render(request, 'bookcataloging/home.html', {'popular_books': popular_books,'user_role': user_role,})

    # recommendations = []
    if my_collections.exists():
        genre_tally = (
            Book.objects.filter(collections__in=my_collections)
                        .values('genre')
                        .annotate(total=Count('id'))
                        .order_by('-total')
        )
        if genre_tally:
            top_genre = genre_tally[0]['genre']       
            genre_pool = list(Book.objects.filter(genre=top_genre))
            recommendations = sample(genre_pool, k=min(3, len(genre_pool))) 
    if not recommendations:
        recommendations = BookRating.get_book_recommendations(request.user)
    
    context = {
        'popular_books': popular_books,
        'my_collections': my_collections,
        'recommendations': recommendations,
        'user_role': user_role,
    }
    return render(request, 'bookcataloging/home.html', context)


@login_required
def check_out_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if not book.checked_out:
        book.check_out_book(user=request.user)
    return redirect('bookcataloging:checked_out_books')


@login_required
def return_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.checked_out and book.checked_out_by == request.user:
        book.return_book()
    return redirect('bookcataloging:checked_out_books')


@login_required
def checked_out_books(request):
    user_role = get_role(request)
    books = Book.get_checked_out_books_by_user(request.user)
    context = {

        'books': books,
        'user_role': user_role,
    }
    return render(request, 'bookcataloging/checked_out_books.html', context)
