import psycopg2
from sqlalchemy import (Column, Integer, String, ForeignKey,
                        MetaData)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

# Player doesn't need user, nb gone
# e.g of a primary foreign key:
# nid = Column(Integer, ForeignKey(Node.nid), primary_key=True)
# link to one-to-one solution (though it's one to many)
# http://stackoverflow.com/questions/24475645/sqlalchemy-one-to-one-relation-primary-as-foreign-key
# determine wtf backref is/does

Base = declarative_base()
metadata = MetaData()  # new, goes w/ import above

'''
class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250, nullable=False)
'''

''' Might want to make tighter restrictions e.g. age=int(2)
    and nullable=False and dob to a datetime '''


class Player(Base):
    __tablename__ = 'master'
    lahmanID = Column(String(9), primary_key=True, nullable=False)
    # user_id = Column(Integer, ForeignKey('user.id'), primary_key=True, nullable=False)  # nb
    name = Column(String)
    age = Column(Integer)
    mlbID = Column(Integer(6))
    dob = Column(String(10))
    pos = Column(String(2))
    teamID = Column(String(3))
    # hitting = relationship("Batting", backref='master')  # to include cascade
    # hitting = relationship("Batting", backref=backref('master', cascade='single_parent=True, all, delete-orphan'))

    ''' need unique refs to user/lahmanID/yearID,
    foreign key to user/lahmanID
    ??? default = 0 for stats or NULL ???
    yearID in batting is SERIAL, problem???
    -- maybe use a default?
    -- maybe remove default from user to make it SERIAL? '''


class Batting(Base):
    __tablename__ = 'batting'
    lahmanID = Column(String(9), ForeignKey('master.lahmanID'), primary_key=True, nullable=False)
    # disabling user, moving to Predictions
    user = Column(Integer, ForeignKey('user.id'), primary_key=True)
    # not sure if primary key need nullable=false, just making sure cascade works
    yearID = Column(Integer(4), primary_key=True)
    teamID = Column(String(3))
    G = Column(Integer(3))
    H = Column(Integer(3))
    AB = Column(Integer(3))
    R = Column(Integer(3))
    doubles = Column(Integer(3))
    triples = Column(Integer(3))
    HR = Column(Integer(2))
    RBI = Column(Integer(3))
    SB = Column(Integer(3))
    CS = Column(Integer(3))
    BB = Column(Integer(3))
    IBB = Column(Integer(3))
    SO = Column(Integer(3))
    HBP = Column(Integer(3))
    GIDP = Column(Integer(3))
    SF = Column(Integer(3))
    SH = Column(Integer(3))
    # trying relationship here, works above
    hitting = relationship(
        Player, backref=backref('master', uselist=True, cascade='delete, all'))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(250))
    name = Column(String(250))
    picture = Column(String(250))

    user_proj = relationship(Batting, backref=backref('batting'))
    # main_id = relationship(Player)


# this is currently garbage
'''
class MasterBattingLink(Base):
    __tablename__ = 'master_batting_link'
    master_user = Column(Integer, primary_key=True)
    master_lahmanID = Column(String(9), primary_key=True)'''
'''ForeignKeyConstraint(
            ['user', 'lahmanID'], ['master.user', 'master.lahmanID'])'''
'''player = relationship(Player)  # nb, this will likely break
    __table_args__ = (
        ForeignKeyConstraint(
            [user, lahmanID], [master.user, master.lahmanID], {})  # {}???
    )'''


# #### insert at end of file ######

engine = create_engine('postgresql://ben:superstar@localhost/roto', echo=True)  # convert_unicode = True

Base.metadata.create_all(engine)
