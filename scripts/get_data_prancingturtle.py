# -*- coding: utf-8 -*-

import codecs
import requests
from datetime import datetime
import math
import os
import mysql_connect_config
import mysql_add_data


def get_session_id(mydb, mycursor, delta, month, sid, url):
    session_key = []
    print(url)
    html = requests.get(url).text
    html = html.split("<h5>(All sessions that included this encounter)</h5>")[1]
    session = html.split('Session/')
    for item in session:
        delta_day = 0
        delta_month = 0
        if "ago" in item:
            if " day" in item:
                days = item.split(" day")[0]
                days = days.split("<b>")[1]
                delta_day = int(days)
            elif " month" in item:
                months = item.split(" month")[0]
                if "<b>" in months:
                    months = months.split("<b>")[1]
                    delta_month = int(months)
            if delta_day <= delta and delta_month <= month:
                if "Detail/" in item:
                    item = item.split("Detail/")[1]
                    item = item.split('">')[0]
                    if item not in sid:
                        session_exist = mysql_add_data.get_database_session(mycursor, item)
                        if not session_exist:
                            session_key += [str(item)]
    return session_key


def get_encounter_id(sid, boss, website, parse_date):
    encounters_id = []
    new_encounterid = []
    for item in sid:
        encounterid = []
        url = website + "/Session/Detail/" + item
        html = requests.get(url).text
        date = html.split('<div class="col-lg-3">')[1]
        date = date.split(" ")[0]
        d = datetime.strptime(date, '%d/%m/%Y')
        date = d.strftime('%Y-%m-%d')
        if date >= parse_date:
            print(date + " " + url)
            guild = html.split('>&lt;')[1]
            guild = guild.split('&gt;</a>')[0]
            # print(guild)
            encounters = html.split('RemoveSelectedEncounters')[1]
            encounters = encounters.split('<a href="/Session/')
            for encounter in encounters:
                if ">Kill<" in encounter:
                    boss_id = encounter.split('BossFight/')[1]
                    boss_id = boss_id.split("?d")[0]
                    if int(boss_id) in boss:
                        if "Overview/" in encounter:
                            encounter = encounter.split("Overview/")[1]
                            encounter = encounter.split('">')[0]
                            encounterid += [encounter]
                            # print(encounter)
            if encounterid:
                encounters_id += [[date, guild, encounterid]]
    encounters_id.sort()
    print(encounters_id)
    for item_encounter in encounters_id:
        for eid in item_encounter[2]:
            new_encounterid += [[eid, item_encounter[0], item_encounter[1]]]
    return new_encounterid


def cf_decode_email(encodedstring):
    r = int(encodedstring[:2], 16)
    name = ''.join([chr(int(encodedstring[i:i + 2], 16) ^ r) for i in range(2, len(encodedstring), 2)])
    name = name.split("@")[0]
    return name


def ability_role():
    abilities = []

    role = "support"
    abilities += [["Wild Storms", role, "Primalist"]]  # Mystic
    abilities += [["Glacial Insignia", role, "Cleric"]]  # Oracle
    abilities += [["Wasting Insignia", role, "Cleric"]]  # Oracle
    abilities += [["Burning Purpose", role, "Mage"]]  # Archon
    abilities += [["Coda of Wrath", role, "Rogue"]]  # Bard
    abilities += [["Power Chord", role, "Rogue"]]  # Bard
    abilities += [["Flesh Rip", role, "Warrior"]]  # Beastmaster

    role = "dps"
    abilities += [["Condemn", role, "Mage"]]  # Mage Necro
    abilities += [["Atrophy", role, "Mage"]]  # Mage Warlock
    abilities += [["Rising Waterfall", role, "Warrior"]]  # Warrior Paragon Skyfall
    abilities += [["Fae Mimicry", role, "Cleric"]]  # Druid
    abilities += [["Bound Fate", role, "Cleric"]]  # Cabalist
    abilities += [["Lebensanstieg", role, "Cleric"]]  # Druid
    abilities += [["Rapid Fire Shot", role, "Rogue"]]  # Marksman
    abilities += [["Hellfire Blades", role, "Rogue"]]  # Nightblade
    # abilities += [["Miserly Affliction", role, "Cleric"]]  # Defiler

    role = "tank"
    abilities += [["Unstable Reaction", role, "Warrior"]]  # Void Knight
    abilities += [["Counter Shock", role, "Mage"]]  # Arbiter
    abilities += [["Icy Fury", role, "Mage"]]  # Arbiter
    abilities += [["Hammer of Faith", role, "Cleric"]]
    abilities += [["Shattered Reflection", role, "Mage"]]  # Arbiter
    abilities += [["Guarded Steel", role, "Rogue"]]  # Riftstalker
    abilities += [["Planar Splash", role, "Rogue"]]  # Riftstalker
    abilities += [["Phantom Blow", role, "Rogue"]]  # Riftstalker
    abilities += [["Tempest", role, "Warrior"]]  # Void Knight
    # abilities += [["Retaliation", role, "Warrior"]]  # Paladin
    abilities += [["Balance of Power", role, "Warrior"]]  # Paladin
    abilities += [["Protector's Fury", role, "Warrior"]]  # Paladin
    abilities += [["Crystalline Smash", role, "Primalist"]]  # Titan

    role = "heal"
    abilities += [["Ruin", role, "Mage"]]  # Mage Chloromancer

    return abilities


def get_role(url, boss):
    ability_name = []
    url += boss + "&outgoing=False&type=DPS&mode=ability&filter=all"
    abilities = ability_role()
    # print(abilities)
    html = requests.get(url).text
    html = html.split("All Abilities")[1]
    html = html.split(")</b></td>")
    for player in html:
        if "<td><b>" in player:
            player = player.split("<td><b>")[1]
            name = player.split(" (")[1]
            abilityname = player.split(" (")[0]
            abilityname = abilityname.encode('ascii', 'xmlcharrefreplace')
            abilityname = abilityname.decode('utf-8')
            if "data-cfemail" in name:
                name = name.split('data-cfemail="')[1]
                name = name.split('">')[0]
                name = cf_decode_email(name)
            for ability in abilities:
                if ability[0] == abilityname:
                    ability_name += [[name, ability[0], ability[1], ability[2]]]
    return ability_name


def get_player_hps_ohps(website, eid, playerid):
    heal = []
    url = website + '/Encounter/Interaction?id=' + eid + '&p=' + playerid + '&outgoing=True&type=HPS&mode=ability&' \
                                                                            'filter=all'
    html = requests.get(url).text
    if '<td class="text-center text-warning"><b>' in html:
        thps = html.split('<td class="text-center text-warning"><b>')[1]
        ehps = thps.split('</b></td>')[0]
        thps = html.split('<td><b>All Abilities')[1]
        thps = thps.split('<td class="text-center">')
        thps = thps[4].split('</td>')[0]
        heal = [ehps, thps]
    return heal


def get_player_aps(website, eid, playerid):
    aps = 0
    url = website + '/Encounter/Interaction?id=' + eid + '&p=' + playerid + '&outgoing=True&type=APS&mode=ability&' \
                                                                            'filter=all'
    # print(url)
    html = requests.get(url).text
    if 'All Abilities' in html:
        aps = html.split("All Abilities")[1]
        # print(aps)
        if '<td class="text-center">' in aps:
            aps = aps.split('<td class="text-center">')
            aps = aps[2].split('</td>')[0]
            # print(aps)
    return aps


def get_tank_role(website, eid, playerid):
    url = website + "Encounter/Interaction?id=" + eid + "&p=" + playerid + "&outgoing=False&type=DPS&mode=ability" \
                                                                           "&filter=all"
    html = requests.get(url).text
    tank_role = False
    encounter = "unknown"
    if "Overview/" in html:
        encounter = html.split("/Encounter/Overview")[1]
        encounter = encounter.split(" (")[0]
        encounter = encounter.split('">')[1]
    encounter_attack = "<td><b>attack (" + encounter
    if encounter_attack in html:
        print(url)
        attack = html.split("<td><b>attack (")[1]
        attack = attack.split('<td class="text-center info">')[0]
        attack = attack.split('<td class="text-center">')
        try:
            attack = int(attack[6].split('</td>')[0].strip())
        except:
            attack = int(attack[7].split('</td>')[0].strip())
        print("attack: " + str(attack))
        if attack > 10:
            tank_role = True
    return tank_role


def get_player_class_dps(eid, player_class, website):
    print("get player, class and dps:")
    infos = []
    fight_length = -1
    for item in eid:
        url = website + "Encounter/PlayerDamageDone/" + item[0]
        print(url)
        html = requests.get(url).text
        players = html.split('roles/')
        roles = []
        for player in players:
            name = ""
            p_class = "unknown"
            role = "unknown"
            playerid = ""
            hps = 0
            ohps = 0
            aps = 0
            if 'id="chkComparePlayer' in player:
                playerid = player.split('id="chkComparePlayer')[1]
                playerid = playerid.split('"')[0]
                aps = get_player_aps(website, item[0], playerid)
                heal = get_player_hps_ohps(website, item[0], playerid)
                if heal:
                    hps = heal[0]
                    ohps = heal[1]
            if "raid_icon_role" in player:
                role = player.split('raid_icon_role_')[1]
                role = role.split(".png")[0]
                if role == "support" or role == "tank":
                    role = "unknown"
            if "-mage" in player:
                name = player.split('-mage">')[1]
                p_class = "Mage"
            elif "-cleric" in player:
                name = player.split('-cleric">')[1]
                p_class = "Cleric"
            elif "-rogue" in player:
                name = player.split('-rogue">')[1]
                p_class = "Rogue"
            elif "-warrior" in player:
                name = player.split('-warrior">')[1]
                p_class = "Warrior"
            elif "-primalist" in player:
                name = player.split('-primalist">')[1]
                p_class = "Primalist"
            elif 'class="unknown">' in player:
                name = player.split('class="unknown">')[1]
                p_class = "unknown"
            if "data-cfemail" in name:
                name = name.split('data-cfemail="')[1]
                name = name.split('">')[0]
                name = cf_decode_email(name)
            else:
                name = name.split('</span>')[0]
            if name:
                name = name.encode('ascii', 'xmlcharrefreplace')
                name = name.decode('utf-8')
                if role != "tank" and playerid:
                    if get_tank_role(website, item[0], playerid):
                        role = "tank"
                roles += [[name, role, playerid, hps, ohps, aps]]
                if p_class != "unknown":
                    player_class.update({name: p_class})
        print(roles)
        url = website + "Encounter/NpcDamageTaken/" + item[0]
        print(url)
        html = requests.get(url).text
        encounter_name = html.split('Encounter: ')[1]
        encounter_name = encounter_name.split("</h4>")[0]
        print(encounter_name)
        npc = []
        encounter = html.split('&outgoing')[0]
        encounter = encounter.split('&n=')[1]
        npc += [encounter]
        if encounter_name == "Commander Isiel":
            if 'Vergelter Ausf. 1' in html:
                vindicator = html.split("DPS graph for Vergelter Ausf. 1")[1]
            elif 'Vengeur I' in html:
                vindicator = html.split("DPS graph for Vengeur I")[1]
            else:
                vindicator = html.split("DPS graph for Vindicator MK1")[1]
            vindicator = vindicator.split('&outgoing')[0]
            vindicator = vindicator.split('&n=')[1]
            npc += [vindicator]
        for boss in npc:
            url = website + "/Encounter/Interaction?id=" + item[0] + "&n="
            ability_name = get_role(url, boss)
            for playername in ability_name:
                print(playername)
                player_class.update({playername[0]: playername[3]})
            url += boss + "&outgoing=False&type=DPS&mode=target&filter=all"
            print(url)
            html = requests.get(url).text
            encounter_name = html.split("<title>")[1]
            encounter_name = encounter_name.split(": ")[0]
            if encounter_name == 'Vergelter Ausf. 1' or encounter_name == 'Vengeur I':
                encounter_name = "Vindicator MK1"
            elif encounter_name == 'Kommandant Isiel' or encounter_name == 'Commandant Isiel':
                encounter_name = "Commander Isiel"
            players = html.split('<td></td>')
            first_hit = False
            totaldamage = 0
            data = html.split("data: [")[1]
            data = data.split("]")[0]
            data = data.split(", ")
            i = -1
            dps = ""
            counter = 0
            fight_length_counter = 0
            total_dps = 0
            # fight_length_prancingturtle = (len(data))
            if encounter_name == "Vindicator MK1":
                for total_dps in data:
                    if totaldamage <= 770399979.2:  # reach 60 % hp until phase change
                        i += 1
                        totaldamage += int(total_dps)
                        # print(str(i) + ": " + str(int(total_dps)) + " - " + str(totaldamage))
                    else:
                        break
            else:
                fight_length = -1
                for total_dps in data:
                    if int(total_dps) > 0:
                        first_hit = True
                        i += counter
                        i += 1
                        fight_length += fight_length_counter
                        fight_length += 1
                        counter = 0
                        fight_length_counter = 0
                    else:
                        fight_length_counter += 1
                        if first_hit:
                            counter += 1
                        if counter == 4:
                            break
            seconds_with_encounter = i
            if seconds_with_encounter == fight_length and int(total_dps) > 0:
                seconds_with_encounter += 1
                fight_length += 1
            elif int(total_dps) > 0:
                if encounter_name != "Vindicator MK1":
                    fight_length += 1
            dps_names = []
            minute = 0
            second = 0
            encounter_time = 0
            for player in players:
                role = "unknown"
                if "<td><b>" in player:
                    name = player.split('<td><b>')[1]
                    if "data-cfemail" in name:
                        name = name.split('data-cfemail="')[1]
                        name = name.split('">')[0]
                        name = cf_decode_email(name).encode('ascii', 'xmlcharrefreplace')
                        name = name.decode('utf-8')
                    else:
                        name = name.split('</b></td>')[0].encode('ascii', 'xmlcharrefreplace')
                        name = name.decode('utf-8')
                    if "All Sources" not in name:
                        dps_names += [name]
                        if encounter_name == "Vindicator MK1":
                            playerdata = html.split("name: 'Average'")[1]
                            playerdata = playerdata.split(", { data:")
                            for pdata in playerdata:
                                if name in pdata:
                                    pdata = pdata.split("], name: '" + name)[0]
                                    pdata = pdata.split("[")[1]
                                    pdata = pdata.split(", ")
                                    player_total_dmg = 0
                                    x = -1
                                    for playerdamage in pdata:
                                        if x <= seconds_with_encounter:
                                            player_total_dmg += int(playerdamage)
                                            x += 1
                                    dps = str((round(player_total_dmg / seconds_with_encounter)))
                                    break
                        else:
                            if 'text-center">' in player:
                                player_total_dmg = player.split('text-center">')[1]
                                player_total_dmg = player_total_dmg.split('</td>')[0]
                                dps = str((round(int(player_total_dmg) / seconds_with_encounter)))
                                # print(player_total_dmg)
                        p_class = player_class.get(name, "unknown")
                        minute = math.floor((seconds_with_encounter % 3600) / 60)
                        minute = '{:02}'.format(minute)
                        second = math.floor(seconds_with_encounter % 60)
                        second = '{:02}'.format(second)
                        encounter_time_minute = math.floor((fight_length % 3600) / 60)
                        encounter_time_minute = '{:02}'.format(encounter_time_minute)
                        encounter_time_second = math.floor(fight_length % 60)
                        encounter_time_second = '{:02}'.format(encounter_time_second)
                        encounter_time = str(encounter_time_minute) + ":" + str(encounter_time_second)
                        # role = "unknown"
                        hps = 0
                        thps = 0
                        aps = 0
                        playerid = 0
                        for name_role in roles:
                            if name == name_role[0]:
                                if role == "unknown":
                                    role = name_role[1]
                                playerid = name_role[2]
                                hps = name_role[3]
                                thps = name_role[4]
                                aps = name_role[5]
                                if int(thps) > 400000:
                                    if role != "heal":
                                        role = role + "/heal"
                        for name_role in ability_name:
                            if name == name_role[0]:
                                if role == "unknown":
                                    role = name_role[2]
                                else:
                                    if name_role[2] not in role:
                                        role += "/" + name_role[2]
                        if "- Lemme Smash -" in item[2]:
                            item[2] = "Lemme Smash"
                        if playerid:
                            info = (item[1] + "\t" + item[0] + "\t" + encounter_name + "\t" + name + "\t" +
                                    p_class + "\t" + dps + "\t" + (str(minute) + ":" + str(second) + "\t" + role)
                                    + "\t" + item[2] + "\t" + encounter_time + "\t" + str(playerid) + "\t" + str(hps)
                                    + "\t" + str(thps) + "\t" + str(aps))
                            print(info)
                            infos += [info]
            if len(dps_names) < 10:
                for healer in roles:
                    if healer[0] not in dps_names:
                        p_class = player_class.get(healer[0], "unknown")
                        info = (item[1] + "\t" + item[0] + "\t" + encounter_name + "\t" + healer[0] + "\t" +
                                p_class + "\t" + "0" + "\t" + (str(minute) + ":" + str(second) + "\t" + healer[1]
                                                               + "\t" + item[2] + "\t" + encounter_time + "\t" + str(
                                            healer[2]) + "\t" + str(healer[3])
                                                               + "\t" + str(healer[4]) + "\t" + str(healer[5])))
                        print(info)
                        infos += [info]

    return infos


def main():
    website = "https://prancingturtle.com/"
    parse_date = "2019-06-10"  # the date from which you want to collect the data
    bossfight = (163, 164, 165)  # Azranel, Commander Isiel, Titan X
    session_id = []
    old_session_id = []
    playerclass = {}
    mydb = mysql_connect_config.database_connect()
    mycursor = mydb.cursor()
    print("Start searching for Session ID's:")
    now = datetime.now()
    date = datetime.strptime(parse_date, '%Y-%m-%d')
    delta = str(now - date)
    delta = delta.split(" day")[0]
    print(delta + " days")
    delta = int(delta) + 1
    month = round(delta / 30)
    for Boss in bossfight:
        session_id += get_session_id(mydb, mycursor, delta, month, session_id, website + "/Session/BossFight/" +
                                     str(Boss) + '?o=1&d=4')
    if session_id:
        session_id.sort()
        print(session_id)
        print("Start searching for Encounter ID's:")
        encounter_id = get_encounter_id(session_id, bossfight, website, parse_date)
        player_class_dps = get_player_class_dps(encounter_id, playerclass, website)
        file = codecs.open("../help_files/dps.tsv", 'w', "utf-8")
        for line in player_class_dps:
            file.write(line + '\r\n')
        file.close()
        print("The file dps.tsv with all new encounters has been created.")
        for sessionid in session_id:
            mysql_add_data.add_database_session(mydb, mycursor, sessionid)
        new_sessions = True
    else:
        print("No new sessions found")
        new_sessions = False
    return new_sessions


if __name__ == "__main__":
    main()
