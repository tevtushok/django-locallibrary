from django.urls import resolve
from django.test import TestCase
from django.urls.exceptions import Resolver404
import uuid

# Create your tests here.


class ViewTestCase(TestCase):
    def test_UrlFalse(self):
        with self.assertRaises(Resolver404):
            resolver = resolve(str(uuid.uuid4()))

    def test_booksTrue(self):
        resolver = resolve('/catalog/books/')
        self.assertEquals(resolver.view_name, 'books')

    def test_bookDetail_True(self):
        resolver = resolve('/catalog/books/1')
        self.assertEquals(resolver.view_name, 'book-detail')

    def test_bookDetail_False(self):
        with self.assertRaises(Resolver404):
            resolver = resolve('/catalog/books/1x')

    def test_Authors_True(self):
        resolver = resolve('/catalog/authors/')
        self.assertEquals(resolver.view_name, 'authors')

    def test_AuthorDetail_True(self):
        resolver = resolve('/catalog/author/1')
        self.assertEquals(resolver.view_name, 'author-detail')

    def test_AuthorDetail_False(self):
        with self.assertRaises(Resolver404):
            resolver = resolve('/catalog/author/1x')

    def test_MyBorrowed_True(self):
        resolver = resolve('/catalog/mybooks/')
        self.assertEquals(resolver.view_name, 'my-borrowed')

    def test_Borrowers_True(self):
        resolver = resolve('/catalog/borrowers/')
        self.assertEquals(resolver.view_name, 'borrowers')

    def test_RenewBookLibrian_True(self):
        UUID = str(uuid.uuid4())
        resolver = resolve('/catalog/book/{0}/renew/'.format(UUID))

    def test_RenewBookLibrian_False(self):
        with self.assertRaises(Resolver404):
            resolver = resolve('/catalog/book/13/renew/')

    def test_AuthorCreate_True(self):
        resolver = resolve('/catalog/author/create')
        self.assertEquals(resolver.view_name, 'author_create')

    def test_AuthorDelete_True(self):
        resolver = resolve('/catalog/author/1/delete')
        self.assertEquals(resolver.view_name, 'author_delete')

    def test_AuthorDelete_False(self):
        with self.assertRaises(Resolver404):
            resolver = resolve('/catalog/author/1x/delete')

    def test_AuthorUpdate_True(self):
        resolver = resolve('/catalog/author/1/update')
        self.assertEquals(resolver.view_name, 'author_update')


    def test_AuthorUpdate_False(self):
        with self.assertRaises(Resolver404):
            resolver = resolve('/catalog/author/1x/update')

    def test_BookCreate_True(self):
        resolver = resolve('/catalog/book/create')
        self.assertEquals(resolver.view_name, 'book_create')

    def test_BookDelete_True(self):
        resolver = resolve('/catalog/book/1/delete')
        self.assertEquals(resolver.view_name, 'book_delete')

    def test_BookDelete_False(self):
        with self.assertRaises(Resolver404):
            resolver = resolve('/catalog/book/1x/delete')

    def test_BookUpdate_True(self):
        resolver = resolve('/catalog/book/1/update')
        self.assertEquals(resolver.view_name, 'book_update')

    def test_BookUpdate_False(self):
        with self.assertRaises(Resolver404):
            resolver = resolve('/catalog/book/1x/update')
