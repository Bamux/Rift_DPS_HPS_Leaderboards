import codecs
import locale
import mysql_connect_config
import gzip
import shutil
from operator import itemgetter, attrgetter


def get_bossid(mycursor):
    sql = "SELECT * FROM boss WHERE instanceid = 1"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def get_classid(mycursor):
    sql = "SELECT * FROM classes"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def get_roleid(mycursor):
    sql = "SELECT * FROM roles"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_leaders_html_comps(mycursor, bossid, number_of_players, guild):
    time = "totaltime"
    if bossid == "2":
        time = "time"
    sql = "select playername, dps, time, totaltime, date, hps, class, role, a.encounterid, ptid, guildname " \
          "FROM Encounterinfo a " \
          "INNER JOIN Encounter on a.id = Encounter.encounterid " \
          "INNER JOIN Player on Encounter.playerid = Player.id " \
          "INNER JOIN Classes on Player.classid = Classes.id " \
          "INNER JOIN Roles on Encounter.roleid = Roles.id " \
          "INNER JOIN Guild on Guild.id = a.guildid " \
          "where bossid = " + bossid + " and guildname <> '" + guild + "' "\
          "ORDER BY " + time + ", date, Encounter.dps desc limit " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_leaders_html_fastest_kills(mycursor, bossid, number_of_players):
    mintime = " time, Min(totaltime) as mintime"
    time = "totaltime"
    if bossid == "2":
        mintime = " Min(time) as mintime, totaltime"
        time = "time"
    sql = "select Guild.guildname, sum(dps) as sum_dps, " + mintime + ", a.encounterid from Encounterinfo a " \
          "INNER JOIN Encounter on a.id = Encounter.encounterid " \
          "INNER JOIN Guild on a.guildid = Guild.id " \
          "WHERE a.bossid = " + bossid + " and a.id = ( " \
          "SELECT id from Encounterinfo b " \
          "WHERE b.bossid = " + bossid + " and b.guildid = a.guildid " \
          "ORDER BY b." + time + " limit 1) " \
          "group by Guild.guildname " \
          "ORDER BY mintime, sum_dps desc limit " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_top_dps_hps(mycursor, bossid, classid, number_of_players, role, dps_hps):
    condition = ""
    if classid:
        condition += " and Player.classid = " + classid + ""
    if role:
        condition += " and Roles.role like '%" + role + "%'"
    sql = "SELECT playername, dps AS DPS, time, totaltime, date, HPSAPS, class, role, " \
          "encounterid, ptid, aps, thps, bossname FROM ( " \
          "SELECT DISTINCT playername, dps, a.encounterid, playerid AS id, dps AS max_dps_hps ," \
          " TIME, totaltime, date, hps + aps as HPSAPS, class, role, ptid, aps, thps, bossname FROM Encounterinfo a " \
          "INNER JOIN Encounter ON a.id = Encounter.encounterid " \
          "INNER JOIN Player ON Encounter.playerid = Player.id " \
          "INNER JOIN Classes on Player.classid = Classes.id " \
          "INNER JOIN Roles on Encounter.roleid = Roles.id " \
          "INNER JOIN Boss on a.bossid = Boss.id " \
          "WHERE bossid = " + bossid + condition + " " \
          "ORDER BY " + dps_hps + " DESC) AS top_dps_hps " \
          "GROUP BY playername " \
          "ORDER BY " + dps_hps + " DESC LIMIT " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_top100(mycursor, bossid, classid, number_of_players, role, dps_hps):
    condition = ""
    if classid:
        condition += " and Player.classid = " + classid + ""
    if role:
        condition += " and Roles.role = 'dps'"
    sql = "SELECT playername, dps AS DPS, time, totaltime, date, HPSAPS, class, role, " \
          "encounterid, ptid, aps, thps, bossname FROM ( " \
          "SELECT DISTINCT playername, dps, a.encounterid, playerid AS id, dps AS max_dps_hps ," \
          " TIME, totaltime, date, hps + aps as HPSAPS, class, role, ptid, aps, thps, bossname FROM Encounterinfo a " \
          "INNER JOIN Encounter ON a.id = Encounter.encounterid " \
          "INNER JOIN Player ON Encounter.playerid = Player.id " \
          "INNER JOIN Classes on Player.classid = Classes.id " \
          "INNER JOIN Roles on Encounter.roleid = Roles.id " \
          "INNER JOIN Boss on a.bossid = Boss.id " \
          "WHERE bossid = " + bossid + condition + " " \
          "ORDER BY " + dps_hps + " DESC) AS top_dps_hps " \
          "GROUP BY playername " \
          "ORDER BY " + dps_hps + " DESC LIMIT " + number_of_players + ""
    # print(sql)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_last_uploads(mycursor):
    sql = "SELECT date, bossname, guildname, playername, class, role, dps, hps, thps, aps, TIME, totaltime, " \
          "Encounterinfo.encounterid, ptid " \
          "FROM encounterinfo " \
          "INNER JOIN Encounter ON Encounterinfo.id = Encounter.encounterid " \
          "INNER JOIN Boss ON Encounterinfo.bossid = Boss.id " \
          "INNER JOIN Player ON Encounter.playerid = Player.id " \
          "INNER JOIN Classes on Player.classid = Classes.id " \
          "INNER JOIN Guild on Encounterinfo.guildid = Guild.id " \
          "INNER JOIN Roles on Encounter.roleid = Roles.id " \
          "ORDER BY encounterinfo.encounterid desc, Boss.id desc, dps desc " \
          "LIMIT 400"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_json(mycursor, bossid, roleid, order):
    number_of_players = "500"
    sql = "SELECT date, guildname, bossname, playername, class, role, dps AS DPS, hps, thps, aps, time, totaltime, " \
          "encounterid, ptid FROM ( " \
          "SELECT DISTINCT playername, dps, a.encounterid, playerid, dps AS max_dps_hps ," \
          " time, totaltime, date, hps + aps as HPSAPS, class, role, ptid, aps, hps, thps, bossname, guildname " \
          "FROM Encounterinfo a " \
          "INNER JOIN Encounter ON a.id = Encounter.encounterid " \
          "INNER JOIN Player ON Encounter.playerid = Player.id " \
          "INNER JOIN Classes on Player.classid = Classes.id " \
          "INNER JOIN Roles on Encounter.roleid = Roles.id " \
          "INNER JOIN Boss on a.bossid = Boss.id " \
          "INNER JOIN Guild on a.guildid = Guild.id " \
          "WHERE bossid = " + bossid + " AND roleid = " + roleid + " " \
          "ORDER BY " + order + " DESC) AS top_dps_hps " \
          "GROUP BY playername " \
          "ORDER BY " + order + " DESC LIMIT " + number_of_players + ""
    # print(sql)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_count_players_encounter(mycursor):
    sql = "SELECT COUNT(id) FROM Player"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_count_encounters(mycursor):
    sql = "SELECT COUNT(id) FROM Encounterinfo"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_count_classes(mycursor):
    sql = "SELECT class, COUNT(Player.id) as number FROM Player " \
          "INNER JOIN Classes on Player.classid = Classes.id " \
          "GROUP BY classid " \
          "ORDER BY NUMBER desc"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def format_number(number):
    locale.setlocale(locale.LC_NUMERIC, "german")
    number = locale.format("%.0f", number, grouping=True)
    return number


def create_url_dps(encounterid, playerid, text):
    if encounterid == "111" and playerid == "148245":
        url = '<a href="https://cdn.discordapp.com/attachments/560240994453553152/607675138359427073/' \
              '2019-08-04_223032.jpg" target="_blank">' + text + "</a>"
    elif encounterid == "17626" and playerid == "141559":
        url = '<a href="https://cdn.discordapp.com/attachments/281193813773516803/498550194191859712/' \
              '2018-10-07_191938.jpg" target="_blank">' + text + "</a>"
    else:
        url = "https://prancingturtle.com"
        url = '<a href="' + url + '/Encounter/Interaction?id=' + encounterid + "&p=" + playerid + \
              '&outgoing=True&type=DPS&mode=ability&filter=all" target="_blank">' + text + "</a>"
    return url


def create_url_hps(encounterid, playerid, text):
    url = "https://prancingturtle.com"
    url = '<a href="' + url + '/Encounter/Interaction?id=' + encounterid + "&p=" + playerid + \
          '&outgoing=True&type=HPS&mode=ability&filter=all" target="_blank">' + text + "</a>"
    return url


def create_url_overview(encounterid, text):
    url = "https://prancingturtle.com"
    url = '<a href="' + url + '/Encounter/PlayerDamageDone/' + encounterid + '" target="_blank">' + text + "</a>"
    return url


def head_html(title, nav_link, html_file):
    html = []
    head = "head.html"
    hide = False
    lookup = False
    default = True
    html_file = "/" + html_file
    dropdown = nav_link.split(" ")[0]
    print(nav_link)
    if not title:
        title = nav_link
    template = codecs.open("../template/" + head, 'r', "utf-8")
    for line in template:
        if "<!-- Hide Navbar -->" in line:
            hide = True
        elif "<!-- Hide Navbar End -->" in line:
            hide = False
        elif '<title>' in line:
            html += ["    <title>" + title + "</title>\n"]
        elif html_file in line or nav_link in line or (dropdown and dropdown in nav_link and dropdown in line):
            if "dropdown-toggle"in line:
                html.pop()
                html += ['                <li class="nav-item dropdown active">\n']
                html += [line]
            elif "dropdown-item" in line:
                line = line.split("dropdown-item")
                line = line[0] + "dropdown-item active" + line[1]
                html += [line]
            elif "nav-link" in line:
                html.pop()
                html += ['                <li class="nav-item active">\n']
                line = line.split("</a>")[0]
                html += [line + '</a><span class="sr-only">(current)</span>\n']
        elif "<!-- Lookup -->" in line:
            lookup = True
        elif "<!-- Lookup End -->" in line:
            lookup = False
        elif "<!-- jQuery first, then Popper.js, then Bootstrap JS -->" in line:
            default = False
        elif "<!-- Default -->" in line:
            default = True
        else:
            if "magelocdn" in line:
                if title == "Most Played Specs":
                    html += [line]
            else:
                if "Lookup" in title:
                    if default:
                        html += [line]
                elif not hide or title == "Latest Uploads on Prancing Turtle" or title == "Most Played Specs":
                    if not lookup:
                        html += [line]
    template.close()
    return html


# exchanges placeholders in the template file with the mysql data
def exchange(mycursor, template, file, mysql_data, nav_link, number_of_players, html_file):
    i = 0
    boss_counter = 0
    tbody = False
    normal_content_zone = False
    player_class = ""
    for line in template:
        if "<title>" in line:
            title = line.split("<title>")[1].split("</title>")[0]
            html = head_html(title, nav_link, html_file)
            for item in html:
                file.write(item)
        if "<!-- Normal Content Zone -->" in line:
            normal_content_zone = True
        if "<!-- Footer -->" in line:
            footer = footer_html()
            for item in footer:
                file.write(item)
        if "#fastest_time" in line:
            time = str(mysql_data[i][2]).split("0:0")[1]
            line = line.replace("#fastest_time", time)
        if normal_content_zone:
            if "<h2>" in line:
                boss_counter += 1
                if "#boss" in line:
                    if mysql_data[i][12] not in nav_link:
                        if "HPS" in nav_link:
                            line = line.replace("#boss", mysql_data[i][12] + " - " + nav_link + " + APS")
                        else:
                            line = line.replace("#boss", mysql_data[i][12] + " - " + nav_link)
                    else:
                        line = line.replace("#boss", mysql_data[i][12] + " - Top 100 DPS")
                elif "#class" in line:
                    line = line.replace("#class", mysql_data[i][6] + " - " + nav_link)
                elif "#dps/hps" in line:
                    if "DPS" in nav_link:
                        line = line.replace("#dps/hps", "DPS")
                    else:
                        line = line.replace("#dps/hps", "HPS")
            elif "#typehead" in line:
                if "DPS" in nav_link:
                    line = line.replace("#typehead", "ST DPS")
                else:
                    line = line.replace("#typehead", "HPAPS")
            elif "#dps/hps</th>" in line:
                if "DPS" in nav_link:
                    line = line.replace("#dps/hps", "HPAPS")
                else:
                    line = line.replace("#dps/hps", "ST DPS")
            elif "<tbody>" in line:
                tbody = True
            elif "</tbody>" in line:
                tbody = False
            elif "#content" in line:
                line = line.replace("#content", content(mycursor))
            elif "#guild" in line:
                guild = mysql_data[i-1][10]
                line = line.replace("#guild", guild)
            elif "#class" in line:
                try:
                    if mysql_data[i][0] != 0:
                            player_class = mysql_data[i][6]
                            line = line.replace("#class", player_class)
                    else:
                        line = line.replace("#class", mysql_data[i][1])
                except:
                    line = line.replace("#class", player_class)
            if tbody:
                if "#name" in line:
                    if mysql_data[i][0] != 0:
                        name = str(mysql_data[i][0])
                        name = name[0:14]
                        line = line.replace("#name", name)
                    else:
                        line = line.replace("#name", "")
                elif "#date" in line:
                    if mysql_data[i][0] != 0:
                        if "DPS" in nav_link:
                            name = create_url_dps(str(mysql_data[i][8]), str(mysql_data[i][9]), str(mysql_data[i][4]))
                            line = line.replace("#date", name)
                        else:
                            name = create_url_hps(str(mysql_data[i][8]), str(mysql_data[i][9]), str(mysql_data[i][4]))
                            line = line.replace("#date", name)
                    else:
                            line = line.replace("#date", "-")
                elif "#url" in line:
                    if mysql_data[i][0] != 0:
                        name = create_url_overview(str(mysql_data[i][4]), str(mysql_data[i][0]))
                        line = line.replace("#url", name)
                    else:
                        line = line.replace("#url", "")
                elif "<td>#dps</td>" in line:
                    if mysql_data[i][0] != 0:
                        dps = format_number(mysql_data[i][1])
                        line = line.replace("#dps", dps)
                    else:
                        line = line.replace("#dps", "")
                elif "#type" in line:
                    if mysql_data[i][0] != 0:
                        if "DPS" in nav_link:
                            dps = format_number(mysql_data[i][1])
                            line = line.replace("#type", dps)
                        else:
                            hps = format_number(mysql_data[i][5])
                            line = line.replace("#type", hps)
                    else:
                        line = line.replace("#type", "")
                elif "#dps/hps</td>" in line:
                    if mysql_data[i][0] != 0:
                        if "DPS" in nav_link:
                            hps = format_number(mysql_data[i][5])
                            line = line.replace("#dps/hps", hps)
                        else:
                            dps = format_number(mysql_data[i][1])
                            line = line.replace("#dps/hps", dps)
                    else:
                        line = line.replace("#dps/hps", "")
                elif "#hps" in line:
                    if mysql_data[i][0] != 0:
                        line = line.replace("#hps", format_number(mysql_data[i][5]))
                    else:
                        line = line.replace("#hps", "")
                elif "#thps" in line:
                    if mysql_data[i][0] != 0:
                        line = line.replace("#thps", format_number(mysql_data[i][11]))
                    else:
                        line = line.replace("#thps", "")
                elif "#ohps" in line:
                    if mysql_data[i][0] != 0:
                        hps = (mysql_data[i][5] - mysql_data[i][10])
                        ohps = mysql_data[i][11] - hps
                        line = line.replace("#ohps", format_number(ohps))
                    else:
                        line = line.replace("#ohps", "")
                elif "#aps" in line:
                    if mysql_data[i][0] != 0:
                        line = line.replace("#aps", format_number(mysql_data[i][10]))
                    else:
                        line = line.replace("#aps", "")
                elif "#totaltime" in line:
                    if mysql_data[i][0] != 0:
                        time = str(mysql_data[i][3]).split("0:0")[1]
                        totaltime = str(mysql_data[i][2]).split("0:0")[1]
                        if time != totaltime:
                            time += " | " + totaltime
                        line = line.replace("#totaltime", time)
                    else:
                        line = line.replace("#totaltime", "")
                elif "#time" in line:
                    if mysql_data[i][0] != 0:
                        time = str(mysql_data[i][2]).split("0:0")[1]
                        line = line.replace("#time", time)
                    else:
                        line = line.replace("#time", "")
                elif "#role" in line:
                    role = mysql_data[i][7]
                    if "/heal/support" in role:
                        role = role.replace("/heal/support", "/heal/s")
                    elif "/support" in role:
                        role = role.replace("/support", "/supp")
                    url = create_url_dps(str(mysql_data[i][8]), str(mysql_data[i][9]), role)
                    # line = line.replace("#date", url)
                    line = line.replace("#role", url)
                elif "#avg" in line:
                    if mysql_data[i] != 0:
                        if (nav_link == "Damage DPS" or "Top 100" in nav_link) and "#percent" in line:
                            x = (number_of_players + 1)*5*boss_counter-1
                            percent = mysql_data[i]/mysql_data[x]*100
                            percent = round(percent)
                            line = line.replace("#percent", str(percent) + "%")
                        else:
                            line = line.split(" (")[0]
                        line = line.replace("#avg", format_number(mysql_data[i]))
                    else:
                        line = line.replace("#avg", "")
                if "</tr>" in line:
                    i += 1
            file.write(line)


def average(data, number_of_players, dps_hps):
    dps_sum = 0
    if number_of_players > 0:
        place = 1
        if dps_hps == "HPSAPS":
            place = 5
        for dps in data:
            if dps[0] != 0:
                dps_sum += (dps[place])
        dps_sum = round(dps_sum/number_of_players)
    return dps_sum


def content(mycursor):
    class_html = ""
    encounters = mysql_count_encounters(mycursor)[0][0]
    players = mysql_count_players_encounter(mycursor)[0][0]
    classes = mysql_count_classes(mycursor)
    i = 0
    for item in classes:
        if i == 0:
            class_html += str(item[1]) + " " + item[0] + "s"
        else:
            class_html += ", " + str(item[1]) + " " + item[0] + "s"
        i += 1
    html = "The database contains " + str(players) + " Players, " + class_html + " who killed " + str(encounters) \
           + ' bosses. The database only contains data after <a href="http://forums.riftgame.com/general-discussions/' \
             'patch-notes/505586-rift-4-5-update-7-11-2018-a.html" target="new">2018-07-11</a> the last major class balance patch.'
    return html


def leaders_html(mycursor, bossid, html_file, nav_link):
    mysql_data = []
    guild = []
    roles = ["support", "tank", "heal"]
    template = codecs.open("../template/" + html_file, 'r', "utf-8")
    file = codecs.open("../public/" + html_file, 'w', "utf-8")
    number_of_players = 10
    for boss_id in bossid:
        data = mysql_leaders_html_fastest_kills(mycursor, str(boss_id[0]), str(number_of_players))
        mysql_data += data + [average(data, number_of_players, "DPS")]
    for boss_id in bossid:
        data = mysql_leaders_html_comps(mycursor, str(boss_id[0]), str(number_of_players), "")
        mysql_data += data + [average(data, number_of_players, "DPS")]
        guild += [(data[1][10])]
    i = 0
    for boss_id in bossid:
        data = mysql_leaders_html_comps(mycursor, str(boss_id[0]), str(number_of_players), guild[i])
        mysql_data += data + [average(data, number_of_players, "DPS")]
        i += 1
    number_of_players = 15
    for boss_id in bossid:
        data = mysql_top_dps_hps(mycursor, str(boss_id[0]), "", str(number_of_players), "", "DPS")
        mysql_data += data + [average(data, number_of_players, "DPS")]
    number_of_players = 10
    for role in roles:
        for boss_id in bossid:
            data = mysql_top_dps_hps(mycursor, str(boss_id[0]), "", str(number_of_players), role, "DPS")
            mysql_data += data + [average(data, number_of_players, "DPS")]
    exchange(mycursor, template, file, mysql_data, nav_link, number_of_players, html_file)
    file.close()
    template.close()
    print("../public/" + html_file + " created")


def tank_sup_dps_hps_html(mycursor, bossid, classid, role, sort_order, html_file, nav_link):
    template_file = "dps_hps_all_roles.html"
    mysql_data = []
    sorted_data = []
    template = codecs.open("../template/" + template_file, 'r', "utf-8")
    file = codecs.open("../public/" + html_file, 'w', "utf-8")
    number_of_players = 10
    for boss_id in bossid:
        unsorted_data = []
        for class_id in classid:
            data = mysql_top_dps_hps(mycursor, str(boss_id[0]), str(class_id[0]), str(number_of_players), role,
                                     sort_order)
            if len(data) < number_of_players:
                players = len(data)
                for i in range(number_of_players - players):
                    data += [(0, class_id[1])]
                unsorted_data += [[average(data, players, sort_order), data]]
            else:
                unsorted_data += [[average(data, number_of_players, sort_order), data]]
        unsorted_data.sort(reverse=True)
        sorted_data += unsorted_data
    for item in sorted_data:
        mysql_data += item[1] + [item[0]]
    exchange(mycursor, template, file, mysql_data, nav_link, number_of_players, html_file)
    file.close()
    template.close()
    print("../public/" + html_file + " created")


def hps_html(mycursor, bossid, classid, role, sort_order, html_file, nav_link):
    template_file = "hps.html"
    mysql_data = []
    template = codecs.open("../template/" + template_file, 'r', "utf-8")
    file = codecs.open("../public/" + html_file, 'w', "utf-8")
    number_of_players = 15
    for boss_id in bossid:
        if boss_id[0] != 2:
            data = mysql_top_dps_hps(mycursor, str(boss_id[0]), "", str(number_of_players), role, sort_order)
            mysql_data += data + [average(data, number_of_players, "HPSAPS")]
    number_of_players = 10
    for class_id in classid:
        for boss_id in bossid:
            if boss_id[0] != 2:
                data = mysql_top_dps_hps(mycursor, str(boss_id[0]), str(class_id[0]), str(number_of_players),
                                         role, sort_order)
                if len(data) < number_of_players:
                    players = len(data)
                    for i in range(number_of_players - players):
                        data += [(0, class_id[1])]
                mysql_data += data + [average(data, number_of_players, "HPSAPS")]
    exchange(mycursor, template, file, mysql_data, nav_link, number_of_players, html_file)
    file.close()
    template.close()
    print("../public/" + html_file + " created")


def top100(mycursor, bossid, classid, role, sort_order, html_file, nav_link):
    template_file = "top100.html"
    mysql_data = []
    sorted_data = []
    template = codecs.open("../template/" + template_file, 'r', "utf-8")
    file = codecs.open("../public/" + html_file, 'w', "utf-8")
    number_of_players = 100
    unsorted_data = []
    for class_id in classid:
        data = mysql_top100(mycursor, str(bossid), str(class_id[0]), str(number_of_players), role, sort_order)
        if len(data) < number_of_players:
            players = len(data)
            for i in range(number_of_players - players):
                data += [(0, class_id[1])]
            unsorted_data += [[average(data, players, sort_order), data]]
            # mysql_data += data + [average(data, players, sort_order)]
        else:
            unsorted_data += [[average(data, number_of_players, sort_order), data]]
    unsorted_data.sort(reverse=True)
    sorted_data += unsorted_data
    for item in sorted_data:
        mysql_data += item[1] + [item[0]]
    exchange(mycursor, template, file, mysql_data, nav_link, number_of_players, html_file)
    file.close()
    template.close()
    print("../public/" + html_file + " created")


def resources(mycursor, html_file):
    normal_content_zone = False
    template = codecs.open("../template/" + html_file, 'r', "utf-8")
    file = codecs.open("../public/" + html_file, 'w', "utf-8")
    for line in template:
        if "<title>" in line:
            title = line.split("<title>")[1].split("</title>")[0]
            html = head_html(title, "Resources", html_file)
            for item in html:
                file.write(item)
        elif "<!-- Footer -->" in line:
            footer = footer_html()
            for item in footer:
                file.write(item)
        elif "<!-- Normal Content Zone -->" in line:
            normal_content_zone = True
        elif "#content" in line:
            line = line.replace("#content", content(mycursor))
        if normal_content_zone:
            file.write(line)
    file.close()
    template.close()
    print("../public/" + html_file + " created")


def avg_raid_dps(dps_sum):
    html = []
    html += ['            <tr>']
    html += ['                <td scope="row">Raid DPS:</td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row">' + str(dps_sum) + '</td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    return html


def empty_row():
    html = []
    html += ['            <tr>']
    html += ['                <td scope="row">-</td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    html += ['                <td scope="row"></td>']
    return html


def last_uploads_html(mycursor, html_file, nav_link):
    html = []
    tablehead_html = ""
    table = False
    tablehead = False
    normal_content_zone = False
    template = codecs.open("../template/" + html_file, 'r', "utf-8")
    file = codecs.open("../public/" + html_file, 'w', "utf-8")
    mysql_data = mysql_last_uploads(mycursor)
    tablehead = False
    encounter_previous = ""
    encounterid_previous = ""
    x = 0
    dps_sum = 0
    for line in template:
        linecopy = line
        if "<title>" in line:
            title = line.split("<title>")[1].split("</title>")[0]
            html = head_html(title, nav_link, html_file)
        elif "<!-- Normal Content Zone -->" in line:
            normal_content_zone = True
        elif "<!-- tablehead start -->" in line:
            tablehead = True
        elif '#date' in line:
            line = line.replace('#date', str(mysql_data[x][0]))
        elif '#boss' in line:
            line = line.replace('#boss', str(mysql_data[x][1]).split(" ")[0])
        elif '#guild' in line:
            line = line.replace('#guild', str(mysql_data[x][2]))
        if tablehead:
            tablehead_html += linecopy
        if normal_content_zone:
            if "<!-- row template here -->" in line:
                table = True
                tablehead = False
                dps_sum = 0
                y = 0
                for item in mysql_data:
                    encounter = item[1]
                    encounterid = item[12]
                    if (encounter_previous and encounter != encounter_previous) \
                            or (encounterid_previous and encounterid != encounterid_previous):
                        while y < 10:
                            html += empty_row()
                            y += 1
                        dps_sum = format_number(dps_sum)
                        html += avg_raid_dps(dps_sum)
                        html += ['            </tbody>\n']
                        html += ['        </table>\n']
                        html += ['    </div>\n']
                        tablehead_html_copy = tablehead_html.replace('#date', str(mysql_data[x][0]))
                        tablehead_html_copy = tablehead_html_copy.replace('#boss', str(mysql_data[x][1]).split(" ")[0])
                        tablehead_html_copy = tablehead_html_copy.replace('#guild', str(mysql_data[x][2]))
                        html += [tablehead_html_copy]
                        dps_sum = 0
                        y = 0
                    encounter_previous = encounter
                    encounterid_previous = item[12]
                    x += 1
                    y += 1
                    dps_sum += item[6]
                    html += ['            <tr>\n']
                    i = 0
                    for data in item:
                        i += 1
                        if type(data) == int:
                            data = format_number(data)
                        if i == 1:
                            # encounterid = item[12]
                            playerid = item[13]
                            html += ['                <td scope="row">'
                                     + create_url_dps(str(encounterid), str(playerid), item[3][0:14]) + '</td>\n']
                        elif i == 11:
                                html += ['                <td scope="col">' + str(item[11]).split("0:")[1] + " | "
                                         + str(item[10]).split("0:")[1] + '</td>\n']
                        # elif i == 6:
                        #     print(data)
                        #     if 'heal/support' in data:
                        #         role = data.replace('heal/support', 'heal/su')
                        #         html += ['                <td scope="col">' + role + '</td>\n']
                        #     else:
                        #         html += ['                <td scope="col">' + data + '</td>\n']
                        elif i > 4:
                            html += ['                <td scope="col">' + str(data) + '</td>\n']
                        if i == 11:
                            break
                    html += ['            </tr>\n']
            if "<!-- end row template -->" in line:
                table = False
                html += avg_raid_dps(format_number(dps_sum))
            else:
                if not table:
                    html += [line]
    for line in html:
        if "#content" in line:
            line = line.replace("#content", content(mycursor))
        if "<!-- Footer -->" in line:
            footer = footer_html()
            for item in footer:
                file.write(item)
        file.write(line)
    file.close()
    template.close()
    print("../public/" + html_file + " created")


def create_json(mycursor, bossid, roleid):
    mysql_data = []
    for boss_id in bossid:
        for role_id in roleid:
            mysql_data += mysql_json(mycursor, str(boss_id[0]), str(role_id[0]), "DPS")
        # for role_id in roleid:
        #     mysql_data += mysql_json(mycursor, str(boss_id[0]), str(role_id[0]), "HPS")
    file = codecs.open("../public/json/data_json.txt", 'w', "utf-8")
    file.write("[\n")
    lastitem = len(mysql_data)
    i = 0
    for item in mysql_data:
        i += 1
        json = "  {\n"
        json += ('    "Date": "' + str(item[0]) + '", \n')
        json += ('    "Guild": "' + str(item[1]) + '", \n')
        json += ('    "Boss": "' + str(item[2]) + '", \n')
        json += ('    "Player": "' + str(item[3]) + '", \n')
        json += ('    "Class": "' + str(item[4]) + '", \n')
        json += ('    "Role": "' + str(item[5]) + '", \n')
        json += ('    "ST DPS": "' + format_number(item[6]) + '", \n')
        json += ('    "HPS": "' + format_number(item[7]) + '", \n')
        json += ('    "THPS": "' + format_number(item[8]) + '", \n')
        json += ('    "APS": "' + format_number(item[9]) + '", \n')
        json += ('    "Time for Boss": "' + str(item[10]).split("0:")[1] + '", \n')
        json += ('    "Total Time": "' + str(item[11]).split("0:")[1] + '", \n')
        json += ('    "Eid": "' + str(item[12]) + '", \n')
        json += ('    "Pid": "' + str(item[13]) + '"\n')
        if i < lastitem:
            json += "  },\n"
        else:
            json += "  }\n"
        file.write(json)
    file.write("]")
    file.close()
    with open('../public/json/data_json.txt', 'rb') as f_in:
        with gzip.open('../public/json/data.json', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def footer_html():
    footer = codecs.open("../template/footer.html", 'r', "utf-8").readlines()
    return footer


def main():
    mydb = mysql_connect_config.database_connect()
    mycursor = mydb.cursor()
    bossid = get_bossid(mycursor)
    classid = get_classid(mycursor)
    roleid = get_roleid(mycursor)
    leaders_html(mycursor, bossid, "index.html", "Overall DPS")
    tank_sup_dps_hps_html(mycursor, bossid, classid, "dps", "DPS", "dps.html", "Damage DPS")
    tank_sup_dps_hps_html(mycursor, bossid, classid, "heal", "DPS", "ddhps.html", "Damage DPS + HPS")
    hps_html(mycursor, bossid, classid, "heal", "DPS", 'dpshps.html', "Heal order by DPS")
    hps_html(mycursor, bossid, classid, "", "HPSAPS", 'hps.html', "Heal order by HPS")
    tank_sup_dps_hps_html(mycursor, bossid, classid, "support", "DPS", "supdps.html", "Support DPS")
    tank_sup_dps_hps_html(mycursor, bossid, classid, "support", "HPSAPS", "suphps.html", "Support HPS")
    tank_sup_dps_hps_html(mycursor, bossid, classid, "tank", "DPS", "tdps.html", "Tank DPS")
    tank_sup_dps_hps_html(mycursor, bossid, classid, "tank", "HPSAPS", "thps.html", "Tank HPS")
    top100(mycursor, 1, classid, "dps", "DPS", "top100_1.html", "Top 100 DPS - Azranel")
    top100(mycursor, 2, classid, "dps", "DPS", "top100_2.html", "Top 100 DPS - Vindicator MK1")
    top100(mycursor, 3, classid, "dps", "DPS", "top100_3.html", "Top 100 DPS - Commander Isiel")
    top100(mycursor, 4, classid, "dps", "DPS", "top100_4.html", "Top 100 DPS - Titan X")
    resources(mycursor, "mostplayed.html")
    resources(mycursor, "videos.html")
    resources(mycursor, "raidsetup.html")
    resources(mycursor, "lookup.html")
    last_uploads_html(mycursor, "latestuploads.html", "Latest Uploads")
    create_json(mycursor, bossid, roleid)


if __name__ == "__main__":
    main()
