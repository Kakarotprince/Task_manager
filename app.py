from flask import Flask,render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager
from models import db
from resources import UserRegistration, UserLogin, TaskList, TaskDetail

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'dev-secret-key' # Use environment variables in production


db.init_app(app)
api = Api(app)
jwt = JWTManager(app)


with app.app_context():
    db.create_all()


@app.route('/')
def serve_frontend():
    return render_template('index.html')


api.add_resource(UserRegistration, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(TaskList, '/tasks')
api.add_resource(TaskDetail, '/tasks/<int:task_id>')

if __name__ == '__main__':
    app.run(debug=True)