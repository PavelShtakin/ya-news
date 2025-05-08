import pytest
from http import HTTPStatus
from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page_for_anonymous_user(news, client):
    url = reverse('news:detail', args=(news.pk,))
    expected_url = f'{reverse("users:login")}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


@pytest.mark.django_db
def test_redirect_edit_comment_for_anonymous(news, comment, client):
    url = reverse('news:edit', args=(comment.pk,))
    expected_url = f'{reverse("users:login")}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


@pytest.mark.django_db
def test_redirect_delete_comment_for_anonymous(news, comment, client):
    url = reverse('news:delete', args=(comment.pk,))
    expected_url = f'{reverse("users:login")}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url

