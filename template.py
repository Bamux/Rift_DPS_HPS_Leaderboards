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
    sql = "select playername, dps, time, totaltime, date, hps, class, " \
          "role, guildname " \
          "from Encounterinfo inner join Encounter on Encounterinfo.id = Encounter.encounterid " \
          "inner join Player on Encounter.playerid = Player.id " \
          "inner join Classes on Player.classid = Classes.id " \
          "inner join Roles on Encounter.roleid = Roles.id " \
          "inner join Guild on Guild.id = Encounterinfo.guildid " \
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
    sql = "select Guild.guildname, sum(dps), " + mintime + " from Encounterinfo a " \
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


def mysql_leaders_html_top_dps_overall(mycursor, bossid, number_of_players):
    sql = "SELECT playername, dps AS DPS, time, totaltime, date, hps, class, role FROM ( " \
          "SELECT DISTINCT playername, dps, a.encounterid, playerid AS id, dps AS maxdps ," \
          " TIME, totaltime, date, hps, class, role FROM Encounterinfo a " \
          "INNER JOIN Encounter ON a.id = Encounter.encounterid " \
          "INNER JOIN Player ON Encounter.playerid = Player.id " \
          "inner join Classes on Player.classid = Classes.id " \
          "inner join Roles on Encounter.roleid = Roles.id " \
          "WHERE bossid = " + bossid + " " \
          "ORDER BY maxdps DESC) AS Maxdps " \
          "GROUP BY playername " \
          "ORDER BY DPS DESC LIMIT " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def mysql_leaders_html_top_dps_role(mycursor, bossid, number_of_players, role):
    sql = "SELECT playername, dps AS DPS, time, totaltime, date, hps, class, role, encounterid FROM ( " \
          "SELECT DISTINCT playername, dps, a.encounterid, playerid AS id, dps AS maxdps ," \
          " TIME, totaltime, date, hps, class, role, encounterid FROM Encounterinfo a " \
          "INNER JOIN Encounter ON a.id = Encounter.encounterid " \
          "INNER JOIN Player ON Encounter.playerid = Player.id " \
          "inner join Classes on Player.classid = Classes.id " \
          "inner join Roles on Encounter.roleid = Roles.id " \
          "WHERE bossid = " + bossid + " and Roles.role like '%" + role + "%' " \
          "ORDER BY maxdps DESC) AS Maxdps " \
          "GROUP BY playername " \
          "ORDER BY DPS DESC LIMIT " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    print(myresult)
    return myresult


def mysql_dps_html(mycursor, bossid, classid, number_of_players):
    sql = "select Player.playername, max(dps) as maxdps, time, totaltime  from Encounter a " \
          "inner join Encounterinfo on a.encounterid = Encounterinfo.id " \
          "inner join Player on a.playerid = Player.id " \
          "inner join Classes on Player.classid = Classes.id " \
          "where Encounterinfo.bossid = " + bossid + " and Player.classid = " + classid + " " \
          "group by Player.id " \
          "order by maxdps desc limit " + number_of_players + ""
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult


def format_number(number):
    locale.setlocale(locale.LC_NUMERIC, "german")
    number = locale.format("%.0f", number, grouping=True)
    return number


def exchange(template, file, mysql_data):  # exchanges the placeholders in the template file with the mysql data
    i = 0
    tbody = False
    for line in template:
        if "<tbody>" in line:
            tbody = True
        elif "</tbody>" in line:
            tbody = False
        elif "#guild" in line:
            line = line.replace("#guild", mysql_data[i][8])
        if tbody:
            if "#name" in line:
                line = line.replace("#name", mysql_data[i][0])
            if "#class" in line:
                line = line.replace("#class", mysql_data[i][6])
            elif "#dps" in line:
                line = line.replace("#dps", format_number(mysql_data[i][1]))
            elif "#date" in line:
                line = line.replace("#date", str(mysql_data[i][4]))
            elif "#hps" in line:
                line = line.replace("#hps", format_number(mysql_data[i][5]))
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
                line = line.replace("#role", role)
            elif "#fastest_time" in line:
                time = str(mysql_data[i-1][2]).split("0:0")[1]
                line = line.replace("#fastest_time", time)
            elif "#avg" in line:
                line = line.replace("#avg", format_number(mysql_data[i]))
            elif "</tr>" in line:
                i += 1
        file.write(line)


def average(data, number_of_players):
    dps_sum = 0
    for dps in data:
        dps_sum += (dps[1])
    dps_sum = round(dps_sum/number_of_players)
    return dps_sum


def leaders_html(mycursor, bossid):
    mysql_data = []
    roles = ["support", "tank", "heal"]
    template = codecs.open("template/leaders.html", 'r', "utf-8")
    file = codecs.open("public/leaders.html", 'w', "utf-8")
    number_of_players = 10
    for boss_id in bossid:
        data = mysql_leaders_html_fastest_kills(mycursor, str(boss_id), str(number_of_players))
        mysql_data += data + [average(data, number_of_players)]
    for boss_id in bossid:
        data = mysql_leaders_html_comps(mycursor, str(boss_id), str(number_of_players))
        mysql_data += data + [average(data, number_of_players)]
    number_of_players = 15
    for boss_id in bossid:
        data = mysql_leaders_html_top_dps_overall(mycursor, str(boss_id), str(number_of_players))
        mysql_data += data + [average(data, number_of_players)]
    number_of_players = 10
    for role in roles:
        for boss_id in bossid:
            data = mysql_leaders_html_top_dps_role(mycursor, str(boss_id), str(number_of_players), role)
            mysql_data += data + [average(data, number_of_players)]
    exchange(template, file, mysql_data)
    file.close()
    template.close()


def dps_html(mycursor, bossid, classid):
    mysql_data = []
    html_file = "dps.html"
    template = codecs.open("template/" + html_file, 'r', "utf-8")
    file = codecs.open("public/dps.html", 'w', "utf-8")
    number_of_players = 10
    for boss_id in bossid:
        for class_id in classid:
            data = mysql_dps_html(mycursor, str(boss_id), str(class_id), "10")
            mysql_data += data + [average(data, number_of_players)]
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
    # dps_html(mycursor, bossid, classid)
    leaders_html(mycursor, bossid)


if __name__ == "__main__":
    main()
