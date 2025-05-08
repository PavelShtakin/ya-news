from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from news.forms import CommentForm

from news.models import News, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Новость', text='Текст')
        cls.user = User.objects.create_user(username='user')
        bulk_news = [News(title=f'Новость {i}', text='Текст') for i in range(11)]
        News.objects.bulk_create(bulk_news)
        cls.comment1 = Comment.objects.create(
            news=cls.news,
            author=cls.user,
            text='Старый комментарий',
            created=timezone.now() - timezone.timedelta(days=1)
        )
        cls.comment2 = Comment.objects.create(
            news=cls.news,
            author=cls.user,
            text='Новый комментарий'
        )

    def test_news_count_on_homepage(self):
        url = reverse('news:home')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertLessEqual(len(object_list), 10)

    def test_news_order_on_homepage(self):
        url = reverse('news:home')
        response = self.client.get(url)
        object_list = response.context['object_list']
        dates = [item.date for item in object_list]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_anonymous_user_has_no_comment_form(self):
        url = reverse('news:detail', args=(self.news.id,))
        response = self.client.get(url)
        self.assertNotIn('form', response.context)

    def test_authorized_user_sees_comment_form(self):
        self.client.force_login(self.user)
        url = reverse('news:detail', args=(self.news.id,))
        response = self.client.get(url)
        self.assertIn('form', response.context)


class TestHomePage(TestCase):
    @classmethod
    def setUpTestData(cls):
        News.objects.bulk_create(
            News(title=f'Новость {index}', text='Просто текст.')
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

    def test_news_count(self):
        url = reverse('news:home')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertLessEqual(len(object_list), settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        url = reverse('news:home')
        response = self.client.get(url)
        object_list = response.context['object_list']
        dates = [news.date for news in object_list]
        sorted_dates = sorted(dates, reverse=True)
        self.assertEqual(dates, sorted_dates)


class TestDetailPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Новость', text='Текст')
        cls.author = User.objects.create_user(username='Пользователь')
        cls.detail_url = reverse('news:detail', args=(cls.news.id,))
        cls.comments = []
        for index in range(3):
            comment = Comment.objects.create(
                news=cls.news,
                author=User.objects.create(username=f'user{index}'),
                text=f'Комментарий {index}',
            )
            comment.created = timezone.now() - timedelta(days=3 - index)
            comment.save()
            cls.comments.append(comment)

    def test_comments_order(self):
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        self.assertEqual(all_timestamps, sorted_timestamps)

    def test_anonymous_user_has_no_form(self):
        response = self.client.get(self.detail_url)
        self.assertIsNone(response.context.get('form'))

    def test_authorized_user_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIsNotNone(response.context.get('form'))
        self.assertIsInstance(response.context['form'], CommentForm)
