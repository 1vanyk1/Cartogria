import sqlalchemy
from .db_session import SqlAlchemyBase
association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('users', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('users.id')),
                                     sqlalchemy.Column('access', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('access.id')))


class Access(SqlAlchemyBase):  # Уровень доступа к базе данных
    __tablename__ = 'access'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    level = sqlalchemy.Column(sqlalchemy.String, default='new')