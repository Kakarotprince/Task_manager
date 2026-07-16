from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Task

class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'User already exists'}, 400
        
        new_user = User(username=data['username'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=str(user.id))
            return {'access_token': access_token}, 200
            
        return {'message': 'Invalid credentials'}, 401

class TaskList(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        tasks = Task.query.filter_by(user_id=current_user_id).all()
        return [{'id': t.id, 'title': t.title, 'description': t.description, 'completed': t.completed} for t in tasks], 200

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        new_task = Task(
            title=data['title'], 
            description=data.get('description', ''), 
            user_id=current_user_id
        )
        db.session.add(new_task)
        db.session.commit()
        return {'message': 'Task created successfully', 'task_id': new_task.id}, 201

class TaskDetail(Resource):
    @jwt_required()
    def get(self, task_id):
        current_user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first_or_404()
        return {'id': task.id, 'title': task.title, 'description': task.description, 'completed': task.completed}, 200

    @jwt_required()
    def put(self, task_id):
        current_user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first_or_404()
        data = request.get_json()
        
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.completed = data.get('completed', task.completed)
        db.session.commit()
        
        return {'message': 'Task updated successfully'}, 200

    @jwt_required()
    def delete(self, task_id):
        current_user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first_or_404()
        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deleted successfully'}, 200