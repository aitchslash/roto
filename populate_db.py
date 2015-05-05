import MySQLdb
import psycopg2
import pickle
import pymysql

# ### using user=1 for initial db population ### #

# this works
# db = MySQLdb.connect('192.168.56.1', 'benjamin', 'plutarch', 'lahman14')
# cur = db.cursor()
# statement = "SELECT * FROM batting WHERE playerID = 'pompeda01'"

# let's try using sqlAlchemy with reflection

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.sql import func
from db_setup import Player, Batting, Base, User

# this and related f(x) could be eliminated if a team db and appropriate query were made
from mlbUtils import makeTeamDictMlbLahman, makeTeamPickles, pickleTeamIDs

# make postgresql engine
engine = create_engine('postgresql://ben:superstar@localhost/roto')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# make MySQL engine
engine2 = create_engine('mysql://benjamin:plutarch@192.168.56.1/lahman14',
                        convert_unicode=True, echo=False)
Base2 = declarative_base()
Base2.metadata.reflect(engine2)

DBSession2 = sessionmaker(bind=engine2)
session2 = DBSession2()


class BattingStat(Base2):
    __table__ = Base2.metadata.tables['batting']  # nb, master better, or no diff?


def main():
    """ db roto must be created but empty """
    """ runs through all 30 teams """
    """ populates master list """
    """ adds stats, prediction """

    # make first user
    user_one = User(email="benjamin.field@gmail.com", name="Benjamin Field")
    session.add(user_one)
    session.commit()
    print "user committed"
    # get 30 team list
    pickleTeamIDs()
    makeTeamPickles()
    teamid_list = getTeamIDList()

    # loop through teams
    # could overwrite teamid_list for testing
    for team_abbr in teamid_list:
        team_dict, lahm_team_id = getTeamFromPickle(team_abbr)
        # insert players into master
        insertPlayersPsql(team_dict, team_abbr)
        # add data to psql
        # loop through players
        for player in team_dict:
            player_stats_to_psql(player, team_abbr)
        # may want to put hard fix in here
    print "DONE!"


def getTeamFromPickle(team_abbr):
    """ fixes 'insecure pickle string error' via
    a dos2unix bit, then opens the pickle """
    # lahm_team_id = filename[-3:]  # needs work
    lahm_team_id = team_abbr
    filename = "teampkls/" + team_abbr
    text = open(filename, 'rb').read().replace('\r\n', '\n')
    open(filename, 'wb').write(text)
    fp = open(filename)
    team_dict = pickle.load(fp)
    fp.close()
    return team_dict, lahm_team_id


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


def getTeamIDList(filename="teampkls/l14_teamID_list"):
    # might want to use a with here
    fp = open(filename)
    teamid_list = pickle.load(fp)
    fp.close()
    return teamid_list


# gotta check for stints, and combine if > 1, ick
def player_stats_to_psql(lahmanID, team_abbr):
    # get recent_stats
    recent_stats = session2.query(BattingStat).filter(BattingStat.playerID == lahmanID,
                                                      BattingStat.yearID >= 2012).order_by(BattingStat.yearID).all()
    holder = []  # nb, testing
    if recent_stats:
        mult_stints = []
        for year_data in recent_stats:
            if year_data.stint == 1:
                year_stats = buildBattingObject(lahmanID, year_data)
                session.add(year_stats)
                holder.append(year_stats)
                session.commit()

            # just use stint2 to populate mult_stints
            #   >2 would be a duplicate and not help
            elif year_data.stint == 2:
                holder.pop()  # here?
                # this could be incorporated into the other query
                # BUT I might want to do more stuff and having it
                # seperate may prove useful
                mult_stints.append(year_data.yearID)
                print lahmanID,
                print mult_stints

        # session.commit()  # may want to move this outside func
        # all stint1's have been added, update multistint years
        if mult_stints:
            for year in mult_stints:
                # print "year: " + str(year)
                year_totals = session2.query(BattingStat.playerID,
                                             BattingStat.yearID,
                                             func.sum(BattingStat.G).label('G'),
                                             func.sum(BattingStat.H).label('H'),
                                             func.sum(BattingStat.AB).label('AB'),
                                             func.sum(BattingStat.R).label('R'),
                                             func.sum(getattr(BattingStat, '2B')).label('2B'),
                                             func.sum(getattr(BattingStat, '3B')). label('3B'),
                                             func.sum(BattingStat.HR).label('HR'),
                                             func.sum(BattingStat.RBI).label('RBI'),
                                             func.sum(BattingStat.SB).label('SB'),
                                             func.sum(BattingStat.CS).label('CS'),
                                             func.sum(BattingStat.BB).label('BB'),
                                             func.sum(BattingStat.IBB).label('IBB'),
                                             func.sum(BattingStat.SO).label('SO'),
                                             func.sum(BattingStat.HBP).label('HBP'),
                                             func.sum(BattingStat.GIDP).label('GIDP'),
                                             func.sum(BattingStat.SF).label('SF'),
                                             func.sum(BattingStat.SH).label('SH')
                                             ).filter(BattingStat.yearID == year,
                                                      BattingStat.playerID == lahmanID
                                                      ).group_by(BattingStat.yearID).one()  # screwing w/ this

                # print year_totals.keys()
                year_totals.teamID = team_abbr
                # stats = year_totals.keys()
                # print stats
                # print year_totals.playerID
                # print "year totals type: ",
                # print type(year_totals)
                # print "teamID: ",
                # print year_totals.teamID
                # UPDATE object to be replaced, object_addy
                object_addy = session.query(Batting).filter(Batting.lahmanID == year_totals.playerID,
                                                            Batting.yearID == year).one()
                # print "object_addy is of type: " + str(type(object_addy))

                #  Build Batting object using summed year # *arg lahID = yt.playerID
                #  assign team name as TOT first

                bo = buildBattingObject(year_totals.playerID, year_totals)
                #  Set addy = new object
                #  Session add/commit
                # holder.pop()  # get rid of non-summed year, wrong spot?
                holder.append(bo)  # tester
                # object_addy = bo
                # session.add(object_addy)
                # session.commit()
                session.delete(object_addy)
                session.commit()
                session.add(bo)
                session.commit()

        career_numbers = getCareerNums(lahmanID)
        career_object = buildBattingObject(lahmanID, career_numbers)
        # change year to 0162
        career_object.yearID = 162
        holder.append(career_object)
        session.add(career_object)
        session.commit()
        # add to db

        # make prediction for 2015
        stats_2015 = calc_2015(holder, lahmanID, team_abbr, user=1)
        session.add(stats_2015)
        session.commit()
    else:  # no recent stats - create blank year
        blank_year = calc_2015(holder, lahmanID, team_abbr, user=1)
        session.add(blank_year)
        session.commit()
    return holder  # tester


def calc_2015(holder, lahmanID, team_abbr, weighting14=7, weighting13=5, weighting12=4, career=0, user=1):
    total_weights = weighting14 + weighting13 + weighting12 + career
    weights = {2014: weighting14,
               2013: weighting13,
               2012: weighting12,
               162: career}
    # sort list, result 4 obj, [2014, 2013, 2012, career]
    # nb, hmm what happens for rookies, missing a year etc?
    if holder:
        holder.sort(key=lambda x: x.yearID, reverse=True)
        age = session.query(Player.age).filter(Player.lahmanID == holder[0].lahmanID).scalar()
    # teamID = team_abbr  # this will need to be from team loop
    # instantiate new Batting object
    pred_2015 = Batting(lahmanID=lahmanID,  # =holder[0].lahmanID,
                        user=user,
                        teamID=team_abbr,
                        yearID=2015)  # G=162)

    stats = ['G', 'H', 'AB', 'R', 'doubles', 'triples', 'HR', 'RBI',
             'SB', 'CS', 'HBP', 'BB', 'IBB', 'SO', 'GIDP', 'SH', 'SF']

    for stat in stats:
        # print stat
        stat_holder = 0
        for row in holder:
            # plate_apps = row.AB + row.BB + row.IBB + row.SH + row.SF
            # print "year weight: " + str(weights[row.yearID])
            # pa/g normalized for 162g should reflect use e.g. pinch hitter
            # modifier = (float(weights[row.yearID]) / total_weights) / row.G * 162
            modifier = (float(weights[row.yearID]) / total_weights)
            modifier = modifier * ageAdjustment(age)
            stat_holder += getattr(row, stat) * modifier
        stat_holder = int(round(stat_holder))
        setattr(pred_2015, stat, stat_holder)
    return pred_2015


def ageAdjustment(age):
    # print "age: " + str(age)
    return 1


def buildBattingObject(lahmanID, year_data):
    year_stats = Batting(lahmanID=lahmanID,
                         user=1,
                         yearID=year_data.yearID,
                         teamID=year_data.teamID,
                         G=year_data.G,
                         H=year_data.H,
                         AB=year_data.AB,
                         R=year_data.R,
                         doubles=getattr(year_data, "2B"),
                         triples=getattr(year_data, "3B"),
                         HR=year_data.HR,
                         RBI=year_data.RBI,
                         SB=year_data.SB,
                         HBP=year_data.HBP,
                         CS=year_data.CS,
                         BB=year_data.BB,
                         IBB=year_data.IBB,
                         SO=year_data.SO,
                         GIDP=year_data.GIDP,
                         SF=year_data.SF,
                         SH=year_data.SH
                         )
    return year_stats


def getCareerNums(lahmanID):
    career_numbers = session2.query(BattingStat.playerID,
                                    BattingStat.yearID,  # is this needed
                                    func.sum(BattingStat.G).label('G'),
                                    func.sum(BattingStat.AB).label('AB'),
                                    func.sum(BattingStat.H).label('H'),
                                    func.sum(BattingStat.R).label('R'),
                                    func.sum(getattr(BattingStat, '2B')).label('2B'),
                                    func.sum(getattr(BattingStat, '3B')). label('3B'),
                                    func.sum(BattingStat.HR).label('HR'),
                                    func.sum(BattingStat.RBI).label('RBI'),
                                    func.sum(BattingStat.SB).label('SB'),
                                    func.sum(BattingStat.CS).label('CS'),
                                    func.sum(BattingStat.BB).label('BB'),
                                    func.sum(BattingStat.IBB).label('IBB'),
                                    func.sum(BattingStat.SO).label('SO'),
                                    func.sum(BattingStat.HBP).label('HBP'),
                                    func.sum(BattingStat.GIDP).label('GIDP'),
                                    func.sum(BattingStat.SF).label('SF'),
                                    func.sum(BattingStat.SH).label('SH')
                                    ).filter(BattingStat.playerID == lahmanID).one()
    career_numbers.teamID = "ALL"
    return career_numbers


# useful methods: keys() returns an arrary of keys
#                 _asdict() returns a dictionay
#                 _labels() returns labels in a tuple
'''
# e.g. iterate over dictionary
key_dictionary = career_numbers._asdict()
for key in key_dictionary:
    print key, key_dictionary[key]
'''
# FIELDING
# not sure why but fielding wasn't populated
#   at least I don't think so.

# let's do that here:
meta = MetaData(bind=engine2)
fielding = Table('fielding', meta, autoload=True, autoload_with=engine2)

# now let's try a simple query
# --- note the use of .c. in the filter
ick = session2.query(fielding).filter(fielding.c.playerID == 'pompeda01').all()
# even with a rookie this returns 3 rows, LF, OF, CF
# --- OF stat might make things simpler

# tester for grouping stints into year:
stat_year = session2.query(BattingStat.playerID,
                           BattingStat.yearID,
                           func.sum(BattingStat.H).label('H'),
                           func.sum(BattingStat.AB).label('AB'),
                           func.sum(BattingStat.R).label('R'),
                           func.sum(getattr(BattingStat, '2B')).label('2B'),
                           func.sum(getattr(BattingStat, '3B')). label('3B'),
                           func.sum(BattingStat.HR).label('HR'),
                           func.sum(BattingStat.RBI).label('RBI'),
                           func.sum(BattingStat.SB).label('SB')
                           ).filter(BattingStat.yearID == 2013,  # year.yearID,
                                    BattingStat.playerID == 'carreez01'  # lahmanID
                                    ).group_by(BattingStat.yearID).one()


''' Helper lines

from sqlalchemy.orm.exc import NoResultFound
>>> try:
...     user = query.filter(User.id == 99).one()
... except NoResultFound, e:
...     print e
No row was found for one()


 from sqlalchemy import MetaData, Table

 meta = MetaData(bind=engine2)

 batting = Table('batting', meta, autoload=True, autoload_with=engine2)'''
