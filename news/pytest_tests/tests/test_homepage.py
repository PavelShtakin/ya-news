def test_homepage_available(client):
    response = client.get('/')
    assert response.status_code == 200