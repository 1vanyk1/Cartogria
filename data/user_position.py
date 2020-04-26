import sqlalchemy
from .db_session import SqlAlchemyBase
association_table = sqlalchemy.Table('position', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('users', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('users.id')),
                                     sqlalchemy.Column('positions', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('positions.id')))


class Position(SqlAlchemyBase):  # Положение пользователя на карте
    __tablename__ = 'positions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    x = sqlalchemy.Column(sqlalchemy.String, default='85')
    y = sqlalchemy.Column(sqlalchemy.String, default='41.3')
    zoom = sqlalchemy.Column(sqlalchemy.Integer, default=6)
    date = sqlalchemy.Column(sqlalchemy.String, default='1931.02.20')
    elem_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    point_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    map_loading = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    status = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    points = sqlalchemy.Column(sqlalchemy.String, nullable=True)