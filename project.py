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
    # might want to convert the two queries to one
    player_data = session.query(Player).filter(Player.lahmanID == playerID).one()
    player_stats = session.query(Batting).filter(Batting.lahmanID == playerID).all()
    return render_template('player.html', player_data=player_data, player_stats=player_stats)


# may need to wrap lahmanID builder in try catch w/ db queries
# using "09" as a kluge suffix to enable id generation w/o access to lahman db
# could try to access - catch: use suffix
# other error handling might be cool too
@app.route('/player/new/', methods=['GET', 'POST'])
def newPlayer():
    if request.method == 'POST':
        fullname = request.form['given'] + " " + request.form['last']
        lahman_id = (request.form['last'][:5] + request.form['given'][:2] + "09").lower()  # 9 should be safe
        team_id = request.form['teamID']  # need this for the redirect

        new_player = Player(name=fullname,
                            lahmanID=lahman_id,
                            age=int(request.form['age']),
                            mlbID=999999,  # hmm, non unique, does it matter?
                            dob=str(request.form['dob']),
                            pos=request.form['position'],
                            teamID=request.form['teamID'])
        session.add(new_player)
        session.commit()  # likely have to commit here so that the Batting has a place to go
        # print "Player committed"

        np_stats = Batting(lahmanID=lahman_id,
                           yearID=2015,
                           teamID=request.form['teamID'],
                           G=request.form["G"],
                           AB=request.form["AB"],
                           H=request.form["H"],
                           CS=request.form["CS"],
                           IBB=request.form["IBB"],
                           R=request.form["R"],
                           doubles=request.form["2B"],
                           triples=request.form["3B"],
                           HR=request.form["HR"],
                           RBI=request.form["RBI"],
                           SB=request.form["SB"],
                           BB=request.form["BB"],
                           SO=request.form["SO"],
                           HBP=request.form["HBP"],
                           GIDP=request.form["GIDP"],
                           SH=request.form["SH"],
                           SF=request.form["SF"])
        session.add(np_stats)
        session.commit()

        return redirect(url_for('teamPage', teamID=team_id))
    else:
        return render_template('newPlayer.html')


@app.route('/player/<playerID>/delete/', methods=['GET', 'POST'])
def deletePlayer(playerID):
    # might want to convert the two queries to one
    player_data = session.query(Player).filter(Player.lahmanID == playerID).one()
    player_stats = session.query(Batting).filter(Batting.lahmanID == playerID).all()
    if request.method == "POST":
        session.delete(player_stats)
        session.delete(player_data)
        session.commit()
        print "deleted"
        # flash ("Player successfully deleted")
        return redirect('teamPage.html', teamID=player_data.teamID)
    else:
        print "go to delete page"
        return render_template('deletePlayer.html', player_data=player_data, player_stats=player_stats)


@app.route('/team/<teamID>/edit/', methods=['GET', 'POST'])
def editTeam(teamID):
    team_batting_data = session.query(Player, Batting).join(Batting).filter(Player.lahmanID == Batting.lahmanID, Player.teamID == teamID, Batting.yearID == 2015).all()
    if request.method == "POST":
        print "Postage!"
        form_data = request.values
        ids = form_data.getlist('lahmanID')
        print ids
        # loop through players, grab data, commit new objs
        for lahmanID in ids:
            # print lahmanID
            batter_obj = session.query(Batting).filter(Batting.lahmanID == lahmanID, Batting.yearID == 2015).one()
            batter_obj.G = request.form[lahmanID + "G"]
            batter_obj.AB = request.form[lahmanID + "AB"]
            batter_obj.H = request.form[lahmanID + "H"]
            batter_obj.CS = request.form[lahmanID + "CS"]
            batter_obj.IBB = request.form[lahmanID + "IBB"]
            batter_obj.R = request.form[lahmanID + "R"]
            batter_obj.doubles = request.form[lahmanID + "2B"]
            batter_obj.triples = request.form[lahmanID + "3B"]
            batter_obj.HR = request.form[lahmanID + "HR"]
            batter_obj.RBI = request.form[lahmanID + "RBI"]
            batter_obj.SB = request.form[lahmanID + "SB"]
            batter_obj.BB = request.form[lahmanID + "BB"]
            batter_obj.SO = request.form[lahmanID + "SO"]
            batter_obj.HBP = request.form[lahmanID + "HBP"]
            batter_obj.GIDP = request.form[lahmanID + "GIDP"]
            batter_obj.SH = request.form[lahmanID + "SH"]
            batter_obj.SF = request.form[lahmanID + "SF"]
            session.add(batter_obj)
            session.commit()
            # flash team updated
        return redirect(url_for('teamPage', teamID=teamID))
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
