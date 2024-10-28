from flask import Flask, request, jsonify, make_response, render_template, session, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) 

# Verifica se está rodando em um ambiente Docker
if os.environ.get('DB_URL'):
    # Configuração para Docker
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
else:
    # Configuração para ambiente local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'


db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'DB_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def json(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}

with app.app_context():
    db.create_all()

@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/users', methods=['POST'])
def create_users():
    try:
        data = request.get_json()
        new_user = User(username=data['username'], email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message': 'user created'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'error creating user: {e}'}), 500)

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return make_response(jsonify({'users': [user.json() for user in users]}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error retrieving users: {e}'}), 500)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({'user': user.json()}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting user'}), 500)

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            user.username = data['username'] if 'username' in data else user.username
            user.email = data['email'] if 'email' in data else user.email
            if 'password' in data:
                user.password_hash = generate_password_hash(data['password'])
            db.session.commit()
            return make_response(jsonify({'message': 'user updated'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error updating user'}), 500)

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error deleting user'}), 500)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
