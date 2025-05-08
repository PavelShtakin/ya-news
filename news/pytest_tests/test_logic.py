import pytest
from django.urls import reverse
from http import HTTPStatus
from news.models import Comment


@pytest.mark.django_db
def test_authorized_user_can_create_comment(author_client, news, author):
    url = reverse('news:detail', args=(news.pk,))
    form_data = {'text': 'Test comment'}
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=(news.pk,)) + '#comments'
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cannot_create_comment(client, news):
    url = reverse('news:detail', args=(news.pk,))
    form_data = {'text': 'Anonymous comment'}
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    form_data = {'text': 'Updated text'}
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=(comment.news.pk,)) + '#comments'
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url
    comment.refresh_from_db()
    assert comment.text == 'Updated text'


@pytest.mark.django_db
def test_other_user_cannot_edit_comment(not_author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    form_data = {'text': 'Malicious update'}
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    original_comment = Comment.objects.get(pk=comment.pk)
    assert original_comment.text == comment.text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=(comment.news.pk,)) + '#comments'
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cannot_delete_comment(not_author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
