import codecs
import os
import mysql_connect_config


def get_database_session(mycursor, sessionid):
    session_exist = False
    sql = "SELECT * FROM Session where sessionid ='" + sessionid + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if myresult:
        session_exist = True
    return session_exist


def add_database_session(mydb, mycursor, sessionid):
    sql = "SELECT * FROM Session where sessionid ='" + sessionid + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if not myresult:
        sql = "INSERT INTO Session (sessionid) VALUES (" + sessionid + ")"
        mycursor.execute(sql)
        mydb.commit()


def database_guild(mydb, mycursor, guild, guildname):
    if guildname not in guild:
        sql = "SELECT * FROM Guild where guildname ='" + guildname + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        if not myresult:
            sql = "INSERT INTO Guild (guildname) VALUES ('" + guildname + "')"
            mycursor.execute(sql)
            mydb.commit()
            sql = "SELECT * FROM Guild where guildname ='" + guildname + "'"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
        if myresult:
            for item in myresult:
                guild[guildname] = item[0]
    return guild


def database_boss(mycursor, boss, bossname):
    if bossname not in boss:
        sql = "SELECT id, bossname FROM Boss where bossname ='" + bossname + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for item in myresult:
            if bossname == item[1]:
                boss[bossname] = item[0]
    return boss


def get_classid(mycursor):
    classid = []
    sql = "SELECT * FROM classes"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for item in myresult:
        classid += [item]
    return classid


def player_class(classid, playerclass):
    for item in classid:
        if playerclass == item[1]:
            playerclass = item[0]
            break
    return playerclass


def database_player(mydb, mycursor, guildid, player, playerid, playername, playerclass):
    if playerid == "0":
        sql = "SELECT ptid, id FROM Player where playername ='" + playername + "' and classid ='"\
              + str(playerclass) + "'"
    else:
        sql = "SELECT id, ptid FROM Player where ptid ='" + playerid + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if not myresult:
        sql = "INSERT INTO Player (ptid, guildid, playername, classid) VALUES (%s, %s, %s, %s)"
        val = (playerid, guildid, playername, playerclass)
        mycursor.execute(sql, val)
        mydb.commit()
        # print(playername, "added to the database.")
        sql = "SELECT ptid, id FROM Player where ptid ='" + playerid + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for item in myresult:
            player = item[1]
    else:
        if playerid == "0":
            for item in myresult:
                player = item[1]
        else:
            sql = "SELECT ptid, id FROM Player where ptid ='" + playerid + "'"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            for item in myresult:
                if int(playerid) == item[0]:
                    player = item[1]

    return player


def database_role(mycursor, role):
    sql = "SELECT * FROM Roles"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for item in myresult:
            role[item[1]] = item[0]
    return role


def database_encounter(mydb, mycursor, encounterid, bossid, player, roleid, dps, hps, thps, aps, time, totaltime,
                       date, bossname, playername, guildid, playerclass):
    new_encounterid = 0
    sql = "SELECT id FROM Encounterinfo where encounterid='" + encounterid + "' and bossid='" + str(bossid) + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if myresult:
        print("Encounterid: " + encounterid + ", Boss: " + bossname + ", Player: " + playername + " already exists")
        for item in myresult:
            new_encounterid = item[0]

    else:
        print(date)
        sql = "INSERT INTO Encounterinfo (guildid, encounterid, bossid, time, totaltime, date) " \
              "VALUES (%s,%s, %s, %s, %s, %s)"
        val = (guildid, encounterid, bossid, time, totaltime, date)
        mycursor.execute(sql, val)
        mydb.commit()
        sql = "SELECT id FROM Encounterinfo where encounterid='" + encounterid + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for item in myresult:
            new_encounterid = item[0]
    if player == "0":
        sql = "SELECT ptid FROM Player where playername ='" + playername + "' and classid ='" + playerclass + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for item in myresult:
            player = item[0]

    sql = "SELECT id FROM Encounter where playerid ='" + str(player) + "' and encounterid='" + str(new_encounterid)\
          + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if not myresult:
        sql = "INSERT INTO Encounter (encounterid, playerid, roleid, dps, hps, thps, aps)" \
              " VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (new_encounterid, player, roleid, dps, hps, thps, aps)
        mycursor.execute(sql, val)
        mydb.commit()
        print(bossname + " - " + playername + " - " + dps)


def change_rolename(rolename):
    if "unknown/" in rolename:
        rolename = rolename.split("unknown/")[1]
    if rolename == "support/heal":
        rolename = "heal/support"
    elif rolename == "support/dps":
        rolename = "dps/support"
    elif rolename == "support/tank":
        rolename = "tank/support"
    elif rolename == "heal/tank":
        rolename = "tank/heal"
    elif rolename == "dps/tank":
        rolename = "tank/dps"
    elif rolename == "tank/support/heal":
        rolename = "tank/heal/support"
    elif rolename == "tank/heal/dps" or rolename == "dps/heal/tank":
        rolename = "tank/dps/heal"
    elif rolename == "support/heal/dps" or rolename == "heal/dps/support":
        rolename = "dps/heal/support"
    return rolename


def main():
    guild = {}
    player = ""
    role = {}
    boss = {}
    mydb = mysql_connect_config.database_connect()
    mycursor = mydb.cursor()
    role = database_role(mycursor, role)
    classid = get_classid(mycursor)
    print("Transfer data to the database")
    if os.path.isfile("../help_files/dps.tsv"):
        file = codecs.open("../help_files/dps.tsv", 'r', "utf-8")
        for item in file:
            line = item.strip()
            line = line.split("\t")
            date = line[0]
            encounterid = line[1]
            bossname = line[2]
            playername = line[3]
            playerclass = line[4]
            dps = line[5]
            time = "00:" + line[6]
            rolename = line[7]
            rolename = change_rolename(rolename)
            guildname = line[8]
            totaltime = line[9]
            if totaltime == "?":
                totaltime = "59:59"
            totaltime = "00:" + totaltime
            playerid = line[10]
            hps = line[11]
            thps = line[12]
            print(line[13])
            aps = line[13]
            # session = database_session(mydb, mycursor, session, sessionid)
            guild = database_guild(mydb, mycursor, guild, guildname)
            # print(guild[guildname])
            boss = database_boss(mycursor, boss, bossname)
            playerclass = player_class(classid, playerclass)
            player = database_player(mydb, mycursor, guild[guildname], player, playerid, playername, playerclass)
            # print(playername + "-" + str(dps) + " - " + playerid)
            database_encounter(mydb, mycursor, encounterid, boss[bossname], player, role[rolename], dps,
                               hps, thps, aps, time, totaltime, date, bossname, playername, guild[guildname],
                               playerclass)
            # print(boss)
        file.close()


if __name__ == "__main__":
    main()
