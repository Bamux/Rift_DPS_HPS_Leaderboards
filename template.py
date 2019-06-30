import codecs
import locale
import mysql.connector


def database_connect():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",  # enter your password to your mysql database here
        database="rift_leaderboards")
    return mydb


def mysql_leaders_html_comps(mycursor, bossid, number_of_players):
    time = "totaltime"
    if bossid == "2":
        time = "time"
    sql = "select playername, dps, time, totaltime, date, hps, class, role, a.encounterid, ptid, guildname " \
          "from Encounterinfo a " \
          "inner join Encounter on a.id = Encounter.encounterid " \
          "inner join Player on Encounter.playerid = Player.id " \
          "inner join Classes on Player.classid = Classes.id " \
          "inner join Roles on Encounter.roleid = Roles.id " \
          "inner join Guild on Guild.id = a.guildid " \
          "where bossid = " + bossid + " " \
          "order by " + time + ", date, Encounter.dps desc limit " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_leaders_html_fastest_kills(mycursor, bossid, number_of_players):
    mintime = " time, Min(totaltime) as mintime"
    time = "totaltime"
    if bossid == "2":
        mintime = " Min(time) as mintime, totaltime"
        time = "time"
    sql = "select Guild.guildname, sum(dps), " + mintime + ", a.encounterid from Encounterinfo a " \
          "inner join Encounter on a.id = Encounter.encounterid " \
          "inner join Guild on a.guildid = Guild.id " \
          "where a.bossid = " + bossid + " and a.id = ( " \
          "select id from Encounterinfo b " \
          "where b.bossid = " + bossid + " and b.guildid = a.guildid " \
          "order by b." + time + " limit 1) " \
          "group by Guild.guildname " \
          "order by mintime, dps limit " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_top_dps_hps(mycursor, bossid, classid, number_of_players, role, dps_hps):
    condition = ""
    if role:
        condition = " and Roles.role like '%" + role + "%'"
    elif classid:
        condition = " and Player.classid = " + classid + ""
    sql = "SELECT playername, dps AS DPS, time, totaltime, date, HPSAPS, class, role, " \
          "encounterid, ptid, aps, thps FROM ( " \
          "SELECT DISTINCT playername, dps, a.encounterid, playerid AS id, dps AS max_dps_hps ," \
          " TIME, totaltime, date, hps + aps as HPSAPS, class, role, ptid, aps, thps FROM Encounterinfo a " \
          "INNER JOIN Encounter ON a.id = Encounter.encounterid " \
          "INNER JOIN Player ON Encounter.playerid = Player.id " \
          "inner join Classes on Player.classid = Classes.id " \
          "inner join Roles on Encounter.roleid = Roles.id " \
          "WHERE bossid = " + bossid + condition + " " \
          "ORDER BY " + dps_hps + " DESC) AS top_dps_hps " \
          "GROUP BY playername " \
          "ORDER BY " + dps_hps + " DESC LIMIT " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def format_number(number):
    locale.setlocale(locale.LC_NUMERIC, "german")
    number = locale.format("%.0f", number, grouping=True)
    return number


def create_url_dps(encounterid, playerid, text):
    url = "https://prancingturtle.com"
    url = '<a href="' + url + '/Encounter/Interaction?id=' + encounterid + "&p=" + playerid + \
          '&outgoing=True&type=DPS&mode=ability&filter=all" target="_blank">' + text + "</a>"
    return url


def create_url_overview(encounterid, text):
    url = "https://prancingturtle.com"
    url = '<a href="' + url + '/Encounter/PlayerDamageDone/' + encounterid + '" target="_blank">' + text + "</a>"
    return url


def exchange(template, file, mysql_data):  # exchanges the placeholders in the template file with the mysql data
    i = 0
    tbody = False
    header = ""
    for line in template:
        if "<h2>" in line:
            header = line.split("<h2>")[1].split("</h2>")[0]
        if "<tbody>" in line:
            tbody = True
        elif "</tbody>" in line:
            tbody = False
        elif "#guild" in line:
            line = line.replace("#guild", mysql_data[i][10])
        elif "#class" in line:
            line = line.replace("#class", mysql_data[i][6])
            # print(i)
        if tbody:
            if "#name" in line:
                name = mysql_data[i][0]
                if header == "Fastest Kills":
                    name = create_url_overview(str(mysql_data[i][4]), str(mysql_data[i][0]))
                line = line.replace("#name", name)
            elif "#dps" in line:
                line = line.replace("#dps", format_number(mysql_data[i][1]))
            elif "#date" in line:
                url = create_url_dps(str(mysql_data[i][8]), str(mysql_data[i][9]), str(mysql_data[i][4]))
                line = line.replace("#date", url)
            elif "#hps" in line:
                line = line.replace("#hps", format_number(mysql_data[i][5]))
            elif "#thps" in line:
                line = line.replace("#thps", format_number(mysql_data[i][11]))
            elif "#ohps" in line:
                hps = (mysql_data[i][5] - mysql_data[i][10])
                ohps = mysql_data[i][11] - hps
                line = line.replace("#ohps", format_number(ohps))
            elif "#aps" in line:
                line = line.replace("#aps", format_number(mysql_data[i][10]))
            elif "#time" in line:
                time = str(mysql_data[i][2]).split("0:0")[1]
                line = line.replace("#time", time)
            elif "#totaltime" in line:
                time = str(mysql_data[i][3]).split("0:0")[1]
                line = line.replace("#totaltime", time)
            elif "#role" in line:
                role = mysql_data[i][7]
                if "/heal/support" in role:
                    role = role.replace("/heal/support", "/heal/s")
                elif "/support" in role:
                    role = role.replace("/support", "/supp")
                url = create_url_dps(str(mysql_data[i][8]), str(mysql_data[i][9]), role)
                # line = line.replace("#date", url)
                line = line.replace("#role", url)
            elif "#fastest_time" in line:
                time = str(mysql_data[i-1][2]).split("0:0")[1]
                line = line.replace("#fastest_time", time)
            elif "#avg" in line:
                line = line.replace("#avg", format_number(mysql_data[i]))
            elif "</tr>" in line:
                i += 1
        file.write(line)


def average(data, number_of_players, dps_hps):
    dps_sum = 0
    place = 1
    if dps_hps == "HPS":
        place = 5
    for dps in data:
        dps_sum += (dps[place])
    dps_sum = round(dps_sum/number_of_players)
    return dps_sum


def leaders_html(mycursor, bossid, html_file):
    mysql_data = []
    roles = ["support", "tank", "heal"]
    template = codecs.open("template/" + html_file, 'r', "utf-8")
    file = codecs.open("public/" + html_file, 'w', "utf-8")
    number_of_players = 10
    for boss_id in bossid:
        data = mysql_leaders_html_fastest_kills(mycursor, str(boss_id), str(number_of_players))
        mysql_data += data + [average(data, number_of_players, "DPS")]
    for boss_id in bossid:
        data = mysql_leaders_html_comps(mycursor, str(boss_id), str(number_of_players))
        mysql_data += data + [average(data, number_of_players, "DPS")]
    number_of_players = 15
    for boss_id in bossid:
        data = mysql_top_dps_hps(mycursor, str(boss_id), "", str(number_of_players), "", "DPS")
        mysql_data += data + [average(data, number_of_players, "DPS")]
    number_of_players = 10
    for role in roles:
        for boss_id in bossid:
            data = mysql_top_dps_hps(mycursor, str(boss_id), "", str(number_of_players), role, "DPS")
            mysql_data += data + [average(data, number_of_players, "DPS")]
    exchange(template, file, mysql_data)
    file.close()
    template.close()
    print("public/" + html_file + " created")


def dps_html(mycursor, bossid, classid, html_file):
    mysql_data = []
    template = codecs.open("template/" + html_file, 'r', "utf-8")
    file = codecs.open("public/" + html_file, 'w', "utf-8")
    number_of_players = 10
    role = ""
    for boss_id in bossid:
        for class_id in classid:
            data = mysql_top_dps_hps(mycursor, str(boss_id), str(class_id), str(number_of_players), role, "DPS")
            mysql_data += data + [average(data, number_of_players, "DPS")]
    exchange(template, file, mysql_data)
    file.close()
    template.close()
    print("public/" + html_file + " created")


def hps_html(mycursor, bossid, classid, html_file):
    mysql_data = []
    template = codecs.open("template/" + html_file, 'r', "utf-8")
    file = codecs.open("public/" + html_file, 'w', "utf-8")
    number_of_players = 15
    for boss_id in bossid:
        if boss_id != 2:
            data = mysql_top_dps_hps(mycursor, str(boss_id), "", str(number_of_players), "", "HPSAPS")
            mysql_data += data + [average(data, number_of_players, "HPS")]
    number_of_players = 10
    for class_id in classid:
        for boss_id in bossid:
            if boss_id != 2:
                data = mysql_top_dps_hps(mycursor, str(boss_id), str(class_id), str(number_of_players), "", "HPSAPS")
                mysql_data += data + [average(data, number_of_players, "HPS")]
    exchange(template, file, mysql_data)
    file.close()
    template.close()
    print("public/" + html_file + " created")


def main():
    bossid = [1, 2, 3, 4]  # 1 Azranel, 2 Vindicator MK1, 3 Commander Isiel, 4 Titan X
    classid = [4, 3, 5, 2, 1]  # 1 Cleric, 2 Mage, 3 Primalist, 4 Rogue, 5 Warrior
    mydb = database_connect()
    mycursor = mydb.cursor()
    database_connect()
    leaders_html(mycursor, bossid, "leaders.html")
    dps_html(mycursor, bossid, classid, "dps.html")
    hps_html(mycursor, bossid, classid, 'hps.html')


if __name__ == "__main__":
    main()
