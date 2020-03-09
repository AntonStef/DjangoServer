from django.contrib import admin
from .models import Book, Author, BookInstance, Genre


# чтобы в книгах можно было отображать реальные доступные копии
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    # уберает не нужные инстансы, которые не относятся
    # extra конкретнойкниги
    extra = 0


# чтобы в авторах можно было отображать имеющиеся книги
class BooksInline(admin.TabularInline):
    model = Book
    exclude = ['summary']
    # уберает не нужные инстансы, которые не относятся
    # extra конкретнойкниги
    extra = 0


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]


# декоратор делает тоже что и admin.site.register(BookAdmin)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # можно передвать результаты работы методов, опредяляемых в модели
    # display_genre
    list_display = ('title', 'author', 'display_genre')
    list_filter = ('author', )
    inlines = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        ('Main information', {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )


# Register your models here.
# admin.site.register(Book)
# admin.site.register(AuthorAdmin)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)
