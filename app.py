from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import db_session
from data.users import User
from data.access_layer import Access
from data import users_api
from flask_login import LoginManager, login_user, login_required, logout_user
from flask import make_response, jsonify
from requests import get
app = Flask(__name__)
app.config['SECRET_KEY'] = 'DB92086F79CA157AE381C444751FA8'
login_manager = LoginManager()
login_manager.init_app(app)
current_user_id = None
label_job = 'jobs'
redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторить пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/<lang>/logout')
@login_required
def logout(lang):
    global current_user_id
    logout_user()
    current_user_id = None
    return redirect("/" + lang)


@login_manager.user_loader
def load_user(user_id):
    global current_user_id
    session = db_session.create_session()
    current_user_id = user_id
    return session.query(User).get(user_id)


@app.route('/')
def f():
    return redirect("/ru")


@app.route('/<lang>')
def home_page(lang):
    param = {}
    # db_session.global_init("db/blogs.sqlite")
    # session = db_session.create_session()
    # if label_job == 'jobs':
    #     for job in session.query(Jobs).all():
    #         category = session.query(Category).filter(Category.id == job.id).first()
    #         user = session.query(User).filter(User.id == job.team_leader).first()
    #         param['jobs'] = param.get('jobs', []) + [[job.id, job.job, user.surname + ' ' + user.name, job.work_size, job.collaborators, category.name, job.is_finished, job.team_leader]]
    # elif label_job == 'departments':
    #     for job in session.query(Departament).all():
    #         param['jobs'] = param.get('jobs', []) + [[job.id, job.title, job.chief, job.members, job.email]]
    # param['label_job'] = label_job
    param['lang'] = lang
    return render_template('home_page.html', **param)


@app.route('/<lang>/register', methods=['GET', 'POST'])
def register(lang):
    form = RegisterForm()
    db_session.global_init("db/database.sqlite")
    session = db_session.create_session()
    if request.method == 'POST' and form.validate() and form.is_submitted():
        if form.password.data != form.password2.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.login = form.login.data
        user.email = form.email.data
        category = Access()
        category.level = 'new'
        user.access.append(category)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user, remember=False)
        return redirect('/' + lang)
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/<lang>/login', methods=['GET', 'POST'])
def login(lang):
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/" + lang)
        return render_template('login.html', message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


if __name__ == '__main__':
    db_session.global_init("db/database.sqlite")
    app.register_blueprint(users_api.blueprint)
    app.run(port=5000, host='127.0.0.1')
