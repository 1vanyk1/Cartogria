import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Map_Object(SqlAlchemyBase, UserMixin, SerializerMixin):  # Элементы на карте
    __tablename__ = 'maps'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    start_date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    end_date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    names = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    color = sqlalchemy.Column(sqlalchemy.String, default='#000000')
    borders = sqlalchemy.Column(sqlalchemy.String)
    leaders = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    leaders_names = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    flags = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    capitals = sqlalchemy.Column(sqlalchemy.String, nullable=True)