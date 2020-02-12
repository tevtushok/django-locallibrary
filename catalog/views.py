import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Book, BookInstance, Author
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookModelForm

def index(request):
    """
    Function for representing home pate
    """
    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    data = {}
    data['num_books'] = Book.objects.all().count()
    data['num_instances'] = BookInstance.objects.all().count()
    data['num_instances_available'] = BookInstance.objects.filter(status__exact='a').count()
    data['num_authors'] = Author.objects.count()
    data['num_books_title_filter'] = Book.objects.filter(title__contains='world').count()
    data['num_books_genre_filter'] = Book.objects.filter(genre__name__contains='fiction').distinct().count()
    data['num_visits'] = num_visits


    return render(
            request,
            'index.html',
            context={'data': data}
    )


from django.views import generic

class BookListView(generic.ListView):
    model = Book
    context_object_name = 'book_list'
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            books = Book.objects.filter(author_id=pk)
            paginator = Paginator(books, self.paginate_by)
            page = self.request.GET.get('page', 1)

            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            context['page_obj'] = page_obj
            context['book_list'] = context['page_obj']
            context['is_paginated'] = paginator.num_pages > 1 or None
        return context

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    paginate_by = 10
    template_name = 'catalog/bookinstance_list_boorowed_books.html'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


#from django.contrib.admin.views.decorators import staff_member_required

class BorrowersListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = ('catalog.can_mark_returned')
    template_name = 'catalog/bookinstance_list_borrowers.html'

@permission_required('catalog.can_mark_returned')
def renew_book_librian(request, pk):
    bookinstance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data

    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        if form.is_valid():
            bookinstance.due_back = form.cleaned_data['due_back']
            bookinstance.save()
            return HttpResponseRedirect(reverse('borrowers'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(
            initial={'due_back': proposed_renewal_date}
        )

    context = {
        'form': form,
        'bookinstance': bookinstance,
    }
    return render(
        request, 'catalog/book_renew_librian.html', context
    )


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('catalog.add_author')
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {
        'date_of_death': '05/11/2018',
    }

class AuthorUpdate(UpdateView):
    permission_required = ('catalog.change_author')
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    permission_required = ('catalog.delete_author')
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('catalog.add_book')
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    success_url = reverse_lazy('books')

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('catalog.change_book')
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    success_url = reverse_lazy('books')

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('catalog.delete_book')
    model = Book
    success_url = reverse_lazy('books')
