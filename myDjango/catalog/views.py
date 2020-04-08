from django.shortcuts import render
from .models import *
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm, RenewBookModelForm

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author
from django.utils.translation import ugettext_lazy as _


# render - функция которая генерирует HTML-файлы при помощи
# шаблонов страниц и соотвествующих данных


# Create your views here.
# декоратор для аутентификации пользователяs
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

# для ограничения доступа используется декоратор, поскольку у нас метод
# для классов происходит наследование у класса PermissionRequiredMixin
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        # print(request.POST['renewal_date'])

        # 1 способ
        # print(request.POST)
        form = RenewBookForm(request.POST)
        # print(form)
        # 2 способ
        # form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        # здесь происходит и внутрення валидация (Django) и дополнитльная валидация, которую создал я внутри формы
        # RenewBookForm --> метод clean_renewal_date
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)

            # 1 способ
            book_inst.due_back = form.cleaned_data['renewal_date']
            # 2 способ
            # book_inst.due_back = form.cleaned_data['due_back']

            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        # 1 способ
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })
        # 2 способ
        # form = RenewBookModelForm(initial={'due_back': proposed_renewal_date, })

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})

# Обобщенные классы отображения для редактирования
# синтаксис такой как и у форм, которые наслеюутся у ModelForm
# Отображения  "создать" и "обновить" используют  шаблоны с именем model_name_form.html,
# по умолчанию: (вы можете поменять суффикс на что-нибудь другое, при помощи поля
# template_name_suffix в вашем отображении, например, template_name_suffix = '_other_suffix')
#  я ничего не менял, поэтому название шаблона должно быть author_form.html, поскольку модель Author
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author

    # указываем разрешения
    permission_required = ('catalog.can_update_create_delete_author', )

    fields = '__all__'
    initial = {'date_of_death': '12/10/1500', }


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author

    # указываем разрешения
    permission_required = ('catalog.can_update_create_delete_author', )

    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


# Отображения "удалить" ожидает "найти" шаблон с именем формата model_name_confirm_delete.html
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    # указываем разрешения
    permission_required = ('catalog.can_update_create_delete_author', )

    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book

    # указываем разрешения
    permission_required = ('catalog.can_update_create_delete_book', )

    fields = '__all__'
    # initial = {'date_of_death': '12/10/1500', }
    initial = {'summary': 'Очень интересная книга раз ты ее добавляешь!', }


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book

    # указываем разрешения
    permission_required = ('catalog.can_update_create_delete_book', )
    fields = '__all__'

    # fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


# Отображения "удалить" ожидает "найти" шаблон с именем формата model_name_confirm_delete.html
class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    # указываем разрешения
    permission_required = ('catalog.can_update_create_delete_book', )

    success_url = reverse_lazy('books')
