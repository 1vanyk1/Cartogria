from flask import Flask, render_template, redirect, request, Response
try:  # Импортирование заголовков
    from flask_headers import headers
except BaseException:
    from flask.ext.headers import headers
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import db_session, users_api
from data.users import User
from data.access_layer import Access
from data.user_position import Position
from data.maps import Map_Object
from data.marks import Mark_Object
from data.dates_comparisons import date_more_or_equal, date_less_or_equal, date_less, date_equal, date_more
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import make_response, jsonify
from data import yandex_map_api
import datetime
import svgwrite
app = Flask(__name__)
app.config['SECRET_KEY'] = 'DB92086F79CA157AE381C444751FA8'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)
current_user_id = None
redirect("/")
hexs = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'a': 10,
        'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}  # Для конверта 16-ричных чисел в 10-ричные
rgbs = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'a',
        11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}  # Для конверта 10-ричных чисел в 16-ричные


def convert_cords2xy(x, y, cord_x, cord_y, zoom):  # Конвертирование географических координат в
    delta_x = 843 / (2 ** zoom)                    # координаты на плоскости
    cord_x, cord_y = float(cord_x), float(cord_y)
    return [600 * (cord_x - x) / delta_x + 300,
            90 * (y - cord_y) / (180 - y - cord_y) * (2 ** zoom) + 225]


def convert_xy2cords(x, y, pos_x, pos_y, zoom):  # Конвертирование координат на плоскости в
    delta_x = 843 / (2 ** zoom)                  # географические координаты
    return ((delta_x * (pos_x - 300)) / 600 + x,
            (40500 - 180 * pos_y - 450 * y + 2 * pos_y * y) / (90 * (2 ** zoom) + 225 - pos_y) + y)


def arithmetic_mean_arrays(array1, array2):  # Ср. ариф. элементов одного массива с соответствующими
    return [(n1 + array2[i]) / 2 for i, n1 in enumerate(array1)]  # элементоми другого массива


def convert_hex2rgb(hexx):  # Конвертирование 16-ричных чисел в 10-ричные
    return hexs[hexx[0]] * 16 + hexs[hexx[1]]


def convert_rgb2hex(rgb):  # Конвертирование 0-ричных чисел в 16-ричные
    return rgbs[rgb // 16] + rgbs[rgb % 16]


def check_shape(shape):  # Проверка фигуры на правильность
    res = [i for i in shape if -85 < i[1] < 85]
    return res, res != shape


def load_current_map(date):  # Загрузка карты из базы данных
    session = db_session.create_session()
    date = list(map(int, date.split('.')))  # Дата пользователя
    objects_res, ids, colors, names = [], [], [], []
    try:
        objs = session.query(Map_Object).all()
    except BaseException:  # Если нет никаких элементов в базе данных то мы отправляем пустые данные
        return [[], [], [], []]
    for obj in list(objs):
        try:  # У каждого объекта определяем начальную...
            obj_start = list(map(int, obj.start_date.split('.')))
        except BaseException:
            obj_start = [1, 1, 1]
        try:  # ... и конечную даты
            obj_end = list(map(int, obj.end_date.split('.')))
        except BaseException:
            obj_end = [10000, 1, 1]  # Если объект подходит по датам \/
        if date_more_or_equal(date, obj_start) and date_less_or_equal(date, obj_end):
            borders = list([list(map(int, i[0].split('.'))), i[1].split(';')] for i in
                           map(lambda x: x.split(':'), obj.borders.split('|')))
            t = True  # /\ То мы определяем о нём информацию
            t_check = False
            for i in range(len(borders) - 1):  # Смотрим каждый элемент
                if date_more_or_equal(date, borders[i][0]) and date_less(date, borders[i + 1][0]):
                    if borders[i][1] not in ['', None]:  # И если он подходит, то мы его добавляем
                        ids.append(obj.id)
                        colors.append(obj.color)
                        res, t_check = check_shape(list(map(lambda x: list(
                            map(float, x.split(','))), borders[i][1])))
                        if t_check:
                            borders[i][1] = list(map(lambda x: ','.join(list(map(str, x))), res))
                        objects_res.append(res)
                    t = False
                    break
            if t and borders[-1][1] not in ['', None]:  # Если ни кто не прошёл 1 условие, то
                ids.append(obj.id)  # смотрим на последний элемент, если он
                colors.append(obj.color)  # подходит, то его добавляем
                res, t_check = check_shape(list(map(lambda x: list(
                    map(float, x.split(','))), borders[-1][1])))
                if t_check:
                    borders[-1][1] = list(map(lambda x: ','.join(list(map(str, x))), res))
                objects_res.append(res)
            # Определяем имя объекта
            if obj.names is None:  # Если имён нет
                names.append('')
            else:
                names_obj = list([list(map(int, i[0].split('.'))), i[1]] for i in map(
                    lambda x: x.split(':'), obj.names.split('|')))
                t = True
                for i in range(len(names_obj) - 1):  # Смотрим каждый элемент
                    if date_more_or_equal(date, names_obj[i][0]) and date_less(date,
                                                                               names_obj[i + 1][0]):
                        if names_obj[i][1] not in ['', None]:
                            names.append(names_obj[i][1])
                        t = False
                        break
                if t and names_obj[-1][1] not in ['', None]:
                    names.append(names_obj[-1][1])
            if t_check:
                obj.borders = '|'.join(':'.join(['.'.join(
                    map(str, i[0])), ';'.join(i[1])]) for i in borders)
                session.commit()
    return [objects_res, ids, colors, names]


def load_current_marks(date):  # Загружаем метки на карте по датам
    session = db_session.create_session()
    date = list(map(int, date.split('.')))
    objects_res = []
    ids = []
    try:
        objs = session.query(Mark_Object).all()
    except BaseException:  # Если нет никаких элементов в базе данных то мы отправляем пустые данные
        return [[], []]
    for obj in list(objs):  # Определяем начальную и конечную даты
        obj_start = list(map(int, obj.start_date.split('.')))
        try:
            obj_end = list(map(int, obj.end_date.split('.')))
        except BaseException:
            obj_end = obj_start
        if date_more_or_equal(date, obj_start) and date_less_or_equal(date, obj_end):
            objects_res.append([obj.x, obj.y])  # Если элемент подходит, то мы его добавляем
            ids.append(obj.id)
    return [objects_res, ids]


def change_point_of_elem(elem_id, point_id, points, date):  # Изменяем посицию вершины элемента
    session = db_session.create_session()
    date = list(map(int, date.split('.')))
    obj = session.query(Map_Object).filter(Map_Object.id == elem_id).first()
    borders = list([list(map(int, i[0].split('.'))), i[1].split(';')] for i in
                   map(lambda x: x.split(':'), obj.borders.split('|')))
    t = True  # /\ получаем данные об элементе
    for i in range(len(borders) - 1):  # Определяем по дате \/
        if date_more_or_equal(date, borders[i][0]) and date_less(date, borders[i + 1][0]):
            borders[i][1][point_id] = ','.join(map(str, points))  # И меняем подходящий элемент
            t = False
            break
    if t:  # Если ни что не подходит...
        borders[-1][1][point_id] = ','.join(map(str, points))  # ...то, меняем последний элемент
    obj.borders = '|'.join(':'.join(['.'.join(map(str, i[0])), ';'.join(i[1])]) for i in borders)
    session.commit()


def add_name_of_elem(elem_id, date, name):  # Добавляем название элементу
    session = db_session.create_session()
    date = list(map(int, date.split('.')))
    obj = session.query(Map_Object).filter(Map_Object.id == elem_id).first()
    t = True
    if obj.names is None:  # Если имён нет
        names_obj = [[list(map(int, obj.start_date.split('.'))), name]]
        t = False
    else:
        names_obj = list([list(map(int, i[0].split('.'))), i[1]] for i in map(
            lambda x: x.split(':'), obj.names.split('|')))
        for i in range(len(names_obj) - 1):  # Определяем какой сейчас элемент мы видим...
            if date_equal(date, names_obj[i][0]):
                return
            if date_more(date, names_obj[i][0]) and date_less(date, names_obj[i + 1][0]):
                names_obj.insert(i + 1, [date, name])  # ...и добавляем ему название
                t = False
                break
    if t:
        if date_equal(date, names_obj[-1][0]):
            return
        names_obj.insert(len(names_obj), [date, name])  # ...и добавляем ему название
    obj.names = '|'.join(':'.join(['.'.join(map(str, i[0])), i[1]]) for i in names_obj)
    session.commit()


def change_name_of_elem(elem_id, date, name):  # Изменяем название элементу
    session = db_session.create_session()
    date = list(map(int, date.split('.')))
    obj = session.query(Map_Object).filter(Map_Object.id == elem_id).first()
    t = True
    if obj.names is None:  # Если имён нет
        names_obj = [[list(map(int, obj.start_date.split('.'))), name]]
        t = False
    else:
        names_obj = list([list(map(int, i[0].split('.'))), i[1]] for i in map(
            lambda x: x.split(':'), obj.names.split('|')))
        for i in range(len(names_obj) - 1):  # Определяем какой сейчас элемент мы видим...
            if date_more(date, names_obj[i][0]) and date_less(date, names_obj[i + 1][0]):
                names_obj[i][1] = name  # ...и меняем ему название
                t = False
                break
    if t:
        names_obj[-1][1] = name  # ...и меняем ему название
    obj.names = '|'.join(':'.join(['.'.join(map(str, i[0])), i[1]]) for i in names_obj)
    session.commit()


def add_frame_of_elem(elem_id, date):  # Добавляем "кадр" элемента
    session = db_session.create_session()
    date = list(map(int, date.split('.')))
    obj = session.query(Map_Object).filter(Map_Object.id == elem_id).first()
    borders = list([list(map(int, i[0].split('.'))), i[1].split(';')] for i in map(
        lambda x: x.split(':'), obj.borders.split('|')))
    t = True
    for i in range(len(borders) - 1):  # Определяем какой сейчас элемент мы видим...
        if date_equal(date, borders[i][0]):
            return
        if date_more(date, borders[i][0]) and date_less(date, borders[i + 1][0]):
            borders.insert(i + 1, [date, borders[i][1]])
            t = False
            break
    if t:
        if date_equal(date, borders[-1][0]):
            return
        borders.insert(len(borders), [date, borders[-1][1]])  # ...и его копируем
    obj.borders = '|'.join(':'.join(['.'.join(map(str, i[0])), ';'.join(i[1])]) for i in borders)
    session.commit()


def insert_point_of_elem(elem_id, point_id, points, date):  # Добавляем вершину
    session = db_session.create_session()
    date = list(map(int, date.split('.')))
    obj = session.query(Map_Object).filter(Map_Object.id == elem_id).first()
    borders = list([list(map(int, i[0].split('.'))), i[1].split(';')] for i in map(
        lambda x: x.split(':'), obj.borders.split('|')))
    t = True
    for i in range(len(borders) - 1):  # Находим подходящий "кадр"
        if date_more_or_equal(date, borders[i][0]) and date_less(date, borders[i + 1][0]):
            borders[i][1].insert(point_id, ','.join(map(str, points)))
            t = False  # и добовляем в него вершину /\
            break
    if t:  # НЕ ОБРАЩАЙТЕ ВНИМАНИЕ НА PEP8. Если это "исправить", то будут возникать ошибки
        borders[-1][1].insert(point_id, ','.join(map(str, points)))
    obj.borders = '|'.join(':'.join(['.'.join(map(str, i[0])), ';'.join(i[1])]) for i in borders)
    session.commit()


def remove_point_of_elem(elem_id, point_id, date):  # Удаление вершины
    session = db_session.create_session()
    date = list(map(int, date.split('.')))
    obj = session.query(Map_Object).filter(Map_Object.id == elem_id).first()
    borders = list([list(map(int, i[0].split('.'))), i[1].split(';')] for i in map(
        lambda x: x.split(':'), obj.borders.split('|')))
    t = True
    for i in range(len(borders) - 1):  # ...определяем нужную позицию и удаляем
        if date_more_or_equal(date, borders[i][0]) and date_less(date, borders[i + 1][0]):
            borders[i][1].pop(point_id)
            t = False
            break
    if t:
        borders[-1][1].pop(point_id)
    obj.borders = '|'.join(':'.join(['.'.join(map(str, i[0])), ';'.join(i[1])]) for i in borders)
    session.commit()


def generate_map(x, y, zoom, user_id):  # Создаём карту
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    if not position.map_loading:
        position.map_loading = True  # Проверка на то, создаётся ли карта, если нет, то продолжаем
        session.commit()
        current_map = load_current_map(position.date)  # Загружаем информацию о карте
        borders, ids, colors, names = current_map[0], current_map[1], current_map[2], current_map[3]
        current_marks = load_current_marks(position.date)  # И о метках
        marks, ids_m = current_marks[0], current_marks[1]
        if position.elem_id not in ids and position.elem_id is not None:
            position.elem_id = None  # Снимаем выделение, если нет элемента
            position.point_id = None
            session.commit()
        if position.point_id not in ids_m and position.point_id is not None:
            position.point_id = None  # Снимаем выделение, если нет метки
            session.commit()
        x, y, zoom = float(x), float(y), int(zoom)  # Позиция пользователя
        dwg = svgwrite.Drawing(f'static/svg/{user_id}.svg', profile='tiny')
        p, p2, rounds = [], [], []          # /\ Файл с обрабоанной карты
        r, g, b, name = '00', '00', '00', ''
        t = position.status == 2 and position.points is not None and position.points != ''
        if t:  # /\ Редактируем ли мы регион
            shape = position.points.split(',')
            points1 = [convert_cords2xy(x, y, float(shape[i * 2]), float(shape[i * 2 + 1]), zoom)
                       for i in range(len(shape) // 2)]
            t = t and(not(all([i[0] > 600 for i in points1]) or all([i[0] < 0 for i in points1]) or
                          all([i[1] > 450 for i in points1]) or all([i[1] < 0 for i in points1])))
            if t:  # Если регион на карте, то его добавляем
                dwg.add(dwg.polygon(points=points1, fill='black', fill_opacity=0.1, stroke="black",
                                    stroke_width="2"))
        dwg.add(dwg.rect(insert=(0, 0), size=(600, 450), fill='black', opacity=0, id='delta'))
        t2 = False
        ids2 = []
        for nn, shape in enumerate(borders):
            points = [convert_cords2xy(x, y, i[0], i[1], zoom) for i in shape]
            center_points = [arithmetic_mean_arrays(points[i], points[i - 1]) for i in
                             range(len(shape))]  # Если регион на карте, то его добавляем
            if not(all([i[0] > 600 for i in points]) or all([i[0] < 0 for i in points]) or
                   all([i[1] > 450 for i in points]) or all([i[1] < 0 for i in points])):
                dwg.add(dwg.polygon(points=points, fill=colors[nn], opacity=0.25, stroke=colors[nn],
                                    stroke_width="2", id='a' + str(ids[nn])))
                ids2.append(ids[nn])
                if position.elem_id == ids[nn]:
                    t2 = True  # Если этот регион выделен, то получаем его данные
                    p = points
                    p2 = center_points
                    r, g, b, name = colors[nn][1:3], colors[nn][3:5], colors[nn][5:7], names[nn]
                rounds.append(points)
        ids = ids2
        if position.status in [0, 1] and position.elem_id is not None and t2:
            dwg.add(dwg.polygon(points=p, stroke="white", fill="none",
                                stroke_width="2", id='a' + str(position.elem_id)))
            if position.status == 1:  # Если регион выбран при редактировании, то добавляем точки
                for i in range(len(p)):
                    dwg.add(dwg.circle(center=p[i], r=3, fill='white', stroke="black",
                                       stroke_width="1", id='b' + str(i)))
                    dwg.add(dwg.circle(center=p2[i], r=3, fill='grey', id='c' + str(i)))
        if t:  # Добавляем ли мы регион? Если да, то добавляем последнюю вершину (\/ ТУТ ОШИБКИ НЕТ)
            dwg.add(dwg.circle(center=points1[-1], r=3, fill='red', id='last_point'))
        ids_m2 = []
        for nn, mark in enumerate(marks):  # Добавляем метки
            point = convert_cords2xy(x, y, mark[0], mark[1], zoom)
            if 0 < point[0] < 600 and 0 < point[1] < 450:  # Если регион на карте, то его добавляем
                if position.elem_id is None and position.point_id == ids_m[nn]:
                    dwg.add(dwg.circle(center=point, r=5, fill='blue', stroke="white",
                                       stroke_width="3", id='m' + str(ids_m[nn])))
                else:
                    dwg.add(dwg.circle(center=point, r=5, fill='white', stroke="blue",
                                       stroke_width="3", id='m' + str(ids_m[nn])))
                ids_m2.append(ids_m[nn])
        ids_m = ids_m2
        dwg.save()  # Сохраняем карту
        position.map_loading = False
        session.commit()
        return [p, p2, rounds, ids, r, g, b, ids_m, name]
    return []


@app.route('/api/move_point/<int:x>/<int:y>/<cord_x>/<cord_y>/<int:zoom>/<int:user_id>/<points>',
           methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def move_point(x, y, cord_x, cord_y, zoom, user_id, points):  # Перемещаем вершину
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    if position.point_id is not None:
        points = points.split(',')
        for i in range(len(points) // 2):
            if int(x) < float(points[2 * i]) + 5 < int(x) + 10 and int(y) < float(
                    points[2 * i + 1]) + 5 < int(y) + 10:
                x, y = points[2 * i], points[2 * i + 1]
                break  # Если рядом есть точка, то их соединяем
        change_point_of_elem(position.elem_id, position.point_id, list(convert_xy2cords(
            float(cord_x), float(cord_y), float(x), float(y), zoom)), position.date)
        session.commit()  # /\ Перемещаем вершину
        p = generate_map(cord_x, cord_y, zoom, user_id)  # Обновляем точку
        position.point_id = None
        if p:
            return jsonify({'res': True})
    return jsonify({'res': False})


@app.route('/api/end_adding_shape/<int:added>/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def end_adding_shape(added, user_id):  # Добавляем фигуру
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    if position.points is None or position.points == '':  # Если фигура "пустая" (её нет)...
        position.status = 1                               # ...то мы отменяем добавление
        position.elem_id = None
        position.points = None
        session.commit()
        return jsonify({'success': 'OK'})
    points = position.points.split(',')
    position.status = 1
    position.elem_id = None
    position.points = None
    session.commit()
    if added == 1:
        obj = Map_Object()  # Добавляем объект на карту
        obj.start_date = position.date
        obj.borders = ':'.join([position.date, ';'.join([','.join(
            [str(float(points[i * 2])), str(float(points[i * 2 + 1]))]) for i in range(
            len(points) // 2)])])
        session.add(obj)
        session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/remove_shape/<int:elem_selected>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def remove_shape(elem_selected):  # Удаляем фигуру
    session = db_session.create_session()
    obj = session.query(Map_Object).filter(Map_Object.id == elem_selected).first()
    session.delete(obj)
    session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/add_frame/<int:elem_selected>/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def add_frame(elem_selected, user_id):  # Добавляем "кадр"
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    add_frame_of_elem(elem_selected, position.date)
    return jsonify({'success': 'OK'})


@app.route('/api/remove_mark/<int:elem_selected>/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def remove_mark(elem_selected, user_id):  # Удаляем метку
    session = db_session.create_session()
    obj = session.query(Mark_Object).filter(Mark_Object.id == elem_selected).first()
    session.delete(obj)
    position = session.query(Position).filter(Position.id == user_id).first()
    position.point_id = None  # И снимаем выделение с этой метки
    session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/add_new_point/<int:x>/<int:y>/<cord_x>/<cord_y>/<int:zoom>/<int:user_id>/<points>',
           methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def add_new_point(x, y, cord_x, cord_y, zoom, user_id, points):  # Добавление новая вершины у фигуры
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    points = points.split(',')
    for i in range(len(points) // 2):
        if int(x) < float(points[2 * i]) + 5 < int(x) + 10 and int(y) < float(
                points[2 * i + 1]) + 5 < int(y) + 10:
            x, y = points[2 * i], points[2 * i + 1]  # Если есть рядом точка, то их связываем
            break
    if position.points is None:  # Добавляем вершину
        position.points = ','.join(map(str, convert_xy2cords(float(cord_x), float(cord_y),
                                                             float(x), float(y), zoom)))
    else:
        position.points += ',' + ','.join(map(str, convert_xy2cords(float(cord_x), float(cord_y),
                                                                    float(x), float(y), zoom)))
    session.commit()
    p = generate_map(cord_x, cord_y, zoom, user_id)  # Обновляем карту
    if p:
        return jsonify({'res': True})
    return jsonify({'res': False})


@app.route('/api/add_new_mark/<int:x>/<int:y>/<cord_x>/<cord_y>/<int:zoom>/<int:user_id>',
           methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def add_new_mark(x, y, cord_x, cord_y, zoom, user_id):  # Добавляем новую метку
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    pos = convert_xy2cords(float(cord_x), float(cord_y), float(x), float(y), zoom)
    obj = Mark_Object()
    obj.start_date = position.date
    obj.end_date = position.date
    obj.x = str(pos[0])
    obj.y = str(pos[1])
    session.add(obj)
    session.commit()
    return jsonify({'res': True})


@app.route('/api/select_item/<int:elem_id>/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def select_item(elem_id, user_id):  # Выделить элемент
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    position.elem_id = elem_id
    position.point_id = None
    session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/click_on_mark/<int:elem_id>/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def click_on_mark(elem_id, user_id):  # Выделение метки
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    position.point_id = elem_id
    session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/set_moving_point/<int:elem_id>/<int:point_id>/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def set_moving_point(elem_id, point_id, user_id):  # Начинаем перемещать вершину
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    if position:
        position.elem_id = elem_id
        position.point_id = point_id
        session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/change_color/<int:color>/<value>/<int:elem_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def change_color(color, value, elem_id):  # Изменяем цвет элемента
    session = db_session.create_session()
    obj = session.query(Map_Object).filter(Map_Object.id == elem_id).first()
    obj_color = obj.color
    obj_color = obj_color[:color * 2 - 1] + convert_rgb2hex(
        int(float(value))) + obj_color[color * 2 + 1:]  # Изменяем цвет
    obj.color = obj_color
    session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/change_status/<int:status>/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def change_status(status, user_id):  # Изменяем меню пользователя
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    if position:
        position.status = status
        position.elem_id = None
        session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/remove_last_point/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def remove_last_point(user_id):  # Удаляем последнюю точку при редактировании региона
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    if position:
        position.points = ','.join(position.points.split(',')[:-2])
        session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/delete_point/<int:elem_id>/<int:point_id>/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def delete_point(elem_id, point_id, user_id):  # Удаляем вершину
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    remove_point_of_elem(elem_id, point_id, position.date)
    return jsonify({'success': 'OK'})


@app.route('/api/add_moving_point/<int:elem_id>/<int:point_id>/<int:user_id>/<cord_x>/<cord_y>',
           methods=['POST'])
def add_moving_point(elem_id, point_id, user_id, cord_x, cord_y):  # Добавляем вершину элементу...
    session = db_session.create_session()                          # ...который уже создан...
    position = session.query(Position).filter(Position.id == user_id).first()
    if position:                                                   # ... и начинаем перемещать
        insert_point_of_elem(elem_id, point_id, [cord_x, cord_y], position.date)
        position.elem_id = elem_id  # /\ Добавляем вершину
        position.point_id = point_id
        session.commit()
    return jsonify({'success': 'OK'})


@app.route('/api/remove_moving_point/<int:user_id>', methods=['POST'])
@headers({'Access-Control-Allow-Origin': "http://127.0.0.1:5000",
          "Access-Control-Allow-Methods": "POST, GET, OPTIONS, PUT, DELETE",
          "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization, X-",
          'Content-Type': 'application/json'})
def remove_moving_point(user_id):  # Перестоть редактировать метку/вершину
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == user_id).first()
    if position:
        position.elem_id = None
        position.point_id = None
        session.commit()
    return jsonify({'success': 'OK'})


@app.errorhandler(404)
def not_found(error):  # Обработка ошибок
    return make_response(jsonify({'error': 'Not found'}), 404)


class RegisterForm(FlaskForm):  # Регистрация пользователя
    email = EmailField('Email', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторить пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):  # Вход пользователя
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/<lang>/logout')  # Выход из профиля
@login_required
def logout(lang):
    global current_user_id
    logout_user()
    current_user_id = None
    return redirect("/" + lang)


@login_manager.user_loader
def load_user(user_id):  # Когда загружается пользователь
    global current_user_id
    session = db_session.create_session()
    current_user_id = user_id
    return session.query(User).get(user_id)


@app.route('/')
def f():  # Переход на главную страницу
    return redirect("/ru")


@app.route('/<lang>/move/<int:side>')
def move_map(lang, side):  # Перемещаем карту
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == current_user.id).first()
    cord_x = float(position.x)  # Получаем координаты и...
    cord_y = float(position.y)  # ...в зависимости от направления и zoom меняем их
    if side in [0, 2]:
        if side == 2:   # Перемещаем карту вниз...
            cord_y -= 10 * (0.1 ** (position.zoom // 2 - 2))
            if cord_y < -85:
                cord_y = -85
        else:  # ... и вверх до упора
            cord_y += 10 * (0.1 ** (position.zoom // 2 - 2))
            if cord_y > 85:
                cord_y = 85
    else:
        if side == 1:  # Перемещаем карту влево...
            cord_x += 10 * (0.1 ** (position.zoom // 2 - 2))
        else:  # ... вправо
            cord_x -= 10 * (0.1 ** (position.zoom // 2 - 2))
        cord_x = (cord_x + 180) % 360 - 180
    if position:  # И сохраняем
        position.x = str(cord_x)
        position.y = str(cord_y)
        session.commit()
    return redirect("/" + lang)


def check_date(date):
    date = list(map(int, date))
    if date_less(date, [1931, 2, 20]):
        date = [1931, 2, 20]
    elif date_more(date, [1932, 12, 31]):
        date = [1932, 12, 31]
    date = list(map(str, map(int, date)))
    date[1] = '0' * (2 - len(date[1])) + date[1]
    date[2] = '0' * (2 - len(date[2])) + date[2]
    return date


@app.route('/<lang>/change_date/<int:part>/<int:value>')
def change_date(lang, part, value):  # Меняем дату пользователя
    if value == 2:
        value = -1
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == current_user.id).first()
    date = list(map(int, position.date.split('.')))
    date[part] = date[part] + value  # Изменяем
    da = {0: 31, 1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30,
          12: 31}
    if part == 2:  # Далее обрабатываем в зависимости от даты
        if date[2] > da[date[1]]:  # Если дней >, чем в месяце, то переходим к следующему месяцу
            date[1] += date[2] // da[date[1]]
            date[2] = 1
    if date[2] <= 0:  # А если номер дня меньше 1, то к предыдущему
        date[2] = da[date[1] - 1]
        date[1] -= 1
    date[0] += (date[1] - 1) // 12  # Меняем год, если номер месяца не между 1 и 12
    date[1] = (date[1] - 1) % 12 + 1
    if date[2] > da[date[1]]:  # Если дней >, чем в месяце, то переходим к следующему месяцу
        date[2] = da[date[1]]  # (2 проверка на всякий случай)
    print(date)
    position.date = '.'.join(check_date(date)) # Конвертируем обратно
    session.commit()  # Сохраняем изменения
    return redirect("/" + lang)


@app.after_request
def add_header(response):  # Да, да... Тут тоже заголовки, без них не будет менятся изображение
    response.cache_control.no_store = True
    response.cache_control.public = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/<lang>/change_zoom/<int:n>')
def change_zoom(lang, n):  # Меняем zoom
    session = db_session.create_session()
    position = session.query(Position).filter(Position.id == current_user.id).first()
    zoom = position.zoom  # Изменяем...
    if n == 1:
        zoom += 1
    else:
        zoom -= 1
    if zoom > 10:  # Если не попадает в промежуток, то исправляем
        zoom = 10
    elif zoom < 3:
        zoom = 3
    position.zoom = zoom
    session.commit()  # Сохраняем
    return redirect("/" + lang)


@app.route('/<lang>', methods=['POST', 'GET'])
def home_page(lang):
    if not current_user.is_authenticated:  # Если пользователь не зарегистрирован, то регистрируем
        return redirect("/" + lang + "/login")
    session = db_session.create_session()
    position = session.query(Position).get(current_user.id)
    param = {}
    if request.method == 'POST':
        if request.form['submit_button'] == 'mark_change':  # Если мы изменяем метку, то...
            mark = session.query(Mark_Object).filter(Mark_Object.id == position.point_id).first()
            if mark:  # ... сохраняем изменения
                mark.name = request.form['name']
                mark.text = request.form['about']
                mark.end_date = '.'.join(request.form['trip-end'].split('-'))
        elif request.form['submit_button'] == 'shape_change':  # Если мы изменяем элемент, то...
            obj = session.query(Map_Object).filter(Map_Object.id == position.elem_id).first()
            obj.color = '#' + ''.join(convert_rgb2hex(int(float(request.form[i]))) for i in
                                      ['r', 'g', 'b'])
        elif request.form['submit_button'] == 'shape_name_change':  # Если мы изменяем название, то
            if position.elem_id is not None:
                if request.form.get('accept'):
                    add_name_of_elem(position.elem_id, position.date, request.form['name'])
                else:
                    change_name_of_elem(position.elem_id, position.date, request.form['name'])
        elif request.form['submit_button'] == 'date_change':  # Если мы изменяем название, то
            position.date = '.'.join(check_date(request.form['trip-date'].split('-')))
    position.map_loading = False
    session.commit()
    param['access'] = session.query(Access).get(current_user.id).level
    param['lang'] = lang
    param['map'] = yandex_map_api.get_map_source(position.x, position.y, str(position.zoom))
    p = generate_map(position.x, position.y, str(position.zoom), current_user.id)
    if p:  # /\ Генерируем карту | Если на карте есть объекты, то получаем их данные \/
        param['points'] = p[0]
        param['center_points'] = p[1]
        param['rounds'] = p[2]
        if not p[2]:
            param['rounds'] = [-1]
        param['count_of_pols'] = p[3]
        param['r'], param['g'], param['b'] = convert_hex2rgb(p[4]), convert_hex2rgb(p[5]), \
                                             convert_hex2rgb(p[6])
        param['elem_selected'] = position.elem_id
        param['point_selected'] = position.point_id
        param['mark_ids'] = p[7]
        param['name_elem'] = p[8]
    else:  # А если нет, то \/
        param['points'] = []
        param['center_points'] = []
        param['rounds'] = [-1]
        param['count_of_pols'] = []
        param['r'], param['g'], param['b'] = '00', '00', '00'
        param['elem_selected'] = -1
        param['point_selected'] = -1
        param['mark_ids'] = []
        param['name_elem'] = ''
    param['cord_x'] = position.x
    param['cord_y'] = position.y
    param['zoom'] = position.zoom
    param['date'] = '-'.join(position.date.split('.'))
    param['user_id'] = current_user.id
    param['bg_map'] = yandex_map_api.get_map_source(param['cord_x'], param['cord_y'],
                                                    str(param['zoom']))
    param['status'] = position.status  # /\ Берём карту из Яндекс.Карт
    if param['access'] == 'new' and param['status'] != 0:
        param['status'] = 0
        position.status = 0
        session.commit()
    if param['elem_selected'] is None:  # Если элемент не выделен, то \/
        param['elem_selected'] = -1
    if param['point_selected'] is None:
        param['point_selected'] = -1
    elif param['point_selected'] != -1:  # Если выбранна метка, то
        mark = session.query(Mark_Object).filter(Mark_Object.id == position.point_id).first()
        if mark:  # Получаем информацию о ней
            if mark.text is None:
                param['text_point'] = ''
            else:
                param['text_point'] = mark.text
            if mark.name is None:
                param['name_point'] = ''
            else:
                param['name_point'] = mark.name
            param['start_date'] = '-'.join(mark.start_date.split('.'))
            if mark.end_date is None:
                param['end_date'] = param['start_date']
            else:
                param['end_date'] = '-'.join(mark.end_date.split('.'))
        else:  # Если не получается получить инфорвацию \/
            param['text_point'] = ''
            param['name_point'] = ''
            param['start_date'] = '1-1-1'
            param['end_date'] = '9999-12-31'
    res = Response(render_template('home_page.html', **param))
    return res  # Запрос


@app.route('/<lang>/register', methods=['GET', 'POST'])  # Регистрация
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
        access = Access()
        access.level = 'new'
        user.access.append(access)
        position = Position()
        user.position.append(position)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user, remember=False)
        return redirect('/' + lang)
    return render_template('register.html', title='Регистрация', form=form, lang=lang)


@app.route('/<lang>/login', methods=['GET', 'POST'])  # Вход
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
    return render_template('login.html', form=form, lang=lang)


if __name__ == '__main__':  # Запуск
    db_session.global_init("db/database.sqlite")
    app.register_blueprint(users_api.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
