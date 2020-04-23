from django.test import TestCase

# Create your tests here.

from ..models import Author, BookInstance, Book, Genre
from django.urls import reverse

import datetime
from django.utils import timezone

from django.contrib.auth.models import User  # Необходимо для представления User как borrower
from django.contrib.auth.models import Permission # Required to grant the permission needed to set a book as returned.

import uuid


class AuthorListViewTest(TestCase):
    # перед тем как иммитировать get и post запросы необходимо авторизоавться

    # setUpTestData - вызывается каждый раз перед запуском теста
    # на уровне настройки всего класса. Запускается 1 раз.
    # setUp - каждая функция тестирования будет получать
    # "свежую" версию данных объектов, то есть для каждого теста (def)
    # будет вызываться заново setUp и создаваться новые объекты

    # для данного класса имеется 4 теста поэтому setUp будет вызываться 4 раза.


    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name='Surname %s' % author_num, )

    def setUp(self):
        # Создание пользователя
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

    # иммитация get-запроса и получения ответа resp
    # get-запрос можно сделать двумя путями
    # resp = self.client.get('/catalog/authors/') - генерируем через пярмой адрес
    # resp = self.client.get(reverse('authors')) - ченерируем адрес через имя

    # resp.context содержит много полезной информации которую мы передаем из view
    # в шаблон, а также различную служебную информацию по пагинации и другим параметрам.

    # сейчас эти тесты работают поскольку мы создаем пользователя и логинимся
    # при каждом тесте.
    # если мы не залогинимся тесты не будут работать поскольку AuthorListView наследуется от
    # LoginRequiredMixin, то есть наши запросы будет постоянно перенапрявлять 302 статус
    # на страницу с логированием, поскольку мы при тестировании не логинились

    def test_view_url_exists_at_desired_location(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get('/catalog/authors/')
        # print(resp)
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] is True)
        # сколько авторов выводится на конкретной странице пагинации
        self.assertTrue(len(resp.context['author_list']) == 3)
        # print(len(resp.context))

    def test_lists_all_authors(self):
        login = self.client.login(username='testuser1', password='12345')
        # Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] is True)
        self.assertTrue(len(resp.context['author_list']) == 3)
        # print(resp.context)


class LoanedBookInstancesByUserListViewTest(TestCase):
    # setUpTestData - вызывается каждый раз перед запуском теста
    # на уровне настройки всего класса. Запускается 1 раз.
    # setUp - каждая функция тестирования будет получать
    # "свежую" версию данных объектов, то есть для каждого теста (def)
    # будет вызываться заново setUp и создаваться новые объекты

    def setUp(self):
        # Создание двух пользователей
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        # Создание книги
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG',
                                        author=test_author)
        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # Присвоение типов many-to-many напрямую недопустимо
        # print(genre_objects_for_book)
        # input()
        # test_book.genre = genre_objects_for_book
        test_book.save()

        # Создание 30 объектов BookInstance
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy % 5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'
            BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date,
                                        borrower=the_borrower, status=status)

    # проверка на то, что нас правильно перенаправляет на страницу логирования
    # в случае если мы не залогированы
    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    # а тут мы уже используем предвариательную авторизацию с последующем запросам
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))
        # print(resp)

        # Проверка что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка ответа на запрос
        self.assertEqual(resp.status_code, 200)

        # Проверка того, что мы используем правильный шаблон
        self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')

    # тест на списоп забронированных книг
    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Проверка, что изначально у нас нет книг в списке
        self.assertTrue('bookinstance_list' in resp.context)
        # всего 0 книг со статусом 'o'
        self.assertEqual(len(resp.context['bookinstance_list']), 0)

        # Берем первые 10 книг
        get_ten_books = BookInstance.objects.all()[:10]

        # выставляим их, что они взяты 'o' - on loan
        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # Проверка, что все забронированные книги в списке
        resp = self.client.get(reverse('my-borrowed'))
        # Проверка, что пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Проверка успешности ответа
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)
        # проверяем сколько у нас книг со статусом 'o'
        # их должно быть 5 поскольку, всего 30 книг, из них у каждого пользователя по 15
        # при это у каждого из пользователей 5 книг со статусом 'o' и 10 со статусом 'm'
        self.assertEqual(len(resp.context['bookinstance_list']), 5)

        # print(resp.context['bookinstance_list'])
        # input()

        # Подтверждение, что все книги (их 5) принадлежат testuser1 и взяты "на прокат"
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            # print(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    # проверка что книги отсартированы по дате от меньшей к большей
    # .order_by('due_back')
    def test_pages_ordered_by_due_date(self):

        # Изменение статуса на "в прокате"
        # все 30 книг указываем что в прокате
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Пользователь залогинился
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Подтверждение, что из всего списка показывается только 10 экземпляров
        # хотя у пользователя всего 15 книг со стасусом 'o'
        # выводят только 10 потому что соотвесвующий класс во views (LoanedBooksByUserListView)
        # имеет paginate_by = 10
        self.assertEqual(len(resp.context['bookinstance_list']), 10)

        # проверка что книги отсартированы по дате от меньшей к большей
        # .order_by('due_back')
        last_date = 0
        for copy in resp.context['bookinstance_list']:
            # print(copy.due_back)
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)

class RenewBookInstancesViewTest(TestCase):
    # здесь мы не просто создаем пользователей для логирования
    # но и ещё даем права на доступ

    def setUp(self):
        #Создание пользователя
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        # права на доступ редактирование книг
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        # просмотра всех зарегистрированных книг
        permission = Permission.objects.get(name='Check all borrowed books')
        test_user2.user_permissions.add(permission)
        # print(test_user2.user_permissions)
        test_user2.save()

        # проверим всели права получил testuser2
        permissions = Permission.objects.filter(user=test_user2)
        # print(permissions)

        #Создание книги
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
        self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',
                                                              due_back=return_date, borrower=test_user1, status='o')

        #Создание объекта BookInstance для для пользователя test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016',

                                                              due_back=return_date, borrower=test_user2, status='o')
    # проверка на то, что тебя перебрасывает если ты не авторизовался
    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        # print(resp.url.startswith('/accounts/login/'))
        # print(resp.url)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))
        # input()

    # проверка на то, что если ты авторизовался, тебя не пустит посокльку нет прав на доступ
    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))
        # print(resp)
        # print(resp.status_code)
        # input()

    # когда логинимся пользователем у которого есть права на исправление статуса
    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk, }))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(resp.status_code, 200)

    # когда пользователь имеет права на редактирование и может редактировать дату заема книги
    # для которой он не является заемщиком --> библиотекарь меняют дату для члена библиотеки
    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(resp.status_code, 200)

    # генерируем случай uuid для книги, ее естественно нет и должно вывалиться в ошибку
    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()  # unlikely UID to match our bookinstance!
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid, }))
        # print(resp)
        self.assertEqual(resp.status_code, 404)
        # input()
    # проверка на корректность использования шаблона
    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')

    # очень классная проверка - мне нравится
    # мы берем и проверяем правильно ли у нас иннициализирована дата предлогаемая
    # для переноса брони, мы ее устанавливали во views.
    # form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })
    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        # Заметьте, что мы имеем возможность получить доступ к начальному
        # значению из поля формы resp.context['form'].initial['renewal_date'].
        # print(resp.context['form'])
        # input()
        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future)

        # а также можем получить доуступ к атрибутам (help_text, label) поля конкретного (renewal_date)
        # через указание fields
        # print(resp.context['form'].fields['renewal_date'].help_text)
        # саму форму мы описывали в forms
        # renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).",
        #                                    label='New date')
        self.assertEqual(resp.context['form'].fields['renewal_date'].help_text,
                         'Enter a date between now and 4 weeks (default 3).')
        self.assertEqual(resp.context['form'].fields['renewal_date'].label, 'New date')

    # отправляем пост запрос для изменения даты брони
    # первым атрибутам мы указываем куда шлем и указываем id конркетнойкниги
    # вторым атрибутом {'renewal_date': valid_date_in_future} - мы передаем значение
    # в конце нам перебрасывает на страницу со всеми заброннированными книгами
    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='12345')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': valid_date_in_future})
        self.assertRedirects(resp, reverse('all-borrowed'))

    # проверка что выводится правильно сообщение в случае если дата взята старая для продления брони -
    # а именно вчерашний день
    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='12345')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': date_in_past})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')

    # проверка что выводится правильно сообщение в случае если дата взята больше чем положено
    # для продления брони - а именно вперед больше чем на 4 недели
    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='12345')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': invalid_date_in_future})
        # код у запроса должен быть 200,
        # поскольку все работает просто форма не прошла валидацию
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')


class AuthorCreateTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(first_name='Christian', last_name='Surname', )

        # Создание двух пользователей
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        # права на
        permission = Permission.objects.get(name='Access for update Author')
        test_user2.user_permissions.add(permission)
        test_user2.save()

    # проверка на то, что тебя перебрасывает если ты не авторизовался
    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('author_create'))
        self.assertEqual(resp.status_code, 302)

        # 1 вариант
        # self.assertTrue(resp.url.startswith('/accounts/login/'))
        # 2 вариант
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/author/create/')

    # когда логинимся пользователем у которого есть права на добавление автора
    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author_create'))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(resp.status_code, 200)

    # когда логинимся пользователем у которого нет прав на добавление автора
    def test_logged_in_without_permission_borrowed_book(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('author_create'))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(resp.status_code, 403)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author_create'))
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'catalog/author_form.html')

    # подключаемся к форме через отображение
    def test_initial_birth_death(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author_create'))

        self.assertEqual(resp.context['form'].initial['date_of_death'], '12/10/1600')
        self.assertEqual(resp.context['form'].initial['date_of_birth'], '12/10/1500')

    # подключаемся к форме через отображение, а потом к полям модели (потому что форма на основе модели)
    # но инициализируется все в  AuthorCreate in views
    def test_max_length_last_name_first_name(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author_create'))

        self.assertEqual(resp.context['form'].fields['first_name'].max_length, 100)
        self.assertEqual(resp.context['form'].fields['last_name'].max_length, 100)

    def test_date_of_death_label(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('author_create'))

        self.assertEqual(resp.context['form'].fields['date_of_death'].label, 'Died')

    # проверка валидации что выводится сообщение в случае если используется неверный формат для даты
    # например не 22/04/2020 а 22.04.2020 то есть не формат для объекта класса datetime
    def test_form_invalid_date_of_birth_death(self):
        login = self.client.login(username='testuser2', password='12345')
        invalid_date_birth = '22.04.2020'
        invalid_date_death = '22.04.1605'
        resp = self.client.post(reverse('author_create'),
                                {'date_of_birth': invalid_date_birth,
                                 'date_of_death': invalid_date_death})
        # код у запроса должен быть 200,
        # поскольку все работает просто форма не прошла валидацию
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'date_of_birth', 'Enter a valid date.')
        self.assertFormError(resp, 'form', 'date_of_death', 'Enter a valid date.')
