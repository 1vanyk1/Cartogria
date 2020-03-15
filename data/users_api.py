from flask import jsonify, request
import flask
from data import db_session
from data.users import User
from data.access_layer import Access


blueprint = flask.Blueprint('users_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/users')
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('login', 'email', 'access'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>',  methods=['GET'])
def get_one_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'users': user.to_dict(only=('login', 'email', 'access'))
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['login', 'email']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    user = User()
    user.login = request.json['login']
    user.email = request.json['email']
    category = Access()
    category.name = 'new'
    user.access.append(category)
    session.add(user)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['login', 'email', 'access']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    user.surname = request.json['surname']
    user.name = request.json['name']
    category = session.query(Access).get(user_id)
    category.level = request.json['access']
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    category = session.query(Access).get(user_id)
    session.delete(category)
    session.delete(user)
    session.commit()
    return jsonify({'success': 'OK'})