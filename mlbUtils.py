#!C:\python27\python.exe

# needs to have Lahman db connected
# and access to internet

# relies on mlb not changing the urls and/or the formatting of
# team lists, depth charts, and individual json pages

import os
import urllib
import json
import pymysql
import pickle

# should find a good way to use date_verified in getTeamPage
# postion listing are filtered out in getUnique
# should add else logic (and another array to return pitchers)
#       run through get getMlbData, stick 'em in another pickle'

# seed page is used for grabbing all team depth charts
seedPage = "http://toronto.bluejays.mlb.com/team/depth_chart/?c_id=tor"
mydb = pymysql.connect('192.168.56.1', 'benjamin', 'plutarch', 'lahman14')


def pickleTeamIDs():
    # mydb = pymysql.connect('localhost', 'root', '', 'lahman14')
    # lazily made mydb a global
    # mydb = pymysql.connect('192.168.56.1', 'benjamin', 'plutarch', 'lahman14')

    cursor = mydb.cursor()
    statement = "SELECT teamID FROM teams where yearID = 2014 ORDER BY teamID"
    cursor.execute(statement)
    team_tuples = cursor.fetchall()
    cursor.close()
    team_ids = []
    for abbr in team_tuples:
        team_ids.append(abbr[0])
    curr_path = os.getcwd()
    pkl_dir = "teampkls"
    file_name = "l14_teamID_list"
    full_path = os.path.join(curr_path, pkl_dir, file_name)
    with open(full_path, "wb") as tp:
        pickle.dump(team_ids, tp)
    return team_ids  # for testing


def makeTeamPickles():
    warnings = []
    mlbteamid_to_lah_dict = makeTeamDictMlbLahman()
    team_links = getAllLinks()
    # sort to help with testing
    team_links.sort(key=lambda x: x[1])
    # team_links = team_links[0:3]  # for testing first team
    for team in team_links:
        roster_array, team_warnings = mlb2Bbref(team[2])
        team_dict = {}
        for player in roster_array:
            team_dict[player[5]] = {'name': player[0],
                                    'dob': player[1],
                                    'age': player[2],
                                    'mlbID': player[3],
                                    'pos': player[4]
                                    }
        curr_path = os.getcwd()
        pkl_dir = "teampkls"
        file_name = mlbteamid_to_lah_dict[team[1]]
        full_path = os.path.join(curr_path, pkl_dir, file_name)
        with open(full_path, "wb") as fp:  # flag might be better as "w"
            pickle.dump(team_dict, fp)
        warnings.append(team[0])
        warnings.append(team_warnings)

    # write warnings to a text file
    addy = os.path.join(curr_path, pkl_dir, "warnings.txt")

    # needs to be fixed/improved
    # currently only writing last team, remove pop()
    # like to try adding team name, add append(team) to warnings.append
    with open(addy, "wb") as wf:
        for i in range(0, len(warnings)):
            # even are team name, odd are arrays
            if i % 2 == 0:
                wf.write(str(warnings[i]) + "\n")
            else:
                for elem in warnings[i]:
                    wf.write(str(elem) + "\n")


def generateTest():
    ''' makes a pickle of the Jays roster for sharing/testing '''
    ''' only place pickle is used currently '''
    roster_array, warnings = mlb2Bbref(jays)
    ''' turning it into a dictionary isn't necessary but cool '''
    jays_dict = {}
    for player in roster_array:
        jays_dict[player[5]] = {'name': player[0],
                                'dob': player[1],
                                'age': player[2],
                                'mlbID': player[3],
                                'pos': player[4]
                                }
    curr_path = os.getcwd()
    pkl_dir = "teampkls"
    file_name = "TOR"
    full_path = os.path.join(curr_path, pkl_dir, file_name)
    with open(full_path, "wb") as fp:  # flag might be better as "w"
        pickle.dump(jays_dict, fp)

    '''
    # old working lines for current dir
    fp = open("jays_roster.pkl", "w")
    pickle.dump(jays_dict, fp)
    fp.close()
    '''
    return jays_dict


def getDepthChart(seed):
    """ Grabs a MLB page and excises appropriate text for link gathering """
    links_start = "Select Team"
    seed_html = urllib.urlopen(seed)
    seed_text = seed_html.read()
    seed_text = seed_text[seed_text.find(links_start):]  # truncate beginning
    seed_text = seed_text[:seed_text.find("/form")]  # truncate end
    return seed_text


def getLink(seed_text, link_array):
    """ Utility used in getAllLinks that parses the string from GetDepthChart
    to extract team links """
    start = seed_text.find("/team/depth_")
    end = seed_text.find('">')
    link = "http://mlb.mlb.com" + seed_text[start:end]
    id_start = link.find("=") + 1
    mlb_id = link[id_start:]
    # nameStart = end + 2
    name_end = seed_text[end + 2:].find("</op")
    name = seed_text[end + 2:end + name_end + 2]
    info = [name, mlb_id, link]
    link_array.append(info)
    new_text = seed_text[end + 4:]  # truncate
    return new_text, link_array


def getAllLinks():
    """ Returns a 30 team list of lists['team_name_string', '3letter_abbr',
    'web_link_to_depth_chart']"""
    text = getDepthChart(seedPage)
    link_array = []
    while text.find("/team/depth_") > 0:
        text, link_array = getLink(text, link_array)
    return link_array


jays = "http://mlb.mlb.com/team/depth_chart/index.jsp?c_id=tor"  # for testing getTeamPage


def getTeamPage(seed):
    """ Grabs a team's depth chart and excises appropriate text for link gathering """
    """ date_verified could prove useful but is not yet implemented """
    raw_page = urllib.urlopen(seed)
    page_text = raw_page.read()
    date_start = page_text.find("Verified:")
    date_verified = page_text[date_start:date_start + 22]
    pos_start = page_text.find('id="pos_')
    pos_end = page_text.find('id="pos_DL') + 20  # page end looks like "pos_DL" or pos_notes
    page = page_text[pos_start: pos_end]
    return date_verified, page


def getUnique(team):  # nb, tester getUnique(jays)
    """ returns unique batters from a string from depth chart link """
    '''
    ALPosList = ['LEFT FIELD', 'CENTRE FIELD', 'RIGHT FIELD',
                'SHORTSTOP', '2ND BASE', '1ST BASE', 'ROTATION',
                'DH', 'CATCHER', '3RD BASE', 'BULLPEN', 'CENTER FIELD']
            '''
    hit_list = ['LEFT FIELD', 'CENTRE FIELD', 'RIGHT FIELD',
                'SHORTSTOP', '2ND BASE', '1ST BASE',
                'DH', 'CATCHER', '3RD BASE', 'CENTER FIELD']
    holder = []
    unique = []
    holder2 = []
    pos_hold = []
    date_verified, stub = getTeamPage(team)
    print date_verified
    # update, stub = m[0], m[1]  # nb, old line m[0] is date_verified
    # stub = m[1]
    # loop through the team page string extract [A. Name, httpSuffix]
    for i in range(0, 11):
        player_name, stub, position_name = getPosition(stub)
        # screwing with this line
        holder.append(player_name)  # old line
        pos_hold.append(position_name)
        # print pos_hold  # nb, test line
        # stub = t  # nb, old line replaced in getPostion call above
    # construct hitting index, or:
    # if pos_hold[i] in hit_list
    hit_array = []
    # print holder  # nb, test print
    for i in range(0, len(pos_hold)):
        if pos_hold[i] in hit_list:
            # print pos_hold[i]  # nb, test print
            hit_array.append(i)
    for i in hit_array:  # sub in hitting index
        for j in range(len(holder[i])):
            holder2.append(holder[i][j])
    for name in holder2:
        if name not in unique:
            unique.append(name)
    return holder2, unique  # holder2 no longer needed, here for testing


def playersByPosition(team):  # nb, tester getUnique(jays)
    """ returns batters by position from a truncated depth chart link scrape"""
    """ format is an array [position, [['A. Name','mlbhttpsuffix']] """
    """ array is of len(# of postions), depth2(pos name, [players]) """
    '''
    ALPosList = ['LEFT FIELD', 'CENTRE FIELD', 'RIGHT FIELD',
                'SHORTSTOP', '2ND BASE', '1ST BASE', 'ROTATION',
                'DH', 'CATCHER', '3RD BASE', 'BULLPEN', 'CENTER FIELD']
            '''
    hit_list = ['LEFT FIELD', 'CENTRE FIELD', 'RIGHT FIELD',
                'SHORTSTOP', '2ND BASE', '1ST BASE',
                'DH', 'CATCHER', '3RD BASE', 'CENTER FIELD']
    holder = []
    unique = []
    holder2 = []
    player_by_position = []
    pos_hold = []
    date_verified, stub = getTeamPage(team)
    print date_verified
    # update, stub = m[0], m[1]  # nb, old line m[0] is date_verified
    # stub = m[1]
    # loop through the team page string extract [A. Name, httpSuffix]
    for i in range(0, 11):
        player_name, stub, position_name = getPosition(stub)
        # screwing with this line
        holder.append(player_name)  # old line
        pos_hold.append(position_name)
        # print pos_hold  # nb, test line
        # stub = t  # nb, old line replaced in getPostion call above
    # construct hitting index, or:
    # if pos_hold[i] in hit_list
    hit_array = []
    # print holder  # nb, test print
    for i in range(0, len(pos_hold)):
        if pos_hold[i] in hit_list:
            # print pos_hold[i]  # nb, test print
            hit_array.append(i)
    # print hit_array
    for i in hit_array:  # sub in hitting index
        loop_holder = []
        # player_by_position.append([pos_hold[i]])
        for j in range(len(holder[i])):
            holder2.append(holder[i][j])
            loop_holder.append(holder[i][j])
            # print player_by_position[i]
            # player_by_position.append(holder[i][j])
        player_by_position.append([pos_hold[i], loop_holder])

        # print pos_hold[i], holder[i][j]

    # need to change this loop to combine unique OFers
    for name in holder2:
        if name not in unique:
            unique.append(name)

    # need to ensure that centre/center field is unified
    # could just use where it's located index[1] but a loop is robust
    # nb, don't need this if unifying OF
    for position_name in player_by_position:
        if position_name[0] == "CENTRE FIELD":  # use uppercase?
            position_name[0] = "CENTER FIELD"

    # unify OFers
    outfielders = []
    for i in range(0, 3):
        for player in player_by_position[i][1]:
            if player not in outfielders:
                outfielders.append(player)
    # print outfielders  # test print

    player_by_position = [['OF', outfielders]] + player_by_position[3:]

    return holder2, unique, player_by_position  # holder2 no longer needed, here for testing


def getMLBdata(team):
    """ takes a http link to a mlb team depth chart and returns:
            an array of all unique players on a team [full name, dob, age, mlbID, pos, lahmanID]
            and an array of warnings e.g. altID, generated player ID (for rookies) etc. """
    """ grabs data from MLB on web from player .json """

    holder2, unique, player_by_position = playersByPosition(team)
    # web_prefix = "http//mlb.mlb"
    # mlb_web_str = web_prefix + unique[0][1]  # nb, test
    # print mlb_web_str  # nb, test
    roster = []
    for player in range(0, len(unique)):
        mlb_json_prefix = "http://mlb.mlb.com/lookup/json/named.player_info.bam?sport_code=%27mlb%27&player_id="
        id_string = unique[player][1][-6:]
        mlb_json_string = mlb_json_prefix + id_string
        # could make dictionary and implement checking here
        raw_json_page = urllib.urlopen(mlb_json_string)
        page_text = raw_json_page.read()
        player_json_data = json.loads(page_text)
        player_dictionary = player_json_data['player_info']['queryResults']['row']
        name = str(player_dictionary['name_display_first_last'])
        dob = str(player_dictionary['birth_date'][:10])
        age = int(player_dictionary['age'])
        position = str(player_dictionary['primary_position_txt'])
        roster.append([name, dob, age, id_string, position])
    return roster


def mlb2Bbref(team):
    """ generates lahmanID and appends it to getMLBdata array """
    """ takes a http link to a mlb team depth chart and returns:
            an array of all unique players on a team [full name, dob, age, mlbID, pos, lahmanID]
            and an array of warnings e.g. altID, generated player ID (for rookies) etc. """
    roster = getMLBdata(team)
    #  tobefilled = []
    warnings = []
    for i in range(0, len(roster)):
        names = roster[i][0].split(" ")  # two lines to avoid "Jr"
        first, last = names[0], names[1]
        if first[1] == ".":
            first = first[0] + first[2]  # deal with initials
            warnings.append([roster[i][0], "initials"])
        if last[1] == "'":  # e.g. O'Malley
            last = last[0] + last[2:]
        like_string = (last[:5] + first[:2]).lower() + "%"
        # mydb = pymysql.connect('localhost', 'root', '', 'lahman14') # nb, lazy global instead
        cursor = mydb.cursor()
        statement = '''SELECT playerID, birthYear, birthMonth, birthDay
           FROM master
           WHERE playerID LIKE "%s"
            and birthYear > 1965''' % (like_string)
        cursor.execute(statement)

        query_results = cursor.fetchall()
        # compare dob's, ensure not multiple names
        year, month, day = roster[i][1].split("-")

        if query_results:
            found = 0
            for j in range(0, len(query_results)):
                if int(year) == query_results[j][1] and int(month) == query_results[j][2] and int(day) == query_results[j][3]:
                    # ['given surname', 'dob', age, 'bbref']
                    filler = query_results[j][0]  # appending bbref, but what if there is none?
                    roster[i].append(filler)
                    found += 1
                else:
                    warnings.append([roster[i][0], "alt id"])

            if found != 1:
                bbref = genPlayerID(cursor, like_string)
                roster[i].append(bbref)
                # print "got here"
                warnings.append([roster[i][0], 'altID & genID'])
        else:
            bbref = genPlayerID(cursor, like_string)
            roster[i].append(bbref)
            print roster[i]
            warnings.append([roster[i][0], "generated playerID"])
        cursor.close()
    print "WARNING: " + str(warnings)
    return roster, warnings


def genPlayerID(cursor, like_string):
    statement = '''SELECT COUNT(DISTINCT playerID) FROM master
                            WHERE playerID LIKE "%s"''' % (like_string)
    cursor.execute(statement)
    result = cursor.fetchall()
    # cursor.close()
    newidnum = result[0][0] + 1
    if newidnum < 10:
        newidnum = "0" + str(newidnum)
    bbref = like_string[:-1] + str(newidnum)
    return bbref


def getPosition(page):  # maybe rework using page.split("position_header")
    """ Utility helps parse team page in getUnique """
    start = page.find("position_header")
    end = page[start + 4:].find('id="pos_')
    section = page[start:start + end]
    slices = section.split('href="')
    pos_name_start = slices[0].find('">') + 2
    pos_name_end = slices[0].find('</li>')
    pos_name = slices[0][pos_name_start: pos_name_end]
    # posHold = [] #temp
    # print pos_name
    holder = []
    del slices[0]  # don't need name any longer
    for elem in slices:
        s = elem.find('">')
        link = elem[:s]
        # print link # test line
        # posHold.append(pos_name)
        name = elem[s + 2:elem.find("</a>")]
        holder.append([name, link])
    page = page[start + end:]
    return holder, page, pos_name


def makeTeamDictMlbLahman():
    """ Makes a dictionary of teams {mlb teamID : lahman teamID} """
    mlb_teamid_lahman = {}
    mlb = getAllLinks()  # array [teamName, abbr, depthhttpaddy]
    mlb.sort(key=lambda x: x[1])
    # lazy use of mydb global
    # lahmandb = pymysql.connect('localhost', 'root', '', 'lahman14')
    # cur = lahmandb.cursor()
    cursor = mydb.cursor()
    statement = "SELECT teamID, name from teams WHERE yearID = 2014 order by teamID"
    cursor.execute(statement)
    lahman_teamids = list(cursor.fetchall())  # list of tuples, (ID, name)
    cursor.close()
    # do some brute force correction
    ana = mlb.pop(0)
    mlb.insert(12, ana)
    cha = lahman_teamids.pop(4)
    lahman_teamids.insert(8, cha)
    nym = mlb.pop(17)
    mlb.insert(18, nym)
    for i in range(0, 30):
        mlb_teamid_lahman[mlb[i][1]] = lahman_teamids[i][0]
    return mlb_teamid_lahman


def makeTeamSelectList():
    teams_dict = makeTeamDictMlbLahman()
    keys = teams_dict.keys()
    keys.sort()
    for key in keys:
        select_line = '<option value="{}">{}</option>'.format(teams_dict[key], key)
        print select_line
