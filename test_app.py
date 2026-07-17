import pytest
from app import app, db

@pytest.fixture
def client():
    # Configure app for testing using an in-memory database
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_user_registration_and_login(client):
    # Test Registration
    reg_response = client.post('/register', json={'username': 'testuser', 'password': 'password123'})
    assert reg_response.status_code == 201

    # Test Login
    login_response = client.post('/login', json={'username': 'testuser', 'password': 'password123'})
    assert login_response.status_code == 200
    assert 'access_token' in login_response.get_json()

def test_task_creation(client):
    # Register and login to get JWT
    client.post('/register', json={'username': 'testuser', 'password': 'password123'})
    login_response = client.post('/login', json={'username': 'testuser', 'password': 'password123'})
    token = login_response.get_json()['access_token']

    # Test Task Creation with Auth Header
    headers = {'Authorization': f'Bearer {token}'}
    task_response = client.post('/tasks', json={'title': 'Ace the interview', 'description': 'Review Python concepts'}, headers=headers)
    
    assert task_response.status_code == 201
    assert task_response.get_json()['message'] == 'Task created successfully'

def test_task_update_and_completion(client):
    # 1. Register and login
    client.post('/register', json={'username': 'testuser2', 'password': 'password123'})
    login_response = client.post('/login', json={'username': 'testuser2', 'password': 'password123'})
    token = login_response.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Create a task
    create_resp = client.post('/tasks', 
                              json={'title': 'Learn Pytest', 'description': 'Write update tests'}, 
                              headers=headers)
    task_id = create_resp.get_json()['task_id']

    # 3. Update the task (Mark as completed)
    update_resp = client.put(f'/tasks/{task_id}', 
                             json={'completed': True}, 
                             headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.get_json()['message'] == 'Task updated successfully'

    # 4. Fetch the task to verify it was actually saved in the database
    get_resp = client.get(f'/tasks/{task_id}', headers=headers)
    task_data = get_resp.get_json()
    assert task_data['completed'] is True