from django.db import models
from isbn_field import ISBNField
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Genre(models.Model):
    """
    Model representing a book genre (e.g.g Science Fiction, Non Fiction).
    """
    name = models.CharField(max_length=200, help_text="enter a book genre (e.g. Science Fiction, French Poety etc.)")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name

class Language(models.Model):
    """
    Model representing language of book
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    """
    Model representing a book (but not a specific copy of book).
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # ForeignKey used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file.
    summary = models.TextField(max_length=2000, help_text="Enter a brief description of the book")
    isbn = ISBNField(clean_isbn=False,help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    # ManyToManyField used because genre can contain many books. Book can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.title

    def get_absolute_url(self):
        """
        Return the url to access a particular book instance.
        """
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """
        Creates a sting for the Genre. This is required for display genre in Admin
        """
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])

    class Meta:
        ordering = ['pk']

class BookInstance(models.Model):
    """
    Model representing a specify copy of book (i.e. that can be borrowed from the library).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True, help_text="Book return date")
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = [
            ('m', 'Maintenance'),
            ('o', 'On loan'),
            ('a', 'Available'),
            ('r', 'Reserved'),
    ]

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text="Book availablity")

    class Meta:
        ordering = ['due_back']
        permissions = (('can_mark_returned', 'Set book as returned'),)

    """
    String for representing book.title, status, due back and id
    """
    def __str__(self):
        #human_status = ''.join([s[1] for s in self.LOAN_STATUS if s[0] == self.status])
        return "{0}, [{1}], {2}, {3}".format(self.book.title, self.get_status_display(),
            self.due_back, self.id
    )

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

class Author(models.Model):
    """
    Model representing an author
    """
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """
        Returns the url to access a particular author instance
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return "{0}, {1}".format(self.first_name, self.last_name)

    class Meta:
        ordering = ['pk']

