from flask import (Flask, render_template, url_for, request, redirect,
                   flash, session as login_session)
app = Flask(__name__)


from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Player, Batting
import random
import string

# imports for Oauth2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

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
    return render_template('base_team.html', player_data=team_batting_data, teamID=teamID)


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
        try:
            new_player = Player(name=fullname,
                                lahmanID=lahman_id,
                                age=int(request.form['age']),
                                mlbID=999999,  # hmm, non unique, does it matter?
                                dob=str(request.form['dob']),
                                pos=request.form['position'],
                                teamID=request.form['teamID'])
        except ValueError as ve:
            return redirect(url_for('errorPage', error=ve))

        session.add(new_player)
        try:
            session.commit()  # likely have to commit here so that the Batting has a place to go
        except exc.SQLAlchemyError as e:
            session.rollback()
            print "Error commiting Player Info"
            return redirect(url_for('errorPage', error="likely a duplicate entry"))

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
        try:
            session.commit()
        except exc.SQLAlchemyError as e:
            session.rollback()
            #  need to delete player entry
            aborted_player = session.query(Player).filter(Player.lahmanID == lahman_id)
            if aborted_player:
                session.delete(aborted_player)
                session.commit()
            return redirect(url_for('errorPage', error=e))

        '''
        except exc.SQLAlchemyError as e:
            session.rollback()
            print "Player Id (likely) already exists, oops"
            print e
            # flash oops
            # raise e
            return redirect(url_for('errorPage', error=e))'''
        '''
        finally:
            session.remove()'''
        print "Player committed"

        return redirect(url_for('editTeam', teamID=team_id))
    else:
        return render_template('newPlayer.html')


@app.route('/error/<error>')
def errorPage(error):
    return render_template('base_error.html', error=error)


@app.route('/player/<playerID>/delete/', methods=['GET', 'POST'])
def deletePlayer(playerID):
    # might want to convert the two queries to one
    player_data = session.query(Player).filter(Player.lahmanID == playerID).one()
    player_stats = session.query(Batting).filter(Batting.lahmanID == playerID).all()
    team_id = player_data.teamID
    print team_id
    if request.method == "POST":
        print "Did post"
        # the below loop was needed prior to cascade
        # scratch that, IS needed; cascade not working, yes it IS
        '''
        for year in player_stats:
            session.delete(year)
        session.commit()
        print "did first bit" '''
        session.delete(player_data)
        session.commit()
        print "deleted"
        # flash ("Player successfully deleted")
        return redirect(url_for('teamPage', teamID=team_id))
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


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    # print 'login_session["state"] = %s' % login_session['state']
    # return "The current sessionstate is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    print 'received state of %s' % request.args.get('state')
    print 'here the login_session["state"] = %s' % login_session['state']
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # gplus_id = request.args.get('gplus_id')
    # print "request.args.get('gplus_id') = %s" %request.args.get('gplus_id')
    code = request.data
    print "received code of %s " % code

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    response = make_response(json.dumps('Successfully connected user.', 200))

    print "#Get user info"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    print "data: ",
    print data

    # login_session['credentials'] = credentials
    # login_session['gplus_id'] = gplus_id
    login_session['username'] = data["name"]
    print login_session['username']
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    # print login_session['email']

    # see if user exists, if it doesn't make a new one
    '''
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id

        output = ''
        output += '<h1>Welcome, '
        output += login_session['username']

        output += '!</h1>'
        output += '<img src="'
        output += login_session['picture'] '''
    # output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    # return output

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# Disconnect by revoking a user's token and resetting the login_session
@app.route("/gdisconnect")
def gdisconnect():
    # only disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('User is not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # GET the token and revoke
    access_token = credentials.access_token
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
