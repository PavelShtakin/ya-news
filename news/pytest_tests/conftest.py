import pytest
from datetime import datetime, timedelta
from django.test.client import Client
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create_user(username='author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create_user(username='not_author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Test News',
        text='Some text',
        date=datetime.now() - timedelta(days=1),
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Test comment'
    )
