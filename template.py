import codecs
import mysql.connector


def database_connect():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="dublin12",  # enter your password to your mysql database here
        database="rift_leaderboards")
    return mydb


def get_top_10(mycursor, bossid, classid):
    sql = "select Boss.bossname, Player.playername,Classes.class, dps, time, totaltime  from Encounter a " \
          "inner join Encounterinfo on a.encounterid = Encounterinfo.id " \
          "inner join Boss on Encounterinfo.bossid = Boss.id " \
          "inner join Player on a.playerid = Player.id " \
          "inner join Classes on Player.classid = Classes.id " \
          "where Encounterinfo.bossid = " + bossid + "  and Classes.id = " + classid + " and a.dps = (" \
          "select dps from Encounter b inner join Encounterinfo on b.encounterid = Encounterinfo.id " \
          "where Classes.id = " + classid + " and Encounterinfo.bossid = " + bossid + " and a.playerid = b.playerid " \
          "Order by b.dps desc limit 1) Order by a.dps desc limit 10"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    print(myresult)
    return myresult


def exchange(top_10):
    template = codecs.open("template_dps.html", 'r', "utf-8")
    file = codecs.open("dps.html", 'w', "utf-8")
    i = 0
    for line in template:
        if "<td>player</td>" in line:
            line = line.replace("player", (top_10[i][1]))
        elif "<td>dps</td>" in line:
            line = line.replace("dps", (str(top_10[i][3])))
        elif "<td>time</td>" in line:
            line = line.replace("time", (str(top_10[i][4])))
            i += 1
        file.write(line)
    file.close()
    template.close()


def main():
    bossid = [1, 2, 3, 4]  # 1 Azranel, 2 Vindicator MK1, 3 Commander Isiel, 4 Titan X
    classid = [4, 3, 5, 2, 1]  # 1 Cleric, 2 Mage, 3 Primalist, 4 Rogue, 5 Warrior
    top_10 = []
    mydb = database_connect()
    mycursor = mydb.cursor()
    database_connect()
    for boss_id in bossid:
        for class_id in classid:
            top_10 += get_top_10(mycursor, str(boss_id), str(class_id))
    exchange(top_10)


if __name__ == "__main__":
    main()
