from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import News, Comment

User = get_user_model()


class TestCommentEditDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Новость', text='Текст')
        cls.author = User.objects.create_user(username='author')
        cls.reader = User.objects.create_user(username='reader')
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Оригинальный текст'
        )
        cls.edit_url = reverse('news:edit', args=(cls.comment.pk,))
        cls.delete_url = reverse('news:delete', args=(cls.comment.pk,))
        cls.form_data = {'text': 'Обновлённый текст'}

    def test_author_can_edit_comment(self):
        self.client.force_login(self.author)
        self.client.post(self.edit_url, data=self.form_data)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, self.form_data['text'])

    def test_author_can_delete_comment(self):
        self.client.force_login(self.author)
        self.client.post(self.delete_url)
        self.assertFalse(Comment.objects.exists())

    def test_anonymous_cant_edit_or_delete_comment(self):
        edit_response = self.client.get(self.edit_url)
        delete_response = self.client.get(self.delete_url)
        login_url = reverse('users:login')
        expected_edit_redirect = f'{login_url}?next={self.edit_url}'
        expected_delete_redirect = f'{login_url}?next={self.delete_url}'
        self.assertRedirects(edit_response, expected_edit_redirect)
        self.assertRedirects(delete_response, expected_delete_redirect)

    def test_foreign_user_cant_edit_or_delete_comment(self):
        self.client.force_login(self.reader)
        edit_response = self.client.get(self.edit_url)
        delete_response = self.client.get(self.delete_url)
        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
