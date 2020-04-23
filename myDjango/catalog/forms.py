from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime  # for checking renewal date range.

from django.forms import ModelForm
from .models import BookInstance

# создание формы на основе класса Form
class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).",
                                   label='New date')

    # создаем дополнительную поля поля renewal_date из формы, что бы оно было не позже текущего дня
    # и не позже 4-х недель вперед
    # мето должен иметь имя clean_<fieldname>(), где fieldname - это интересующее нас поле
    # в данном случае renewal_date
    def clean_renewal_date(self):
        # Данный шаг позволяет нам, при помощи валидаторов, получить "очищенные", проверенные,
        # а затем, приведенные к стандартным типам, данные
        # в данном случае в datetime.datetime
        # print(type(self.cleaned_data['renewal_date']), self.cleaned_data['renewal_date'])
        # print(self.cleaned_data)
        data = self.cleaned_data['renewal_date']

        # Проверка того, что дата не выходит за "нижнюю" границу (не в прошлом).
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Проверка того, то дата не выходит за "верхнюю" границу (+4 недели).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Помните, что всегда надо возвращать "очищенные" данные.
        # print('data', data)
        return data

# создание формы на основе уже существующей модели
# это намного легче на мой взгляд
# этот класс явялется эквивалентом RenewBookForm, только он на основе модели
class RenewBookModelForm(ModelForm):

    # создается метод для валидации конкретного поля формы. Поскольку тут нет объявления полей, а они берутся из модели
    # поэтому мы пишем уже не clean_renewal_date, а clean_due_back потому что поле модели "due_back"
    def clean_due_back(self):
        data = self.cleaned_data['due_back']

        # Проверка того, что дата не в прошлом
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past (!using Model!)'))

        # Check date is in range librarian allowed to change (+4 weeks)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead (!using Model!)'))

        # Не забывайте всегда возвращать очищенные данные
        return data

    class Meta:
        model = BookInstance
        # происываем поля которые хотим отсавим в форме
        fields = ['due_back', ]
        # значением атребутов для полей формы указываем следующим образом
        # атребут = {поле: значене}
        labels = {'due_back': _('Renewal date custom'), }
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).'), }
