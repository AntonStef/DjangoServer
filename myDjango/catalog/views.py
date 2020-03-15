from django.shortcuts import render
from .models import *
from django.db.models.functions import Lower
# render - функция которая генерирует HTML-файлы при помощи
# шаблонов страниц и соотвествующих данных


# Create your views here.
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
    num_genre_my = [Object.name for Object in Genre.objects.all()
                    if 'ЖАС'.lower() in Object.name.lower()]
    # Получить книги которы содержат гарри без учета регистра
    num_books_my = [Object.title for Object in Book.objects.all()
                    if 'ГарРи'.lower() in Object.title.lower()]

    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_genre_my': num_genre_my, 'num_books_my': num_books_my},
    )