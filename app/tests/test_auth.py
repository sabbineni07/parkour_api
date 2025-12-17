import pytest
from app import db
from app.models.user import User

def test_register_user(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'first_name': 'New',
        'last_name': 'User'
    })
    
    assert response.status_code == 201
    assert 'access_token' in response.json
    assert response.json['user']['username'] == 'newuser'

def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    # Create first user
    client.post('/api/auth/register', json={
        'username': 'duplicate',
        'email': 'first@example.com',
        'password': 'password123',
        'first_name': 'First',
        'last_name': 'User'
    })
    
    # Try to register with same username
    response = client.post('/api/auth/register', json={
        'username': 'duplicate',
        'email': 'second@example.com',
        'password': 'password123',
        'first_name': 'Second',
        'last_name': 'User'
    })
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error'].lower()

def test_login_success(client):
    """Test successful login"""
    # Create user first
    user = User(
        username='loginuser',
        email='login@example.com',
        first_name='Login',
        last_name='User'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    # Login
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert response.json['user']['username'] == 'loginuser'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'invalid' in response.json['error'].lower()

def test_get_profile(client, auth_headers):
    """Test getting user profile"""
    response = client.get('/api/auth/profile', headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['user']['username'] == 'testuser'

def test_get_profile_unauthorized(client):
    """Test getting profile without authentication"""
    response = client.get('/api/auth/profile')
    
    assert response.status_code == 401

def test_update_profile(client, auth_headers):
    """Test updating user profile"""
    response = client.put('/api/auth/profile', 
                         headers=auth_headers,
                         json={
                             'first_name': 'Updated',
                             'last_name': 'Name'
                         })
    
    assert response.status_code == 200
    assert response.json['user']['first_name'] == 'Updated'
    assert response.json['user']['last_name'] == 'Name'



