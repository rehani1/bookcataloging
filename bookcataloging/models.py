from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q

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
    review = models.TextField()
    read_status = models.BooleanField()
    book_image = models.ImageField(upload_to='book_pics/', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books', null=True)
    series = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    checked_out = models.BooleanField(default=False)
    checked_out_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True , related_name='checked_out_books')

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
        ratings = self.ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / ratings.count(), 2)
        return None

    def check_out_book(self, user):
        if not self.checked_out:
            self.checked_out = True
            self.checked_out_by = user
            self.save()

    def return_book(self):
        self.checked_out = False
        self.checked_out_by = None
        self.save()

    @classmethod
    def get_checked_out_books_by_user(cls, user):
        return cls.objects.filter(checked_out_by=user)


class BookRating(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_ratings')
    rating = models.IntegerField(choices=RATING_CHOICES)

    @classmethod
    def get_book_recommendations(cls, user):
        books_by_fav_authors = Book.objects.filter(
            id__in=BookRating.objects.filter(
                user=user,
                rating__gte=3
            ).values('book__author')
            .annotate(
                num_books_read=Count('book')
            )
            .values('book')
        )

        books_by_genre = Book.objects.filter(
            genre__in=BookRating.objects.filter(
                user=user,
                rating__gte=4
            ).values('book__genre')
            .annotate(
                num_reads=Count('book')
            )
            .values('book__genre')
        ).filter(ratings__rating__gte=4)

        recommendations = set(books_by_fav_authors) | set(books_by_genre)

        return recommendations

    @classmethod
    def get_popular_books(cls):
        popular_books = Book.objects.annotate(
            high_ratings=Count('ratings', filter=Q(ratings__rating__gte=4))
        ).filter(
            high_ratings__gte=3
        ).distinct()

        return popular_books

    class Meta:
        unique_together = ('book', 'user')


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

class Collections(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book, related_name='collections')
    is_public = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    description = models.TextField(blank=True, null=True)
    approved_users = models.ManyToManyField(User, related_name='approved_collections', blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_collection(cls, name, owner, approved_users, is_public=True, description=None):
        return cls.objects.create(
            name=name,
            owner=owner,
            is_public=is_public,
            description=description,
            approved_users=approved_users
        )

    def add_book(self, book):
        self.books.add(book)


    @classmethod
    def get_my_collections(cls, user):
        return Collections.objects.filter(owner=user)

class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collections, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} requested access to {self.collection.name}"
