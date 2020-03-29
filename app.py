from flask import Flask, render_template, redirect, request, session, Response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import db_session, db_map_session, users_api
from data.users import User
from data.access_layer import Access
from flask_login import LoginManager, login_user, login_required, logout_user
from flask import make_response, jsonify
from data import yandex_map_api
import datetime
import svgwrite
import json
import flask
from requests import get
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
app.config['SECRET_KEY'] = 'DB92086F79CA157AE381C444751FA8'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)
current_user_id = None
redirect("/") #"myDrawing"
# blueprint = flask.Blueprint('main_api', __name__,
#                             template_folder='templates')


@app.route('/api/get_click_pos/<int:x>/<int:y>', methods=['POST'])
def edit_user(x, y):
    print(x, y)
    if not 'cord_x' in session:
        session['cord_x'] = 85
    if not 'cord_y' in session:
        session['cord_y'] = 41.3
    if not 'zoom' in session:
        session['zoom'] = 6
    dwg = svgwrite.Drawing('static/svg/test.svg', profile='tiny')
    dwg.add(dwg.image(insert=(0, 0), size=(600, 450), href=yandex_map_api.get_map_source(str(session['cord_x']), str(session['cord_y']),
                                                 str(session['zoom']))))
    dwg.add(dwg.rect(insert=(0, 0), size=(600, 450), fill='black', opacity=0, id="delta"))
    dwg.add(dwg.rect(insert=(x, y), size=(x + 1, y + 1), fill='black', opacity=1, id="delta"))
    dwg.save()
    return jsonify({'success': 'OK'})


# @app.route('/api/get_image', methods=['GET'])
# def edit_user():
#     d = drawSvg.Drawing(200, 100, origin='center')
#
#     d.append(drawSvg.Lines(-80, -45,
#                         70, -49,
#                         95, 49,
#                         -90, 40,
#                         close=False,
#                         fill='#eeee00',
#                         stroke='black'))
#
#     d.append(drawSvg.Rectangle(0, 0, 40, 50, fill='#1248ff'))
#     d.append(drawSvg.Circle(-40, -10, 30,
#                          fill='red', stroke_width=2, stroke='black'))
#
#     p = drawSvg.Path(stroke_width=2, stroke='green',
#                   fill='black', fill_opacity=0.5)
#     p.M(-30, 5)  # Start path at point (-30, 5)
#     p.l(60, 30)  # Draw line to (60, 30)
#     p.h(-70)  # Draw horizontal line to x=-70
#     p.Z()  # Draw line to start
#     d.append(p)
#
#     d.append(drawSvg.ArcLine(60, -20, 20, 60, 270,
#                           stroke='red', stroke_width=5, fill='red', fill_opacity=0.2))
#     d.append(drawSvg.Arc(60, -20, 20, 60, 270, cw=False,
#                       stroke='green', stroke_width=3, fill='none'))
#     d.append(drawSvg.Arc(60, -20, 20, 270, 60, cw=True,
#                       stroke='blue', stroke_width=1, fill='black', fill_opacity=0.3))
#     return d


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


class AddObjectForm(FlaskForm):
    text_id = StringField('Текстовый id', validators=[DataRequired()])
    name = BooleanField('Название')
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


@app.route('/<lang>/move/<int:side>')
def move_map(lang, side):
    if side in [0, 2]:
        if side == 2:
            session['cord_y'] -= 10 * (0.1 ** (session['zoom'] // 2 - 2))
            if session['cord_y'] < -85:
                session['cord_y'] = -85
        else:
            session['cord_y'] += 10 * (0.1 ** (session['zoom'] // 2 - 2))
            if session['cord_y'] > 85:
                session['cord_y'] = 85
    else:
        if side == 1:
            session['cord_x'] += 10 * (0.1 ** (session['zoom'] // 2 - 2))
        else:
            session['cord_x'] -= 10 * (0.1 ** (session['zoom'] // 2 - 2))
        session['cord_x'] = (session['cord_x'] + 180) % 360 - 180
    return redirect("/" + lang)


@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.public = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/<lang>/change_zoom/<int:n>')
def change_zoom(lang, n):
    if n == 1:
        session['zoom'] += 1
    else:
        session['zoom'] -= 1
    if session['zoom'] > 18:
        session['zoom'] = 18
    elif session['zoom'] < 1:
        session['zoom'] = 1
    return redirect("/" + lang)


@app.route('/<lang>')
def home_page(lang):
    if not 'cord_x' in session:
        session['cord_x'] = 85
    if not 'cord_y' in session:
        session['cord_y'] = 41.3
    if not 'zoom' in session:
        session['zoom'] = 6
    param = {}
    param['lang'] = lang
    param['map'] = yandex_map_api.get_map_source(str(session['cord_x']), str(session['cord_y']),
                                                 str(session['zoom']))
    # dwg = svgwrite.Drawing('static/svg/test.svg', profile='tiny')
    # dwg.add(dwg.image(insert=(0, 0), size=(600, 450), href=param['map']))
    # dwg.add(dwg.rect(insert=(0, 0), size=(600, 450), fill='black', opacity=0, id="delta"))
    # dwg.save()
    print(param['map'])
    res = Response(render_template('home_page.html', **param))
    return res


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
    db_map_session.global_init("db/mapbase.sqlite")
    app.register_blueprint(users_api.blueprint)
    app.run(port=5000, host='127.0.0.1')
