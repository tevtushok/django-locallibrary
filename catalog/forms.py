import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.forms import ModelForm

from catalog.models import BookInstance, Book

class RenewBookModelForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('New renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default is 3).')}

    def clean_due_back(self):
        date = self.cleaned_data.get('due_back', 0)

        if not date:
            raise ValidationError(_('Invalid date - invalid value'))

        if date < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        if date > (datetime.date.today() + datetime.timedelta(weeks=4)):
            raise ValidationError(_('Invalid date - renewal date more than 4 weeks ahead'))

        return date

    """

        def clean_title(self):
            title = self.cleaned_data['title']
            return title

        def clean_author:
            author = self.cleaned_data['author']
            return author

        def clean_summary:
            summary = self.cleaned_data['summary']
            return summary

        def clean_isbn:
            isbn = self.cleaned_data['isbn']
            return isbn

        def clean_genre:
            genre = self.cleaned_data['genre']
            return genre

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
"""
