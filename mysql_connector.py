import codecs
import os
import mysql.connector


def database_connect():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",  # enter your password to your mysql database here
        database="rift_leaderboards") # enter your database name
    print(mydb)
    return mydb


def database_session(mydb, mycursor, session, sessionid):
    if sessionid not in session:
        sql = "SELECT * FROM Session where sessionid ='" + sessionid + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        if not myresult:
            sql = "INSERT INTO Session (sessionid) VALUES (" + sessionid + ")"
            mycursor.execute(sql)
            mydb.commit()
        session += [sessionid]
    return session


def database_guild(mydb, mycursor, guild, guildname):
    if guildname not in guild:
        sql = "SELECT * FROM Guild where guildname ='" + guildname + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        if not myresult:
            sql = "INSERT INTO Guild (guildname) VALUES ('" + guildname + "')"
            print(sql)
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


def database_player(mydb, mycursor, guildid, player, playerid, playername, playerclass):
    if playerid not in player:
        sql = "SELECT id, ptid FROM Player where ptid ='" + playerid + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        if not myresult:
            sql = "INSERT INTO Player (ptid, guildid, playername, class) VALUES (%s, %s, %s, %s)"
            val = (playerid, guildid, playername, playerclass)
            mycursor.execute(sql, val)
            mydb.commit()
            print(playername, "added to the database.")
            sql = "SELECT ptid, id FROM Player where ptid ='" + playerid + "'"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            for item in myresult:
                player[playerid] = item[1]
        else:
            sql = "SELECT ptid, id FROM Player where ptid ='" + playerid + "'"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            for item in myresult:
                if int(playerid) == item[0]:
                    player[playerid] = item[1]
    return player


def database_role(mycursor, role):
    sql = "SELECT * FROM Role"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for item in myresult:
            role[item[1]] = item[0]
    return role


def database_encounter(mydb, mycursor, encounterid, bossid, playerid, roleid, dps, hps, thps, aps, time, totaltime,
                       date):
    sql = "SELECT id FROM Encounter where Playerid ='" + str(playerid) + "' and encounterid='" + encounterid + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if not myresult:
        sql = "INSERT INTO Encounter (encounterid, bossid, playerid, roleid, dps, hps, thps, aps, time, totaltime, " \
              "date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
        val = (encounterid, bossid, playerid, roleid, dps, hps, thps, aps, time, totaltime, date)
        mycursor.execute(sql, val)
        mydb.commit()
        print(encounterid + " " + str(playerid), " added to the database.")


def main():
    # session = []
    guild = {}
    player = {}
    role = {}
    boss = {}
    mydb = database_connect()
    mycursor = mydb.cursor()
    database_connect()
    role = database_role(mycursor, role)
    if os.path.isfile("dps.tsv"):
        file = codecs.open("dps.tsv", 'r', "utf-8")
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
            guildname = line[8]
            totaltime = line[9]
            if totaltime == "?":
                totaltime = "59:59"
            totaltime = "00:" + totaltime
            playerid = line[10]
            hps = line[11]
            thps = line[12]
            aps = line[13]
            # session = database_session(mydb, mycursor, session, sessionid)
            guild = database_guild(mydb, mycursor, guild, guildname)
            # print(guild)
            boss = database_boss(mycursor, boss, bossname)
            player = database_player(mydb, mycursor, guild[guildname], player, playerid, playername, playerclass)
            # print(player)
            database_encounter(mydb, mycursor, encounterid, boss[bossname], player[playerid], role[rolename], dps,
                               hps, thps, aps, time, totaltime, date)
            # print(boss)
        file.close()


if __name__ == "__main__":
    main()
