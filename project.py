from flask import Flask, render_template, url_for, request
app = Flask(__name__)


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Player, Batting

# make postgresql engine
engine = create_engine('postgresql://ben:superstar@localhost/roto')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/hello')
@app.route('/index')
def HelloWorld():
    output = ""
    sluggers = session.query(Batting).filter(Batting.yearID == 2015).order_by(Batting.HR.desc()).limit(5).all()
    for row in sluggers:
        output += "<li>" + row.lahmanID + ":  " + str(row.HR) + " HR</li>"
    return output


@app.route('/player/<playerID>/')  # might want to use a converter and/or regex  # user specific too
def PlayerPage(playerID):
    player_data = session.query(Player).filter(Player.lahmanID == id).one()
    player_stats = session.query(Batting).filter(Batting.lahmanID == id, Batting.yearID >= 2012,
                                                 Batting.yearID <= 2014).order_by(Batting.yearID).all()
    career_stats = session.query(Batting).filter(Batting.lahmanID == playerID, Batting.yearID == 162).one()
    proj_stats = session.query(Batting).filter(Batting.lahmanID == playerID, Batting.yearID == 2015).one()
    return render_template('player.html', player_data=player_data, player_stats=player_stats,
                           career_stats=career_stats, proj_stats=proj_stats)


@app.route('/player/<playerID>/edit/', methods=['GET', 'POST'])
def EditPlayer(playerID):
    player_data = session.query(Player).filter(Player.lahmanID == playerID).one()
    player_stats = session.query(Batting).filter(Batting.lahmanID == playerID).all()
    # career_games = session.query(Batting.G).filter(Batting.lahmanID == playerID, Batting.yearID == 162).scalar()
    # proj_games = session.query(Batting.G).filter(Batting.lahmanID == playerID, Batting.yearID == 2015).scalar()
    # modifier = 162 / float(career_games)
    # proj_mod = 162 / float(proj_games)
    if request.method == "POST":
        print "Posted!!!"
        player_id = str(playerID)
        g = request.form['G']
        ab = request.form['AB']
        h = request.form['H']
        cs = request.form['CS']
        ibb = request.form['IBB']
        r = request.form['R']
        h2b = request.form['2B']
        h3b = request.form['3B']
        hr = request.form['HR']
        rbi = request.form['RBI']
        sb = request.form['SB']
        bb = request.form['BB']
        so = request.form['SO']
        hbp = request.form['HBP']
        gidp = request.form['GIDP']
        sf = request.form['SF']
        sh = request.form['SH']

        print "Got Data!!"
        print player_id
        print h, g, ab, cs, ibb, h2b, h3b, r
        print hr, rbi, sb, bb
        print so, hbp, gidp, sf, sh

        #  make new Batting object
        #  session.add()
        #  session.commit()
        return render_template('player_edit.html', player_data=player_data,
                               player_stats=player_stats)
    else:
        return render_template('player_edit.html', player_data=player_data,
                               player_stats=player_stats)  # , mod=modifier, projmod=proj_mod)


@app.route('/team/<teamID>')
def TeamPage(teamID):
    output = ""
    player_list = session.query(Batting.lahmanID).filter(Batting.teamID == teamID, Batting.yearID == 2015).all()
    for row in player_list:
        output += row.lahmanID + "<br>"
    return output


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
