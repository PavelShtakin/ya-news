from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from news.models import News, Comment

User = get_user_model()


class CommentRoutesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.other_user = User.objects.create_user(username='other')
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Комментарий'
        )
        cls.edit_url = reverse('news:edit', args=(cls.comment.pk,))
        cls.delete_url = reverse('news:delete', args=(cls.comment.pk,))
        cls.login_url = reverse('users:login')

    def test_author_has_access_to_edit_and_delete(self):
        self.client.force_login(self.author)
        edit_response = self.client.get(self.edit_url)
        delete_response = self.client.get(self.delete_url)
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)

    def test_anonymous_redirects_to_login(self):
        edit_response = self.client.get(self.edit_url)
        delete_response = self.client.get(self.delete_url)
        expected_login_edit = f'{self.login_url}?next={self.edit_url}'
        expected_login_delete = f'{self.login_url}?next={self.delete_url}'
        self.assertRedirects(edit_response, expected_login_edit)
        self.assertRedirects(delete_response, expected_login_delete)

    def test_foreign_user_gets_404(self):
        self.client.force_login(self.other_user)
        edit_response = self.client.get(self.edit_url)
        delete_response = self.client.get(self.delete_url)
        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)



class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title='Тестовая новость',
            text='Просто текст'
        )

    def test_home_page(self):
        url = reverse('news:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_page(self):
        url = reverse('news:detail', args=(self.news.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestCommentRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='auth', password='pass')
        cls.news = News.objects.create(title='Тестовая новость', text='Текст')
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.user,
            text='Текст комментария'
        )

    def test_edit_and_delete_routes_for_author(self):
        self.client.force_login(self.user)

        edit_url = reverse('news:edit', args=(self.comment.id,))
        delete_url = reverse('news:delete', args=(self.comment.id,))

        edit_response = self.client.get(edit_url)
        delete_response = self.client.get(delete_url)

        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)

    def test_edit_and_delete_redirect_for_anonymous(self):
        edit_url = reverse('news:edit', args=(self.comment.id,))
        delete_url = reverse('news:delete', args=(self.comment.id,))
        login_url = reverse('users:login')

        expected_edit_redirect = f'{login_url}?next={edit_url}'
        expected_delete_redirect = f'{login_url}?next={delete_url}'

        edit_response = self.client.get(edit_url)
        delete_response = self.client.get(delete_url)

        self.assertRedirects(edit_response, expected_edit_redirect)
        self.assertRedirects(delete_response, expected_delete_redirect)

    def test_edit_and_delete_unavailable_for_another_user(self):
        another_user = User.objects.create_user(username='AnotherUser')
        self.client.force_login(another_user)

        edit_url = reverse('news:edit', args=(self.comment.id,))
        delete_url = reverse('news:delete', args=(self.comment.id,))

        edit_response = self.client.get(edit_url)
        delete_response = self.client.get(delete_url)

        self.assertEqual(edit_response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(delete_response.status_code, HTTPStatus.NOT_FOUND)
