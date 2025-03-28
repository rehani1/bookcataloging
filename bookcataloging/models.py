from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    description = models.TextField(blank=True, default="A passionate book enthusiast.")
    quote = models.CharField(
        max_length=255, 
        blank=True, 
        default='"I solemnly swear that I am up to no good" - Harry Potter'
    )
    books_read = models.PositiveIntegerField(default=0)
    pages_read = models.PositiveIntegerField(default=0)
    friends = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Book(models.Model):
    GENRE_CHOICES = [
        ('fantasy', 'Fantasy'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('science_fiction', 'Science Fiction'),
        ('non_fiction', 'Non-fiction'),
        ('historical', 'Historical'),
        ('thriller', 'Thriller'),
    ]

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    review = models.TextField()
    read_status = models.BooleanField()
    book_image = models.ImageField(upload_to='book_pics/', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books', null=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title

    @classmethod
    def get_book_by_title(cls, title):
        return cls.objects.filter(title=title)

    @classmethod
    def get_books_by_author(cls, author):
        return cls.objects.filter(author=author)

    @classmethod
    def get_books_by_genre(cls, genre):
        return cls.objects.filter(genre=genre)

    @classmethod
    def get_reviews_for_book(cls, title):
        return cls.objects.filter(title=title).values('review')

    @classmethod
    def create_book(cls, title, author, isbn, genre, user, read_status=False, rating=None, review=None, series=None):
        if cls.objects.filter(isbn=isbn).exists():
            raise ValueError("A book with this ISBN already exists.")

        return cls.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            read_status=read_status,
            rating=rating,
            review=review,
            genre=genre,
            series=series,
            user=user
        )

    def get_reviews(self):
        return self.bookreview_set.all()

    def get_average_rating(self):
        reviews = self.bookreview_set.all()
        total_rating = sum([review.rating for review in reviews if review.rating is not None])
        return total_rating / len(reviews) if reviews else None


class BookReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    read_status = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"

    @classmethod
    def get_book_recommendations(cls, user):
        books_by_fav_authors = Book.objects.filter(
            id__in=cls.objects.filter(
                user=user,
                rating__gte=3
            ).values('book__author').annotate(
                num_books_read=Count('book'),
            ).filter(
                num_books_read__gte=3
            ).values('book')
        )

        books_by_genre = Book.objects.filter(
            genre__in=BookReview.objects.filter(
                user=user,
                rating__gte=4
            ).values('book__genre').annotate(
                num_reads=Count('book')
            ).filter(num_reads__gte=5).values('book__genre')
        ).filter(rating__gte=4)

        popular_books = Book.objects.filter(
            bookreview__rating__gte=4
        ).annotate(
            num_ratings=Count('bookreview')
        ).filter(
            num_ratings__gte=3
        )

        recommendations = set(books_by_fav_authors) | set(books_by_genre) | set(popular_books)

        return recommendations


class Collections(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book, related_name='collections')
    is_public = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_collection(cls, name, owner, is_public=True):
        return cls.objects.create(name=name, owner=owner, is_public=is_public)

    def add_book(self, book):
        self.books.add(book)
