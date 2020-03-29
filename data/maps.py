import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Map_Object(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'maps'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text_id = sqlalchemy.Column(sqlalchemy.String, unique=True)
    start_date = sqlalchemy.Column(sqlalchemy.String)
    end_date = sqlalchemy.Column(sqlalchemy.String)
    names = sqlalchemy.Column(sqlalchemy.String)
    borders = sqlalchemy.Column(sqlalchemy.String)
    leaders = sqlalchemy.Column(sqlalchemy.String)
    flags = sqlalchemy.Column(sqlalchemy.String)