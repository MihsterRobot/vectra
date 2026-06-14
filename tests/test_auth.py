def test_register(client):
    response = client.post('/auth/register', json={
        'email': 'test@test.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = response.json()
    assert data['email'] == 'test@test.com'
    assert 'id' in data


def test_register_duplicate_email(client):
    client.post('/auth/register', json={
        'email': 'test@test.com',
        'password': 'password123'
    })
    response = client.post('/auth/register', json={
        'email': 'test@test.com',
        'password': 'password123'
    })
    assert response.status_code == 400
    assert response.json()['detail'] == 'Email already registered'


def test_login(client):
    client.post('/auth/register', json={
        'email': 'test@test.com',
        'password': 'password123'
    })
    response = client.post('/auth/token', data={
        'username': 'test@test.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


def test_login_invalid_credentials(client):
    response = client.post('/auth/token', data={
        'username': 'wrong@test.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'
