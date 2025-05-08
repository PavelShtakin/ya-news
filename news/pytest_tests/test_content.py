import pytest
from django.urls import reverse
from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture, comment_visible',
    [
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    ]
)
def test_comment_visibility_in_detail_page(client_fixture, comment, comment_visible):
    url = reverse('news:detail', args=(comment.news.pk,))
    response = client_fixture.get(url)
    object_list = response.context['news'].comment_set.all()
    assert (comment in object_list) is comment_visible


@pytest.mark.django_db
def test_comment_form_shown_for_authorized_user(news, author_client):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ['news:edit']
)
def test_edit_page_contains_form(name, author_client, comment):
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
