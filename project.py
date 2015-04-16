from flask import Flask, render_template, url_for, request, redirect
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


@app.route('/team/<teamID>/')
def teamPage(teamID):
    team_batting_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID).all()
    return render_template('base_team.html', player_data=team_batting_data)


@app.route('/player/<playerID>/')  # might want to use a converter and/or regex  # user specific too
def PlayerPage(playerID):
    player_data = session.query(Player).filter(Player.lahmanID == playerID).one()
    player_stats = session.query(Batting).filter(Batting.lahmanID == playerID).all()
    return render_template('player.html', player_data=player_data, player_stats=player_stats)
    '''
    player_data = session.query(Player).filter(Player.lahmanID == id).one()
    player_stats = session.query(Batting).filter(Batting.lahmanID == id, Batting.yearID >= 2012,
                                                 Batting.yearID <= 2014).order_by(Batting.yearID).all()
    career_stats = session.query(Batting).filter(Batting.lahmanID == playerID, Batting.yearID == 162).one()
    proj_stats = session.query(Batting).filter(Batting.lahmanID == playerID, Batting.yearID == 2015).one()
    return render_template('player.html', player_data=player_data, player_stats=player_stats,
                           career_stats=career_stats, proj_stats=proj_stats)
    '''


@app.route('/team/<teamID>/edit/', methods=['GET', 'POST'])
def editTeam(teamID):
    team_batting_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).all()
    if request.method == "POST":
        pass
    else:
        return render_template('team_edit.html', team_data=team_batting_data)


@app.route('/player/<playerID>/edit/', methods=['GET', 'POST'])
def EditPlayer(playerID):
    player_data = session.query(Player).filter(Player.lahmanID == playerID).one()
    player_stats = session.query(Batting).filter(Batting.lahmanID == playerID).all()

    if request.method == "POST":
        print "Posted!!!"

        stats2015 = session.query(Batting).filter(Batting.lahmanID == playerID, Batting.yearID == 2015).one()

        stats2015.G = request.form['G']
        stats2015.AB = request.form['AB']
        stats2015.H = request.form['H']
        stats2015.CS = request.form['CS']
        stats2015.IBB = request.form['IBB']
        stats2015.R = request.form['R']
        stats2015.doubles = request.form['2B']
        stats2015.triples = request.form['3B']
        stats2015.HR = request.form['HR']
        stats2015.RBI = request.form['RBI']
        stats2015.SB = request.form['SB']
        stats2015.BB = request.form['BB']
        stats2015.SO = request.form['SO']
        stats2015.HBP = request.form['HBP']
        stats2015.GIDP = request.form['GIDP']
        stats2015.SF = request.form['SF']
        stats2015.SH = request.form['SH']

        session.add(stats2015)
        session.commit()

        # flash(db updated)
        ''' works, goes to edit page, try implementing url_for redirect
        return render_template('player_edit.html', player_data=player_data,
                               player_stats=player_stats)
        '''
        return redirect(url_for('PlayerPage', playerID=playerID))
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
