from django.shortcuts import render
from .models import *
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# render - функция которая генерирует HTML-файлы при помощи
# шаблонов страниц и соотвествующих данных


# Create your views here.
# декоратор для аутентификации пользователя
# работает для методов
@login_required
def index(request):
    """
    Функция отображения для домашней страницы сайта.
    """
    # Генерация "количеств" некоторых главных объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Доступные книги (статус = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # Метод 'all()' применен по умолчанию.

    # Получить жанры, которые содержат ЖАС без учета регистра
    num_genre_my = Genre.objects.filter(name__icontains='ЖАС')
    # Получить книги к Genre которые содержат гарри без учета регистра
    num_books_my = Book.objects.filter(title__icontains='ГарРи')

    # добавдяем анализ сессии
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_genre_my': num_genre_my, 'num_books_my': num_books_my, 'num_visits': num_visits},
    )


# generic.ListView - чотбы выводился как список объектов
# Это всё! Обобщенное отображение выполнит запрос к базе данных, получит все записи заданной модели (Book),
# затем отрендерит (отрисует) соответствующий шаблон,
# расположенный в /locallibrary/catalog/templates/catalog/book_list.html
# если не указать queryset или не переопределить метод get_context_data,
# то вернуться все записи Book.objects.all()
class BookListView(LoginRequiredMixin, generic.ListView):
    # указываем куда перенаправить пользователя если он не аутентифицирован
    login_url = 'login'
    # куда сделать перенаправление после авторизации redirect_field_name == next в шаблоне
    # но мы этого не указываем поскольку в самой шаблоне мы
    # поставили метку next и request.path что в случае успешной авторизации кидает нас обратно на последнюю страницу
    # redirect_field_name = 'books'
    model = Book
    paginate_by = 4

    # ваше собственное имя переменной контекста в шаблоне
    context_object_name = 'book_list'
    # Получение 5 книг, содержащих слово 'war' в заголовке
    # queryset = Book.objects.filter(title__icontains='СИЯ')
    queryset = Book.objects.all()
    # Определение имени вашего шаблона и его расположения
    template_name = 'book_list.html'

    # переопределнием методов в классах отображения
    # можно переопределить метод родительского класса по получения списка queryset
    def get_queryset(self):
        # return Book.objects.filter(title__icontains='СИЯ')
        return Book.objects.all()

    # переопределение пеередоваемоего контекста в шаблон
    def get_context_data(self, **kwargs):
        # В первую очередь получаем базовую реализацию контекста
        context = super(BookListView, self).get_context_data(**kwargs)
        # Добавляем новую переменную к контексту и иниуиализируем ее некоторым значением
        context['some_data'] = 'Книги просто отпадные'
        return context


# Это всё! Все что вам надо теперь сделать это создать шаблон
# с именем /locallibrary/catalog/templates/catalog/book_detail.html,
# а отображение передаст ему информацию из базы данных для определенной записи Book,
# выделенной при помощи URL-преобразования.
class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 2

    # куда пересылать если пользователь не авторизован
    login_url = 'login'
    # куда отправлять если авторизован
    # redirect_field_name = 'redirect_to'


    # ваше собственное имя переменной контекста в шаблоне
    context_object_name = 'author_list'
    # 1 вариант получить queryset
    queryset = Author.objects.all()
    # Определение имени вашего шаблона и его расположения
    template_name = 'author_list.html'

    # второй вариант получить queryset
    # переопределнием методов в классах отображения
    # можно переопределить метод родительского класса по получения списка queryset
    def get_queryset(self):
        # return Book.objects.filter(title__icontains='СИЯ')
        return Author.objects.all()

    # переопределение пеередоваемоего контекста в шаблон
    def get_context_data(self, **kwargs):
        # В первую очередь получаем базовую реализацию контекста
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # Добавляем новую переменную к контексту и иниуиализируем ее некоторым значением
        context['some_data'] = 'Авторы конечно красавцы'
        return context


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    context_object_name = 'bookinstance_list'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllLoanedBooksForLibrarianView(PermissionRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    # если не указать context_object_name, то он будет по умолчанию название модели + list
    context_object_name = 'bookinstance_list_on_loan'
    template_name = 'catalog/bookinstance_all_list_borrowed.html'
    # указываем разрешения
    permission_required = ('catalog.can_check_all_borrowed_books', )
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
