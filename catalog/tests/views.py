from django.test import TestCase
from django.test import Client
import uuid
from django.db.models.query import QuerySet
from catalog.models import Book, Author, BookInstance
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
import datetime
import json
import sys
from django.http import HttpResponse
import dumper
from django.shortcuts import get_object_or_404

# Create your tests here.


class ViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.auth_creds = {
                'super': {
                    'username': 'super',
                    'password': 'pwd_super'
                },
                'staff': {
                    'username': 'staff',
                    'password': 'pwd_staff'
                },
                'client': {
                    'username': 'client',
                    'password': 'pwd_client'
                }
        }
        cls.user_super = User.objects.create_user(
            username=cls.auth_creds['super']['username'],
            password=cls.auth_creds['super']['password'],
            is_superuser = True,
            is_staff = True,
        )

        cls.user_group_librarians = Group.objects.create(
            name='Librarians',
        )
        perm = Permission.objects.get(codename='can_mark_returned')
        cls.user_group_librarians.permissions.add(perm)

        cls.user_staff = User.objects.create_user(
            username=cls.auth_creds['staff']['username'],
            password=cls.auth_creds['staff']['password'],
            is_superuser = False,
            is_staff = True,
        )
        cls.user_staff.groups.add(cls.user_group_librarians)

        cls.user_client = User.objects.create_user(
            username=cls.auth_creds['client']['username'],
            password=cls.auth_creds['client']['password'],
            is_superuser = False,
            is_staff = False,
        )

    def test_ok(self):
        pass

    def createBook(self, **kwargs):
        default = {
            'title': 'book_test' + uuid.uuid4().hex,
            'summary': 'summary text',
        }
        default.update(kwargs)
        book = Book.objects.create(**default)
        return book

    def createBookInstance(self, **kwargs):
        default = {
            'imprint': 'imprint_' + uuid.uuid4().hex,
            'due_back': datetime.date.today() + datetime.timedelta(weeks=3),

        }
        default.update(kwargs)
        bi = BookInstance.objects.create(**default)
        return bi

    def createAuthor(self, **kwargs):
        default = {
                'first_name': 'first_name_test-' + uuid.uuid4().hex,
                'last_name': 'last_name_test-' + uuid.uuid4().hex,
        }
        default.update(kwargs)
        author = Author(**default)
        author.save()
        return author

    def formErrorsContainField(self, response, field):
        form = response.context.get('form', False)
        if not form:
            raise AttributeError('countext doesnt have form attribute')
        field = response.context.get('form').errors.get(field, False)
        #return (True, False) [field == False]
        return True if field == True else False

    def addLibrariansPerm(self, codename):
        perm = get_object_or_404(Permission, codename=codename)
        self.user_group_librarians.permissions.add(perm)

    def test_index_true(self):
        response = self.client.get('/catalog/')
        self.assertEquals(200,response.status_code)
        data = response.context.get('data', False)
        self.assertTrue(data)
        self.assertTrue(True,
                isinstance(data.get('num_books', False), int))

    def test_index_false(self):
        invalid_url = '/catalog/' + uuid.uuid4().hex
        response = self.client.get(invalid_url)
        self.assertEquals(404,response.status_code)

    def test_BookListView_true(self):
        response = self.client.get('/catalog/books/')
        self.assertEquals(200, response.status_code)
        book_list1 = response.context.get('book_list')
        self.assertTrue(isinstance(book_list1, QuerySet))
        book = self.createBook()
        response = self.client.get('/catalog/books/')
        book_list2 = response.context.get('book_list')
        self.assertTrue(len(book_list2) > len(book_list1))

    def test_BookDetailView_true(self):
        book = self.createBook()
        url = (reverse('book-detail', args=[str(book.pk)]))
        response = self.client.get(url)
        model = response.context.get('book', False)
        self.assertTrue(isinstance(model, Book))

    def test_BookDetailView_404(self):
        book = self.createBook()
        url = (reverse('book-detail', args=[str(0)]))
        response = self.client.get(url)
        self.assertEquals(404, response.status_code)

    def test_AuthorsListView_True(self):
        response = self.client.get(reverse('authors'))
        author_list = response.context.get('author_list', False)
        self.assertTrue(isinstance(author_list, QuerySet))
        author = self.createAuthor()
        response2 = self.client.get(reverse('authors'))
        author_list2 = response2.context.get('author_list', False)
        self.assertTrue(len(author_list) < len(author_list2))

    def test_AuthorDetailViewTrue(self):
        author = self.createAuthor()
        path = reverse('author-detail', args=[str(author.pk)])
        response = self.client.get(path)
        model = response.context.get('author', False)
        self.assertTrue(isinstance(model, Author))

        [self.createBook(author=author) for _ in range(15)]
        response = self.client.get(path, {'page': '1x'})
        self.assertEquals(200,response.status_code)
        num_pages = response.context_data['page_obj'].paginator.num_pages
        response = self.client.get(path, {'page': num_pages + 1})
        self.assertEquals(200,response.status_code)

    def test_AuthorDetailView404(self):
        author = self.createAuthor()
        path = reverse('author-detail', args=[str(0)])
        response = self.client.get(path)
        self.assertEquals(404,response.status_code)

    def test_LoanedBooksByUserListViewFalse(self):
        path = reverse('my-borrowed')
        response = self.client.get(path)
        expect_path = '/accounts/login/?next=' + path
        self.assertRedirects(response, expect_path, status_code=302)

    def test_LoanedBooksByUserListViewEmptyTrue(self):
        self.assertTrue(self.client.login(**self.auth_creds['client']))
        path = reverse('my-borrowed')
        response = self.client.get(path)
        b_list = response.context.get('bookinstance_list', False)
        self.assertTrue(isinstance(b_list, QuerySet))
        self.assertEquals(0, len(b_list))

    def test_LoanedBooksByUserListViewNotEmptyTrue(self):
        book = self.createBook()
        user = self.user_client
        bi = self.createBookInstance(
            book=book, borrower=user, status='o'
        )
        self.assertTrue(self.client.login(**self.auth_creds['client']))
        path = reverse('my-borrowed')
        response = self.client.get(path)
        b_list = response.context.get('bookinstance_list', False)
        self.assertTrue(isinstance(b_list, QuerySet))
        self.assertTrue(0 < len(b_list))

    def test_BorrowersListViewRedirectLogin(self):
        path = reverse('borrowers')
        response = self.client.get(path)
        expect_path = '/accounts/login/?next=' + path
        self.assertRedirects(response, expect_path, status_code=302)

    def test_BorrowersListView403(self):
        self.assertTrue(self.client.login(**self.auth_creds['client']))
        path = reverse('borrowers')
        response = self.client.get(path)
        self.assertEquals(403, response.status_code)

    def test_BorrowersListViewEmptyTrue(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        path = reverse('borrowers')
        response = self.client.get(path)
        self.assertEquals(200, response.status_code)
        bi_list = response.context.get('bookinstance_list', False)
        self.assertTrue(isinstance(bi_list, QuerySet))

    def test_BorrowersListViewNotEmptyTrue(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        book = self.createBook()
        user = self.user_client
        bi = self.createBookInstance(
            book=book, borrower=user, status='o'
        )
        path = reverse('borrowers')
        response = self.client.get(path)
        self.assertEquals(200, response.status_code)
        bi_list = response.context.get('bookinstance_list', False)
        self.assertTrue(len(bi_list) > 0)

    def test_renew_book_librianViewRedirectClient(self):
        self.assertTrue(self.client.login(**self.auth_creds['client']))
        path = reverse('renew-book-librian', args=[str(uuid.uuid4())])
        response = self.client.get(path)
        expect_path = '/accounts/login/?next=' + path
        self.assertRedirects(response, expect_path, status_code=302)
        pass

    def test_renew_book_librianViewRedirectGuest(self):
        path = reverse('renew-book-librian', args=[str(uuid.uuid4())])
        response = self.client.get(path)
        expect_path = '/accounts/login/?next=' + path
        self.assertRedirects(response, expect_path, status_code=302)
        pass

    def test_renew_book_librianView404(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        path = reverse('renew-book-librian', args=[str(uuid.uuid4())])
        response = self.client.get(path)
        self.assertEquals(404, response.status_code)

    def test_renew_book_librianViewInvalidDate(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        book = self.createBook()
        user = self.user_client
        bi = self.createBookInstance(
            book=book, borrower=user, status='o'
        )
        path = reverse('renew-book-librian', args=[bi.pk])
        response = self.client.post(path, {})
        self.assertTrue(self.formErrorsContainField(response, 'due_back'))

    def test_renew_book_librianViewPastData(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        book = self.createBook()
        user = self.user_client
        bi = self.createBookInstance(
            book=book, borrower=user, status='o'
        )
        path = reverse('renew-book-librian', args=[bi.pk])
        past_date = datetime.date.today() - datetime.timedelta(days=1)
        args = {'due_back': past_date}
        response = self.client.post(path, args)
        self.assertTrue(self.formErrorsContainField(response, 'due_back'))

    def test_renew_book_librianView2MonData(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        book = self.createBook()
        user = self.user_client
        bi = self.createBookInstance(
            book=book, borrower=user, status='o'
        )
        path = reverse('renew-book-librian', args=[bi.pk])
        date_2mon = datetime.date.today() + datetime.timedelta(weeks=8)
        args = {'due_back': date_2mon}
        response = self.client.post(path, args)
        self.assertTrue(self.formErrorsContainField(response, 'due_back'))

    def test_renew_book_librianGetTrue(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        book = self.createBook()
        user = self.user_client
        bi = self.createBookInstance(
            book=book, borrower=user, status='o'
        )
        path = reverse('renew-book-librian', args=[bi.pk])
        response = self.client.get(path)
        self.assertEquals(200, response.status_code)

    def test_renew_book_librianViewValidDate(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        book = self.createBook()
        user = self.user_client
        bi = self.createBookInstance(
            book=book, borrower=user, status='o'
        )
        path = reverse('renew-book-librian', args=[bi.pk])
        future_date = datetime.date.today() + datetime.timedelta(days=1)
        args = {'due_back': future_date}
        response = self.client.post(path, args)
        expect_path = '/catalog/borrowers/'
        self.assertRedirects(response, expect_path, status_code=302)

    def test_author_createGetRedirect(self):
        path = reverse('author_create')
        expect_path = '/accounts/login/?next=' + path
        response = self.client.get(path)
        self.assertRedirects(response, expect_path, status_code=302)

    def test_author_createGet403(self):
        self.assertTrue(self.client.login(**self.auth_creds['client']))
        path = reverse('author_create')
        expect_path = '/accounts/login/?next=' + path
        response = self.client.get(path)
        self.assertEquals(403, response.status_code)

    def test_author_createPostStaff403(self):
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        path = reverse('author_create')
        response = self.client.post(path, {})
        self.assertEquals(403, response.status_code)

    def test_author_createPostStaffTrue(self):
        self.addLibrariansPerm('add_author')
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        path = reverse('author_create')
        args = {
                'first_name': 'test_author',
                'last_name': 'last_author',
                'date_of_birth': '05/13/1000',
        }
        response = self.client.post(path, args)
        self.assertEquals(302, response.status_code)

    def test_author_createPostStaffFalse(self):
        self.addLibrariansPerm('add_author')
        self.assertTrue(self.client.login(**self.auth_creds['staff']))
        path = reverse('author_create')
        args = {
                'first_name': 'test_author',
                'last_name': 'last_author',
                'date_of_birth': '1000',
                'date_of_death': '1000',
        }

        response = self.client.post(path, args)
        db = self.formErrorsContainField(response, 'date_of_birth')
        dd = self.formErrorsContainField(response, 'date_of_birth')
        self.assertTrue(db)
        self.assertTrue(dd)
