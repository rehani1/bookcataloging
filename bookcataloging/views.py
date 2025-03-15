from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpResponse
from .models import UserProfile, Book, BookReview
from django.contrib.auth.decorators import login_required

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
    user_role = get_role(request)
    return render(request, 'bookcataloging/book_recs.html', {'user_role': user_role})

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


