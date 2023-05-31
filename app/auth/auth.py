from flask import render_template, jsonify, request, redirect, flash, Response
from flask_login import logout_user, current_user, login_user
from app import db, app
from app.model import load_user
import time
from hashlib import sha1
from app.auth import bp
from app.model import User

@app.template_filter('sha1')
def cript(text):
    return sha1(text.encode()).hexdigest()

@bp.route('/login', methods=['POST'])
def username():
    username = request.json['login']
    password = request.json['password']
    remember = True

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return Response(status=400)
    
    login_user(user, remember=remember)
    return jsonify({'message': 'Успешно'})

@bp.route('/signup', methods=['POST'])
def signup_post():
    username = request.json['login']
    password = request.json['password']
    key = request.json['key']
    check = False
    if key == sha1('Fontanka86'.encode()).hexdigest():
        check = True
    for user in db.session.query(User).all():
        if key == sha1(user.username.encode()).hexdigest():
            check = True
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Пользователь с таким именем уже создан'})
    if not check:
        return jsonify({'message': 'Неправильный ключ'})
    new_user = User(username=username)
    new_user.set_password(password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': "Успешно"})

@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect('/')