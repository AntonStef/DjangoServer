from django.test import TestCase

# Create your tests here.

from ..models import Author, Book, Genre, BookInstance
from django.contrib.auth.models import User
import datetime


class AuthorModelTest(TestCase):
    # setUpTestData - вызывается каждый раз перед запуском теста
    # на уровне настройки всего класса. Запускается 1 раз.
    # setUp - каждая функция тестирования будет получать
    # "свежую" версию данных объектов, то есть для каждого теста (def)
    # будет вызываться заново setUp и создаваться новые объекты

    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        Author.objects.create(first_name='Big', last_name='Bob')
        # input()

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals(field_label, 'first name')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(field_label, 'date of birth')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEquals(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = '%s, %s' % (author.last_name, author.first_name)
        self.assertEquals(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        #This will also fail if the urlconf is not defined.
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')

# сначала выполняются тесты для BookInstanceModelTest
# потом для BookModelTest
# тупо из-за сортировки по алфавитному порядку
# поэтому сначала создаются объекты в BookInstanceModelTest
# а потом в BookModelTest
# отсюда идет привязка к конкретным id ля Author и Book
class BookModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # почему предыдщий автор записанный в базу (Big Bob) не доступен
        # и приходится создавать нового при этом новый автор имеет id=2
        #Set up non-modified objects used by all test methods
        author = Author.objects.create(first_name='Maks', last_name='Devis')
        # print(Author.objects.all()[0].id)
        # input()
        # author = Author.objects.get(id=3)
        summary = 'It is the best book'
        isbn = '0112345678987'
        Book.objects.create(title='Super Man', author=author,
                            summary=summary, isbn=isbn)
        # print(2)
        # input()

    def test_title_label(self):
        book = Book.objects.get(id=2)
        field_label = book._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_summary_label(self):
        book = Book.objects.get(id=2)
        field_label = book._meta.get_field('summary').verbose_name
        self.assertEquals(field_label, 'summary')

    def test_isbn_label(self):
        book = Book.objects.get(id=2)
        field_label = book._meta.get_field('isbn').verbose_name
        self.assertEquals(field_label, 'ISBN')

    def test_title_summary_isbn_max_length(self):
        book = Book.objects.get(id=2)
        max_length = book._meta.get_field('title').max_length
        self.assertEquals(max_length, 200)
        max_length = book._meta.get_field('isbn').max_length
        self.assertEquals(max_length, 13)
        max_length = book._meta.get_field('summary').max_length
        self.assertEquals(max_length, 1000)

    def test_author_name_is_last_name_comma_first_name(self):
        book = Book.objects.get(id=2)
        author = Author.objects.get(id=3)
        expected_author_name = '%s, %s' % (book.author.last_name, book.author.first_name)
        self.assertEquals(expected_author_name, str(author))
        expected_book_name = '%s' % (book.title, )
        self.assertEquals(expected_book_name, str(book))

    def test_get_absolute_url(self):
        book = Book.objects.get(id=2)
        #This will also fail if the urlconf is not defined.
        self.assertEquals(book.get_absolute_url(), '/catalog/book/2')


# сначала выполняются тесты для BookInstanceModelTest
# потом для BookModelTest
# тупо из-за сортировки по алфавитному порядку
# поэтому сначала создаются объекты в BookInstanceModelTest
# а потом в BookModelTest
# отсюда идет привязка к конкретным id ля Author и Book
class BookInstanceModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(title='Book Title', summary='My book summary',
                                        isbn='ABCDEFG', author=test_author)

        #Создание жанра Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Присвоение типов many-to-many напрямую недопустимо
        # test_book.genre = genre_objects_for_book
        test_book.save()

        #Создание объекта BookInstance для для пользователя test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
                                                              due_back=return_date, status='o')
        # print(1)
        # input()

    def test_imprint_status_isbn_max_length(self):
        book_instance = BookInstance.objects.all()[0]
        max_length = book_instance._meta.get_field('imprint').max_length
        self.assertEquals(max_length, 200)

        max_length = book_instance._meta.get_field('status').max_length
        self.assertEquals(max_length, 1)

    def test_status_help_text(self):
        book_instance = BookInstance.objects.all()[0]
        help_text = book_instance._meta.get_field('status').help_text
        self.assertEquals(help_text, 'Book availability')
