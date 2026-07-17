import pytest
from app import app, db

@pytest.fixture
def client():

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_user_registration_and_login(client):
    
    reg_response = client.post('/register', json={'username': 'testuser', 'password': 'password123'})
    assert reg_response.status_code == 201

    
    login_response = client.post('/login', json={'username': 'testuser', 'password': 'password123'})
    assert login_response.status_code == 200
    assert 'access_token' in login_response.get_json()

def test_task_creation(client):
    
    client.post('/register', json={'username': 'testuser', 'password': 'password123'})
    login_response = client.post('/login', json={'username': 'testuser', 'password': 'password123'})
    token = login_response.get_json()['access_token']

    
    headers = {'Authorization': f'Bearer {token}'}
    task_response = client.post('/tasks', json={'title': 'Ace the interview', 'description': 'Review Python concepts'}, headers=headers)
    
    assert task_response.status_code == 201
    assert task_response.get_json()['message'] == 'Task created successfully'