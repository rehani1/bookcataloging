from django.test import TestCase
from .models import UserProfile, Book, BookReview, Collections
from django.contrib.auth.models import User


# Create your tests here.
class BookModelTest(TestCase):

    def setUP(self):
        self.user1 = User.objects.create_user(username="testuser", password="password123")
        self.user2 = User.objects.create_user(username="otheruser", password="54321")

        self.book1 = Book.objects.create_book(title="Night Watch", author="Terry Pratchett", genre="Fantasy")
        self.book2 = Book.objects.create_book(title="Guards! Guards!", author="Terry Pratchett", genre="Fantasy")
        self.book3 = Book.objects.create_book(title="And Then There Were None", author="Agatha Christie", genre="Mystery")
        self.book4 = Book.objects.create_book(title="Cards on the Table", author="Agatha Christie", genre="Mystery")
        self.book5 = Book.objects.create_book(title="Brave New World", author="Aldous Huxley", genre="Science Fiction")

        self.review1 = BookReview.objects.create(user=self.user1, book=self.book1, rating=5,
                                                 review="One of my favorite books!", read_status=True)

        self.review2 = BookReview.objects.create(user=self.user2, book=self.book4, rating=4,
                                                 review="Great mystery book.", read_status=True)

        self.review3 = BookReview.objects.create(user=self.user1, book=self.book5, rating=2,
                                                 review="Very confusing.", read_status=True)

        self.review4 = BookReview.objects.create(user=self.user2, book=self.book1, rating=3,
                                                 review="It was solid.", read_status=True)

    def test_create_book_object(self):
        """Test that the book was created with the appropriate values"""
        self.assertEqual(self.book1.title, "Night Watch")
        self.assertEqual(self.book1.author, "Terry Pratchett")
        self.assertEqual(self.book1.genre, "Fantasy")
        self.assertEqual(self.book1.rating, None)
        self.assertEqual(self.book1.review, None)
        self.assertEqual(self.book1.read_status, False)

    def test_book_exists(self):
        self.assertEqual(Book.objects.count(), 1)

    def test_get_book_by_title(self):
        """Test that get_book_by_title returns the correct book"""
        Book.get_book_by_title("Night Watch")
        self.assertIsNotNone(self.book)
        self.assertEqual(self.book1.title, "Night Watch")
        self.assertEqual(self.book1.author, "Terry Pratchett")

    def test_get_books_by_author(self):
        """Test that get_books_by_author returns correct books"""
        books = Book.get_books_by_author("Terry Pratchett")
        self.assertEqual(books.count(), 2)
        self.assertIn(self.book1, books)
        self.assertIn(self.book2, books)

    def test_get_books_by_genre(self):
        """Test that get_books_by_genre returns correct books"""
        books = Book.get_books_by_genre("Mystery")
        self.assertEqual(books.count(), 2)
        self.assertIn(self.book3, books)
        self.assertIn(self.book4, books)

    def test_get_reviews(self):
        """Test that get_reviews returns the correct reviews"""
        reviews = self.book1.get_reviews()
        self.assertEqual(reviews.count(), 2)
        self.assertIn(self.review1, reviews)
        self.assertIn(self.review4, reviews)

    def test_get_average_rating(self):
        """Test that get_average_rating returns the correct average"""
        avg_rating = self.book1.get_average_rating()
        self.assertEqual(avg_rating, (5 + 3) / 2)

        avg_rating_book2 = self.book2.get_average_rating()
        self.assertEqual(avg_rating_book2, 4)

        self.assertIsNone(self.book2.get_average_rating())

    def test_get_reviews_for_book(self):
        """Test that get_reviews_for_book returns the correct reviews by title"""
        reviews = list(Book.get_reviews_for_book("Night Watch"))
        self.assertEqual(len(reviews), 2)
        self.assertIn({'review': "One of my favorite books!"}, reviews)
        self.assertIn({'review': "It was solid."}, reviews)

        reviews_no_match = list(Book.get_reviews_for_book("Nonexistent Book"))
        self.assertEqual(len(reviews_no_match), 0)


class BookReviewModelTest(TestCase):
    def setUp(self):
        """Set up test data before each test"""
        self.user1 = User.objects.create_user(username="testuser", password="password123")
        self.user2 = User.objects.create_user(username="otheruser", password="password123")
        self.user3 = User.objects.create_user(username="somebody", password="password123")
        self.user4 = User.objects.create_user(username="anothersomebody", password="password123")

        self.book1 = Book.objects.create_book(title="Night Watch", author="Terry Pratchett", genre="Fantasy")
        self.book2 = Book.objects.create_book(title="Guards! Guards!", author="Terry Pratchett", genre="Fantasy")
        self.book3 = Book.objects.create_book(title="And Then There Were None", author="Agatha Christie", genre="Mystery")
        self.book4 = Book.objects.create_book(title="Cards on the Table", author="Agatha Christie", genre="Mystery")
        self.book5 = Book.objects.create_book(title="Brave New World", author="Aldous Huxley", genre="Science Fiction")
        self.book6 = Book.objects.create_book(title="Dune", author="Frank Herbert", genre="Science Fiction")
        self.book7 = Book.objects.create_book(title="Witches Abroad", author="Terry Pratchett", genre="Fantasy")
        self.book8 = Book.objects.create_book(title="Wyrd Sisters", author="Terry Pratchett", genre="Fantasy")
        self.book9 = Book.objects.create_book(title="Harry Potter and the Sorcerer's Stone", author="J.K. Rowling", genre="Fantasy")

        BookReview.objects.create(user=self.user1, book=self.book1, rating=4, review="Great book!", read_status=True)
        BookReview.objects.create(user=self.user1, book=self.book2, rating=4, review="Loved it!", read_status=True)
        BookReview.objects.create(user=self.user1, book=self.book7, rating=3, review="Good!", read_status=True)
        BookReview.objects.create(user=self.user1, book=self.book8, rating=5, review="Amazing!", read_status=True)

        BookReview.objects.create(user=self.user2, book=self.book3, rating=5, review="Best mystery!", read_status=True)
        BookReview.objects.create(user=self.user2, book=self.book4, rating=4, review="Really good!", read_status=True)
        BookReview.objects.create(user=self.user2, book=self.book6, rating=4, review="A masterpiece!", read_status=True)
        BookReview.objects.create(user=self.user2, book=self.book8, rating=5, review="Epic!", read_status=True)
        BookReview.objects.create(user=self.user2, book=self.book9, rating=5, review="Awesome!", read_status=True)

        BookReview.objects.create(user=self.user3, book=self.book3, rating=5, review="Awesome!", read_status=True)
        BookReview.objects.create(user=self.user4, book=self.book3, rating=4, review="Awesome!", read_status=True)

    def test_create_book_review(self):
        """Test that a BookReview instance is created correctly"""
        review = BookReview.objects.create(
            user=self.user1,
            book=self.book1,
            rating=5,
            review="Awesome book!",
            read_status=True
        )

        saved_review = BookReview.objects.get(id=review.id)
        self.assertEqual(saved_review.user, self.user1)
        self.assertEqual(saved_review.book, self.book1)
        self.assertEqual(saved_review.rating, 5)
        self.assertEqual(saved_review.review, "Awesome book!")
        self.assertTrue(saved_review.read_status)

    def test_book_recommendations(self):
        """Test that book recommendations are correctly generated"""
        recommendations = BookReview.get_book_recommendations(self.user)

        self.assertIn(self.book1, recommendations)
        self.assertIn(self.book2, recommendations)
        self.assertIn(self.book7, recommendations)
        self.assertIn(self.book8, recommendations)

        self.assertIn(self.book9, recommendations)
        self.assertIn(self.book1, recommendations)

        self.assertIn(self.book7, recommendations)
        self.assertIn(self.book3, recommendations)

        self.assertNotIn(Book.objects.create_book(title="Random Book", author="Unknown", genre="Unknown"),
                         recommendations)


class UserProfileTest(TestCase):
    def setUp(self):
        """Set up test user and profile before each test"""
        self.user = User.objects.create_user(username="pippi", password="socks123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            first_name="Pippi",
            last_name="Longstocking",
            description="An energetic reader!",
        )

    def test_user_profile_creation(self):
        """Test that the UserProfile instance is created correctly"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.first_name, "Pippi")
        self.assertEqual(self.profile.last_name, "Longstocking")
        self.assertEqual(self.profile.description, "An energetic reader!")
        self.assertFalse(self.profile.profile_picture)


class CollectionsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_create_book_and_auto_assign_collections(self):
        book = Book.create_book(
            title="The Fellowship of the Ring",
            author="J.R.R. Tolkien",
            isbn="9780618968633",
            genre="fantasy",
            user=self.user,
            series="The Lord of the Rings"
        )

        self.assertEqual(Book.objects.count(), 1)

        author_collection = Collections.objects.get(name="Books by J.R.R. Tolkien")
        self.assertIn(book, author_collection.books.all())

        series_collection = Collections.objects.get(name="Series: The Lord of the Rings")
        self.assertIn(book, series_collection.books.all())

        user_collection = Collections.objects.get(name="testuser's Collection")
        self.assertIn(book, user_collection.books.all())

    def test_create_collection(self):
        collection = Collections.create_collection(name="My Favs", owner=self.user)

        self.assertEqual(Collections.objects.count(), 1)
        self.assertEqual(collection.name, "My Favs")
        self.assertEqual(collection.owner, self.user)
        self.assertTrue(collection.is_public)

    def test_add_book_to_collection(self):
        book = Book.create_book(
            title="Dune",
            author="Frank Herbert",
            isbn="9780441172719",
            genre="science_fiction",
            user=self.user
        )

        collection = Collections.create_collection(name="Sci-Fi Books", owner=self.user)
        collection.add_book(book)
        self.assertIn(book, collection.books.all())
