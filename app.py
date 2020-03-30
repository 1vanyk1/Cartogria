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
import hashlib
import io
from requests import get
import math
from wand.api import library
import wand.color
import wand.image
app = Flask(__name__)
app.config['SECRET_KEY'] = 'DB92086F79CA157AE381C444751FA8'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)
current_user_id = None
redirect("/") #"myDrawing"
# blueprint = flask.Blueprint('main_api', __name__,
#                             template_folder='templates')
#       0   1   2   3   4   5   6   7   8   9   10  11  12
delt = [10, 10, 10, 10, 10, 10, 10, 10, 10, 25, 50, 10, 200]
borders = [[83.03230907439217, 47.22370511070028], [85.55901918847962, 47.05047812901647], [93.7756279333089, 40.67117019527163]]
test = [[85.529764, 47.059125], [83.030796, 47.212243], [79.852264, 44.904618], [80.283950, 42.060340], [76.331270, 40.360061], [93.7756279333089, 40.67117019527163]]


def session_test():
    if 'cord_x' in session:
        session['cord_x'] = 85
    if not 'cord_y' in session:
        session['cord_y'] = 41.3
    if not 'zoom' in session:
        session['zoom'] = 6
    return session['cord_x'], session['cord_y'], session['zoom']


def generate_map(x, y, zoom):
    x = float(x)
    y = float(y)
    zoom = int(zoom)
    delta_y = 445 / (2 ** zoom)
    delta_x = 843 / (2 ** zoom)
    if zoom > 4:
        k = 1
    else:
        k = 6 - zoom
    print(math.cos(math.radians((y - test[1][1]) / 2)))
    #  - (y - i[1]) * (200 / (2 ** (12 - zoom)))
    print(90 - test[1][1], test[1][1], 90 - y, y, (180 - y - test[1][1]) / 2)
    points = [(300 * (delta_x + 2 * i[0] - 2 * x) / delta_x, 225 * (2 * y - 2 * i[1]) / delta_y + 225) for i in test]
    print(points)
    print(y - test[1][1], delta_y)
    print(zoom)
    dwg = svgwrite.Drawing('static/svg/test.svg', profile='tiny')
    dwg.add(dwg.image(insert=(0, 0), size=(600, 450),
                      href=yandex_map_api.get_map_source(str(x), str(y), str(zoom))))
    dwg.add(dwg.rect(insert=(0, 0), size=(600, 450), fill='black', opacity=0, id="delta"))
    dwg.add(dwg.polygon(points=points, fill='black', opacity=0.1))
    # dwg.add(dwg.circle(center=points[1], r=5, fill='black'))
    dwg.add(dwg.circle(center=(test[1][0], 225), r=5, fill='red'))
    dwg.save()


@app.route('/api/get_click_pos/<int:x>/<int:y>', methods=['POST'])
def get_click_pos(x, y):
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
    dwg.save()
    print(x, y)
    return jsonify({'success': 'OK'})


@app.route('/api/get_image.svg')
def get_image():
    if not 'cord_x' in session:
        session['cord_x'] = 85
    if not 'cord_y' in session:
        session['cord_y'] = 41.3
    if not 'zoom' in session:
        session['zoom'] = 6
    dwg = svgwrite.Drawing(profile='tiny', size=(600, 450))
    dwg.add(dwg.image(insert=(0, 0), size=(600, 450),
                      href=yandex_map_api.get_map_source(str(session['cord_x']),
                                                         str(session['cord_y']),
                                                         str(session['zoom']))))
    dwg.add(dwg.rect(id="delta", insert=(0, 0), size=(600, 450), fill='black', opacity=0.5))
    badge = io.StringIO()
    dwg.write(badge)
    response = make_response(badge.getvalue())
    response.headers['Content-Type'] = 'image/svg+xml'
    response.headers['Cache-Control'] = 'no-cache'
    etag = hashlib.sha1(dwg.tostring().encode('utf-8')).hexdigest()
    response.set_etag(etag)
    return response


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
    print(session)
    if n == 1:
        session['zoom'] += 1
    else:
        session['zoom'] -= 1
    if session['zoom'] > 10:
        session['zoom'] = 10
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
    generate_map(str(session['cord_x']), str(session['cord_y']), str(session['zoom']))
    param['res'] = get('http://localhost:5000/api/get_image.svg')
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
