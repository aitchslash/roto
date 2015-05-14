import psycopg2
from db_setup import Base, Player, Batting, User
from sqlalchemy import create_engine  # , union
from sqlalchemy.orm import sessionmaker
import pickle


engine = create_engine('postgresql://ben:superstar@localhost/roto', echo=True)  # convert_unicode = True
# engine = create_engine('mysql://root:@localhost:3306/lahman14', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# ## testing team page query ###
def getTeamData(teamID):
    # old working line but want name/age/etc.
    # team_batting_data = session.query(Player.lahmanID, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID).all()
    team_batting_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID).all()
    return team_batting_data


def getTeamData2(teamID, user_id):
    # gets a result, not yet examined.
    # tbd = session.query(Player, Batting).outerjoin(Batting).filter(user_id != Batting.user).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID).all()
    # limit to 2015 for examination
    # tbd = session.query(Player, Batting).outerjoin(Batting).filter(Batting.user == user_id).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).all()
    # tbd = session.query(Player, Batting).outerjoin(Batting, Batting.user == user_id).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).all()
    # user_batting_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.user == user_id, Batting.yearID == 2015).all()
    # team_batting_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.user == 1, Batting.yearID == 2015).all()

    # ### ENOUGH HERE FOR WORKING KLUDGE ### #

    # all_ids = session.query(Batting.lahmanID, Batting.user).join(Player).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).filter(or_(Batting.user == user_id, Batting.user == 1)).all()
    # user_made_ids = session.query(Batting.lahmanID).join(Player).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.user == user_id, Batting.yearID == 2015).all()
    user_made_ids_sq = session.query(Batting.lahmanID).join(Player).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.user == user_id, Batting.yearID == 2015).subquery()
    # non_overlap = session.query(Batting.lahmanID).join(Player).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).filter(Batting.user == 1).filter(~Batting.lahmanID.in_(user_made_ids)).all()
    non_overlap_sq = session.query(Batting.lahmanID).join(Player).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).filter(Batting.user == 1).filter(~Batting.lahmanID.in_(user_made_ids_sq)).subquery()
    non_overlap_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID).filter(~Batting.lahmanID.in_(user_made_ids_sq)).filter(Player.teamID == teamID, Batting.yearID == 2015)  # .all()
    # non_overlap_data_sq = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID).filter(~Batting.lahmanID.in_(user_made_ids_sq)).filter(Player.teamID == teamID, Batting.yearID == 2015).subquery()
    user_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.user == user_id, Batting.yearID == 2015)  # .all()
    team_data = user_data.union(non_overlap_data).all()
    # tester = session.query(Batting.lahmanID, Batting.user).join(Player).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).filter((Batting.user == user_id) | ((Batting.user == 1).filter(~Batting.lahmanID.in_(user_made_ids)))).all()
    # trial = session.query(Batting.lahmanID, Batting.user).join(Player).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).filter(or_(Batting.user == user_id, Batting.user == 1)).all()
    # perchance = session.query()
    return user_made_ids_sq, non_overlap_sq, non_overlap_data, user_data, team_data


def teamData(teamID, user_id):
    user_made_ids_sq = session.query(Batting.lahmanID).join(Player).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.user == user_id, Batting.yearID == 2015).subquery()
    non_overlap_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID).filter(~Batting.lahmanID.in_(user_made_ids_sq)).filter(Player.teamID == teamID, Batting.yearID == 2015)
    user_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.user == user_id, Batting.yearID == 2015)
    team_data = user_data.union(non_overlap_data).all()
    return team_data


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
                               user_id=1,
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

# ## -- facebook token exchange -- ## #

'''
import httplib2
import requests'''
# url = '''https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=283302008528558&client_secret=4af9c13fda7c5f3ef5c8dcd2cd38dafc&fb_exchange_token=CAAEBqWOVHq4BAFbw4WcdZCoACnnwX8FARaruAPJEmvFliKidYxFeZCaJqj05qHFA7gXgByLZB4DXqpoZBdKzEFkLiVqU1UMiGYiOufCb1iBLyJCHZCuamsgZBpS0VfTKxZAZBmQgPBNPlZBm5ZBlX5XAp7oyKl8ZCwIElhwcg00ZCXaPpZCBf98DFCQY6OkRVHwaMDCEsgoIjtuCtgGFtRNNdYWZCygYpGQIyC2foZD'''


'''
joeyBats = 'bautijo02'
jays_dict = getJays()

joeyObject = Player(lahmanID=joeyBats,
                    dob=jays_dict[joeyBats]['dob'],
                    age=jays_dict[joeyBats]['age'],
                    mlbID=jays_dict[joeyBats]['mlbID'],
                    name=jays_dict[joeyBats]['name'])
'''
