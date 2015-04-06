import psycopg2
from db_setup import Base, Player, Batting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pickle


engine = create_engine('postgresql://ben:superstar@localhost/roto', echo=True)  # convert_unicode = True
# engine = create_engine('mysql://root:@localhost:3306/lahman14', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def getTeamFromPickle(filename):
    """ fixes 'insecure pickle string error' via
    a dos2unix bit, then opens the pickle """
    lahm_team_id = filename[-3:]  # needs work
    text = open(filename, 'rb').read().replace('\r\n', '\n')
    open(filename, 'wb').write(text)
    fp = open(filename)
    team_dict = pickle.load(fp)
    fp.close()
    return team_dict, lahm_team_id


def getTeamIDList(filename="mlb/teampkls/l14_teamID_list"):
    # might want to use a with here
    fp = open(filename)
    teamid_list = pickle.load(fp)
    fp.close()
    return teamid_list


def insertPlayersPsql(team_dict, lahm_team_id):
    """ adds players to pqsl master list by team """
    for lahmanID in team_dict:
        player_object = Player(lahmanID=lahmanID,
                               name=team_dict[lahmanID]['name'],
                               age=team_dict[lahmanID]['age'],
                               dob=team_dict[lahmanID]['dob'],
                               mlbID=team_dict[lahmanID]['mlbID'],
                               teamID=lahm_team_id,
                               pos=team_dict[lahmanID]['pos'])
        session.add(player_object)
        session.commit()  # ? is one commit, outside loop, doable/better ?
    print lahm_team_id + ": inserted"


def getJays(filename='mlb/jays_roster.pkl'):
    """ tester, fixes 'insecure pickle string error' via
    a dos2unix bit, then opens the pickle """
    text = open(filename, 'rb').read().replace('\r\n', '\n')
    open(filename, 'wb').write(text)
    fp = open(filename)
    jays_dict = pickle.load(fp)
    fp.close()
    return jays_dict


def getJays2(filename='mlb/jays_roster.pkl'):
    """ tester, fixes 'insecure pickle string error' via
    a dos2unix bit, then opens the pickle """
    text = open('mlb/jays_roster.pkl', 'rb').read().replace('\r\n', '\n')
    open('mlb/jays_roster.pkl', 'wb').write(text)
    fp = open('mlb/jays_roster.pkl')
    jays_dict = pickle.load(fp)
    fp.close()
    return jays_dict


def testJaysInsert(jays_dict):
    for lahmanID in jays_dict:
        player_object = Player(lahmanID=lahmanID,
                               name=jays_dict[lahmanID]['name'],
                               age=jays_dict[lahmanID]['age'],
                               dob=jays_dict[lahmanID]['dob'],
                               mlbID=jays_dict[lahmanID]['mlbID'],
                               pos=jays_dict[lahmanID]['pos'])
        session.add(player_object)
        session.commit()  # ? is one commit, outside loop, doable/better ?
    print "jays inserted"


def deleteAllTest():
    players = session.query(Player).all()
    for player in players:
        session.delete(player)
        session.commit()

'''
joeyBats = 'bautijo02'
jays_dict = getJays()

joeyObject = Player(lahmanID=joeyBats,
                    dob=jays_dict[joeyBats]['dob'],
                    age=jays_dict[joeyBats]['age'],
                    mlbID=jays_dict[joeyBats]['mlbID'],
                    name=jays_dict[joeyBats]['name'])
'''
